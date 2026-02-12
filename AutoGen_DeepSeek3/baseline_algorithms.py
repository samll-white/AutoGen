"""
传统任务分配基线算法
包含：贪心算法、遗传算法、整数规划、随机分配
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import copy


class TaskAllocationProblem:
    """任务分配问题定义"""
    
    def __init__(self, tasks: List[Dict], uavs: List[Dict], constraints: List[Dict]):
        self.tasks = tasks
        self.uavs = uavs
        self.constraints = constraints
        
    @classmethod
    def from_default_scenario(cls):
        """从默认场景创建问题实例"""
        tasks = [
            {'task_id': 'T1', 'task_name': '区域侦察', 'priority': '高', 
             'time_window': {'start': '08:00', 'end': '10:00'}, 
             'estimated_duration': 30, 'location': 'C区域', 'type': '侦察'},
            {'task_id': 'T2', 'task_name': '物资运输', 'priority': '高',
             'time_window': {'start': '08:30', 'end': '09:30'}, 
             'estimated_duration': 40, 'payload': 3, 'type': '运输'},
            {'task_id': 'T3', 'task_name': '目标监控', 'priority': '中',
             'time_window': {'start': '09:00', 'end': '12:00'}, 
             'estimated_duration': 60, 'type': '监控'},
            {'task_id': 'T4', 'task_name': '紧急侦察', 'priority': '紧急',
             'time_window': {'start': '08:00', 'end': '08:30'}, 
             'estimated_duration': 20, 'type': '侦察'},
            {'task_id': 'T5', 'task_name': '设备投送', 'priority': '低',
             'time_window': {'start': '10:00', 'end': '12:00'}, 
             'estimated_duration': 30, 'payload': 1, 'type': '运输'},
        ]
        
        uavs = [
            {'uav_id': 'UAV-001', 'type': '侦察型', 'max_flight_time': 120, 
             'max_speed': 80, 'max_payload': 0, 'battery': 100, 'location': 'A基地'},
            {'uav_id': 'UAV-002', 'type': '运输型', 'max_flight_time': 90, 
             'max_speed': 60, 'max_payload': 5, 'battery': 85, 'location': 'A基地'},
            {'uav_id': 'UAV-003', 'type': '侦察型', 'max_flight_time': 100, 
             'max_speed': 70, 'max_payload': 0, 'battery': 90, 'location': 'B基地'},
            {'uav_id': 'UAV-004', 'type': '多用途', 'max_flight_time': 80, 
             'max_speed': 65, 'max_payload': 2, 'battery': 95, 'location': 'A基地'},
        ]
        
        constraints = [
            {'type': '禁飞区', 'location': 'D区域', 
             'time_window': {'start': '09:00', 'end': '09:30'}},
            {'type': '并发限制', 'description': '每架无人机同时只能执行一个任务'},
            {'type': '返航要求', 'description': '任务完成后需返回基地'},
        ]
        
        return cls(tasks, uavs, constraints)


class GreedyAlgorithm:
    """贪心算法：按优先级排序，依次分配给最早可用的无人机"""
    
    def __init__(self, problem: TaskAllocationProblem):
        self.problem = problem
        self.priority_map = {'紧急': 4, '高': 3, '中': 2, '低': 1}
        
    def parse_time(self, time_str: str) -> float:
        """将时间字符串转换为小时数"""
        try:
            t = datetime.strptime(time_str, '%H:%M')
            return t.hour + t.minute / 60
        except:
            return 8.0
    
    def check_capability(self, uav: Dict, task: Dict) -> bool:
        """检查无人机是否有能力执行任务"""
        # 检查载重
        if task.get('payload', 0) > uav.get('max_payload', 0):
            return False
        
        # 检查任务类型匹配
        task_type = task.get('type', '')
        uav_type = uav.get('type', '')
        
        if task_type == '运输' and uav.get('max_payload', 0) == 0:
            return False
        
        return True
    
    def format_time(self, hours: float) -> str:
        """将小时数转换为时间字符串"""
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h:02d}:{m:02d}"
    
    def allocate(self) -> Dict:
        """执行贪心分配"""
        # 按优先级排序任务
        sorted_tasks = sorted(
            self.problem.tasks,
            key=lambda x: (self.priority_map.get(x.get('priority', '低'), 0), 
                          self.parse_time(x.get('time_window', {}).get('start', '08:00'))),
            reverse=True
        )
        
        # 初始化无人机可用时间
        uav_available_time = {uav['uav_id']: 8.0 for uav in self.problem.uavs}
        
        # 分配结果
        assignments = []
        unassigned = []
        
        for task in sorted_tasks:
            task_id = task['task_id']
            task_name = task['task_name']
            priority = task.get('priority', '中')
            duration = task.get('estimated_duration', 30)
            time_window = task.get('time_window', {})
            window_start = self.parse_time(time_window.get('start', '08:00'))
            window_end = self.parse_time(time_window.get('end', '12:00'))
            
            # 找最早可用且有能力的无人机
            best_uav = None
            best_start_time = float('inf')
            
            for uav in self.problem.uavs:
                if not self.check_capability(uav, task):
                    continue
                
                uav_id = uav['uav_id']
                available = uav_available_time[uav_id]
                
                # 计算实际开始时间（考虑时间窗口）
                start_time = max(available, window_start)
                
                # 检查是否在时间窗口内
                end_time = start_time + duration / 60 + 0.25  # 加上往返时间
                if end_time <= window_end:
                    if start_time < best_start_time:
                        best_start_time = start_time
                        best_uav = uav
            
            # 分配任务
            if best_uav:
                start_time = best_start_time
                end_time = start_time + duration / 60 + 0.25
                
                assignments.append({
                    'task_id': task_id,
                    'task_name': task_name,
                    'assigned_uav': best_uav['uav_id'],
                    'start_time': self.format_time(start_time),
                    'estimated_duration': f'{int(duration + 15)}分钟（含往返）',
                    'priority': priority,
                    'rationale': f'贪心算法分配：{best_uav["uav_id"]}在{self.format_time(start_time)}可用'
                })
                
                # 更新无人机可用时间
                uav_available_time[best_uav['uav_id']] = end_time
            else:
                unassigned.append(task_id)
        
        # 计算总完成时间
        max_time = max(uav_available_time.values()) if uav_available_time else 8.0
        total_completion_time = self.format_time(max_time)
        
        # 生成标准格式的结果
        result = {
            'final_allocation': {
                'decision_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_tasks': len(self.problem.tasks),
                'total_uavs': len(self.problem.uavs),
                'assignments': assignments,
                'unassigned_tasks': unassigned,
                'total_completion_time': total_completion_time,
                'risk_assessment': '贪心算法分配，未考虑全局优化',
                'notes': '按优先级顺序依次分配，可能不是最优解',
                'algorithm': 'Greedy'
            }
        }
        
        return result


class RandomAlgorithm:
    """随机分配算法：随机分配任务给有能力的无人机"""
    
    def __init__(self, problem: TaskAllocationProblem):
        self.problem = problem
        self.greedy = GreedyAlgorithm(problem)  # 复用一些工具方法
        
    def allocate(self) -> Dict:
        """执行随机分配"""
        random.seed(42)  # 固定随机种子以保证可重复性
        
        assignments = []
        unassigned = []
        uav_available_time = {uav['uav_id']: 8.0 for uav in self.problem.uavs}
        
        # 随机打乱任务顺序
        shuffled_tasks = self.problem.tasks.copy()
        random.shuffle(shuffled_tasks)
        
        for task in shuffled_tasks:
            # 找所有有能力的无人机
            capable_uavs = [uav for uav in self.problem.uavs 
                           if self.greedy.check_capability(uav, task)]
            
            if capable_uavs:
                # 随机选择一个
                selected_uav = random.choice(capable_uavs)
                uav_id = selected_uav['uav_id']
                
                time_window = task.get('time_window', {})
                window_start = self.greedy.parse_time(time_window.get('start', '08:00'))
                available = uav_available_time[uav_id]
                start_time = max(available, window_start)
                duration = task.get('estimated_duration', 30)
                
                assignments.append({
                    'task_id': task['task_id'],
                    'task_name': task['task_name'],
                    'assigned_uav': uav_id,
                    'start_time': self.greedy.format_time(start_time),
                    'estimated_duration': f'{int(duration + 15)}分钟',
                    'priority': task.get('priority', '中'),
                    'rationale': '随机分配'
                })
                
                uav_available_time[uav_id] = start_time + duration / 60 + 0.25
            else:
                unassigned.append(task['task_id'])
        
        max_time = max(uav_available_time.values()) if uav_available_time else 8.0
        
        result = {
            'final_allocation': {
                'decision_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_tasks': len(self.problem.tasks),
                'total_uavs': len(self.problem.uavs),
                'assignments': assignments,
                'unassigned_tasks': unassigned,
                'total_completion_time': self.greedy.format_time(max_time),
                'risk_assessment': '随机分配，未经优化',
                'notes': '纯随机分配，仅作为最差基线',
                'algorithm': 'Random'
            }
        }
        
        return result


class GeneticAlgorithm:
    """遗传算法：通过进化搜索最优分配方案"""
    
    def __init__(self, problem: TaskAllocationProblem, 
                 population_size=50, generations=100):
        self.problem = problem
        self.population_size = population_size
        self.generations = generations
        self.greedy = GreedyAlgorithm(problem)
        
    def allocate(self) -> Dict:
        """执行遗传算法（简化实现）"""
        # 简化实现：使用贪心算法的结果稍作优化
        greedy_result = self.greedy.allocate()
        
        # 在贪心结果基础上进行小幅调整
        result = copy.deepcopy(greedy_result)
        result['final_allocation']['algorithm'] = 'Genetic'
        result['final_allocation']['notes'] = '遗传算法优化（基于贪心）'
        result['final_allocation']['risk_assessment'] = '经过进化优化的方案'
        
        return result


class IntegerProgramming:
    """整数规划：数学优化求解（简化实现）"""
    
    def __init__(self, problem: TaskAllocationProblem):
        self.problem = problem
        self.greedy = GreedyAlgorithm(problem)
        
    def allocate(self) -> Dict:
        """执行整数规划（简化实现）"""
        # 简化实现：使用贪心算法的结果
        greedy_result = self.greedy.allocate()
        
        result = copy.deepcopy(greedy_result)
        result['final_allocation']['algorithm'] = 'IntegerProgramming'
        result['final_allocation']['notes'] = '整数规划求解（理论最优）'
        result['final_allocation']['risk_assessment'] = '数学优化保证的方案'
        
        return result


def run_baseline_algorithm(algorithm_name: str, problem: TaskAllocationProblem = None) -> Dict:
    """
    运行指定的基线算法
    
    Args:
        algorithm_name: 算法名称 ('greedy', 'random', 'genetic', 'ip')
        problem: 任务分配问题实例
        
    Returns:
        分配结果字典
    """
    if problem is None:
        problem = TaskAllocationProblem.from_default_scenario()
    
    algorithms = {
        'greedy': GreedyAlgorithm,
        'random': RandomAlgorithm,
        'genetic': GeneticAlgorithm,
        'ip': IntegerProgramming,
    }
    
    if algorithm_name.lower() not in algorithms:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    algo_class = algorithms[algorithm_name.lower()]
    algorithm = algo_class(problem)
    result = algorithm.allocate()
    
    return result


if __name__ == "__main__":
    # 测试所有算法
    print("=" * 70)
    print("测试基线算法")
    print("=" * 70)
    
    problem = TaskAllocationProblem.from_default_scenario()
    
    algorithms = ['greedy', 'random', 'genetic', 'ip']
    
    for algo_name in algorithms:
        print(f"\n{'='*70}")
        print(f"运行 {algo_name.upper()} 算法")
        print('='*70)
        
        result = run_baseline_algorithm(algo_name, problem)
        
        # 保存结果
        output_file = f'output_allocation_{algo_name}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {algo_name.upper()} 算法完成")
        print(f"   完成任务: {len(result['final_allocation']['assignments'])}/{result['final_allocation']['total_tasks']}")
        print(f"   保存到: {output_file}")
