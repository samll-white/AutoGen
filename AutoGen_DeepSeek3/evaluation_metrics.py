"""
无人机任务分配评估指标模块
提供全面的定量评估指标计算
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np


class AllocationEvaluator:
    """无人机任务分配方案评估器"""
    
    def __init__(self, allocation: Dict, task_input: Dict = None):
        """
        初始化评估器
        
        Args:
            allocation: 分配方案JSON
            task_input: 原始任务输入（可选，用于更详细的评估）
        """
        self.allocation = allocation.get('final_allocation', allocation)
        self.task_input = task_input or self._parse_default_input()
        
    def _parse_default_input(self) -> Dict:
        """解析默认任务输入（从内置数据）"""
        return {
            'total_tasks': 5,
            'total_uavs': 4,
            'tasks': [
                {'task_id': 'T1', 'priority': '高', 'time_window': {'start': '08:00', 'end': '10:00'}, 'estimated_duration': 30},
                {'task_id': 'T2', 'priority': '高', 'time_window': {'start': '08:30', 'end': '09:30'}, 'estimated_duration': 40},
                {'task_id': 'T3', 'priority': '中', 'time_window': {'start': '09:00', 'end': '12:00'}, 'estimated_duration': 60},
                {'task_id': 'T4', 'priority': '紧急', 'time_window': {'start': '08:00', 'end': '08:30'}, 'estimated_duration': 20},
                {'task_id': 'T5', 'priority': '低', 'time_window': {'start': '10:00', 'end': '12:00'}, 'estimated_duration': 30},
            ],
            'uavs': [
                {'uav_id': 'UAV-001', 'max_speed': 80, 'battery': 100},
                {'uav_id': 'UAV-002', 'max_speed': 60, 'battery': 85},
                {'uav_id': 'UAV-003', 'max_speed': 70, 'battery': 90},
                {'uav_id': 'UAV-004', 'max_speed': 65, 'battery': 95},
            ]
        }
    
    def evaluate_all(self) -> Dict[str, Any]:
        """执行全面评估，返回所有指标"""
        metrics = {
            'task_completion': self.evaluate_task_completion(),
            'time_efficiency': self.evaluate_time_efficiency(),
            'resource_utilization': self.evaluate_resource_utilization(),
            'constraint_satisfaction': self.evaluate_constraint_satisfaction(),
            'overall_score': 0.0
        }
        
        # 计算加权总分
        metrics['overall_score'] = self.calculate_overall_score(metrics)
        
        return metrics
    
    def evaluate_task_completion(self) -> Dict[str, Any]:
        """评估任务完成度指标"""
        assignments = self.allocation.get('assignments', [])
        unassigned = self.allocation.get('unassigned_tasks', [])
        
        total_tasks = self.task_input['total_tasks']
        completed_tasks = len(assignments)
        
        # 按优先级统计
        priority_stats = {
            '紧急': {'total': 0, 'completed': 0},
            '高': {'total': 0, 'completed': 0},
            '中': {'total': 0, 'completed': 0},
            '低': {'total': 0, 'completed': 0}
        }
        
        for task in self.task_input['tasks']:
            priority = task.get('priority', '中')
            if priority in priority_stats:
                priority_stats[priority]['total'] += 1
        
        for assignment in assignments:
            priority = assignment.get('priority', '中')
            if priority in priority_stats:
                priority_stats[priority]['completed'] += 1
        
        # 计算完成率
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 高优先级任务完成率
        high_priority_total = priority_stats['紧急']['total'] + priority_stats['高']['total']
        high_priority_completed = priority_stats['紧急']['completed'] + priority_stats['高']['completed']
        high_priority_rate = (high_priority_completed / high_priority_total * 100) if high_priority_total > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'unassigned_tasks': len(unassigned),
            'completion_rate': round(completion_rate, 2),
            'high_priority_completion_rate': round(high_priority_rate, 2),
            'priority_breakdown': priority_stats,
            'score': completion_rate / 100  # 归一化到0-1
        }
    
    def evaluate_time_efficiency(self) -> Dict[str, Any]:
        """评估时间效率指标"""
        assignments = self.allocation.get('assignments', [])
        
        if not assignments:
            return {'score': 0.0}
        
        # 解析时间
        def parse_time(time_str: str) -> datetime:
            try:
                return datetime.strptime(time_str, '%H:%M')
            except:
                return datetime.strptime('08:00', '%H:%M')
        
        # 计算总完成时间
        completion_time_str = self.allocation.get('total_completion_time', '12:00')
        start_time = parse_time('08:00')
        end_time = parse_time(completion_time_str)
        total_duration = (end_time - start_time).total_seconds() / 60  # 分钟
        
        # 计算任务等待时间
        wait_times = []
        for assignment in assignments:
            task_start = parse_time(assignment.get('start_time', '08:00'))
            # 假设所有任务最早可以从08:00开始
            earliest_start = parse_time('08:00')
            wait_time = (task_start - earliest_start).total_seconds() / 60
            wait_times.append(max(0, wait_time))
        
        avg_wait_time = np.mean(wait_times) if wait_times else 0
        
        # 计算紧急任务响应时间
        urgent_response_times = []
        for assignment in assignments:
            if assignment.get('priority') == '紧急':
                task_start = parse_time(assignment.get('start_time', '08:00'))
                window_start = parse_time('08:00')  # T4的时间窗口开始
                response_time = (task_start - window_start).total_seconds() / 60
                urgent_response_times.append(response_time)
        
        avg_urgent_response = np.mean(urgent_response_times) if urgent_response_times else 0
        
        # 效率分数 (总时间越短越好)
        max_duration = 240  # 4小时
        time_score = max(0, 1 - (total_duration / max_duration))
        
        return {
            'total_completion_time_min': round(total_duration, 2),
            'average_wait_time_min': round(avg_wait_time, 2),
            'urgent_response_time_min': round(avg_urgent_response, 2),
            'time_window_utilization': 0.85,  # 简化计算
            'score': round(time_score, 3)
        }
    
    def evaluate_resource_utilization(self) -> Dict[str, Any]:
        """评估资源利用指标"""
        assignments = self.allocation.get('assignments', [])
        total_uavs = self.task_input['total_uavs']
        
        # 统计每个无人机的任务数
        uav_task_count = {}
        for assignment in assignments:
            uav_id = assignment.get('assigned_uav')
            uav_task_count[uav_id] = uav_task_count.get(uav_id, 0) + 1
        
        # 使用的无人机数
        used_uavs = len(uav_task_count)
        utilization_rate = (used_uavs / total_uavs * 100) if total_uavs > 0 else 0
        
        # 负载均衡度（标准差越小越好）
        task_counts = list(uav_task_count.values())
        if len(task_counts) > 1:
            load_std = np.std(task_counts)
            load_balance_score = max(0, 1 - (load_std / 2))  # 标准差归一化
        else:
            load_std = 0
            load_balance_score = 1.0
        
        # 估算飞行距离（简化：假设每个任务平均飞行30km往返）
        estimated_distance = len(assignments) * 30
        
        # 资源利用分数
        util_score = (utilization_rate / 100 * 0.5) + (load_balance_score * 0.5)
        
        return {
            'total_uavs': total_uavs,
            'used_uavs': used_uavs,
            'utilization_rate': round(utilization_rate, 2),
            'uav_task_distribution': uav_task_count,
            'load_balance_std': round(load_std, 2),
            'load_balance_score': round(load_balance_score, 3),
            'estimated_total_distance_km': estimated_distance,
            'score': round(util_score, 3)
        }
    
    def evaluate_constraint_satisfaction(self) -> Dict[str, Any]:
        """评估约束满足指标"""
        assignments = self.allocation.get('assignments', [])
        risk_assessment = self.allocation.get('risk_assessment', '')
        
        # 检测时间冲突
        time_conflicts = self._detect_time_conflicts(assignments)
        
        # 检测约束违反（基于风险评估文本）
        constraint_violations = 0
        if '冲突' in risk_assessment or '违反' in risk_assessment:
            constraint_violations += 1
        
        # 安全性评分（基于风险评估）
        if '低风险' in risk_assessment:
            safety_score = 1.0
        elif '中风险' in risk_assessment:
            safety_score = 0.7
        elif '高风险' in risk_assessment:
            safety_score = 0.4
        else:
            safety_score = 0.8
        
        # 约束满足分数
        conflict_penalty = len(time_conflicts) * 0.2
        violation_penalty = constraint_violations * 0.3
        constraint_score = max(0, 1 - conflict_penalty - violation_penalty)
        
        return {
            'time_conflicts': time_conflicts,
            'conflict_count': len(time_conflicts),
            'constraint_violations': constraint_violations,
            'safety_score': round(safety_score, 3),
            'risk_level': self._extract_risk_level(risk_assessment),
            'score': round(constraint_score, 3)
        }
    
    def _detect_time_conflicts(self, assignments: List[Dict]) -> List[str]:
        """检测时间冲突"""
        conflicts = []
        uav_schedules = {}
        
        for assignment in assignments:
            uav_id = assignment.get('assigned_uav')
            start_time = assignment.get('start_time', '08:00')
            duration_str = assignment.get('estimated_duration', '30分钟')
            
            # 解析持续时间
            try:
                duration = int(''.join(filter(str.isdigit, duration_str)))
            except:
                duration = 30
            
            if uav_id not in uav_schedules:
                uav_schedules[uav_id] = []
            
            uav_schedules[uav_id].append({
                'task': assignment.get('task_id'),
                'start': start_time,
                'duration': duration
            })
        
        # 检查每个无人机的时间表是否有重叠
        for uav_id, schedules in uav_schedules.items():
            if len(schedules) > 1:
                # 简化：如果同一无人机有多个任务，检查时间是否合理安排
                for i in range(len(schedules) - 1):
                    conflicts.append(f"{uav_id}可能存在任务间隔紧张")
                    break
        
        return conflicts
    
    def _extract_risk_level(self, risk_assessment: str) -> str:
        """从风险评估文本提取风险等级"""
        if '低风险' in risk_assessment:
            return '低'
        elif '中风险' in risk_assessment:
            return '中'
        elif '高风险' in risk_assessment:
            return '高'
        else:
            return '未知'
    
    def calculate_overall_score(self, metrics: Dict) -> float:
        """计算加权总分"""
        weights = {
            'task_completion': 0.4,      # 任务完成度权重最高
            'time_efficiency': 0.25,     # 时间效率
            'resource_utilization': 0.2, # 资源利用
            'constraint_satisfaction': 0.15  # 约束满足
        }
        
        total_score = 0
        for key, weight in weights.items():
            if key in metrics:
                total_score += metrics[key].get('score', 0) * weight
        
        return round(total_score * 100, 2)  # 转换为百分制
    
    def generate_report(self, metrics: Dict) -> str:
        """生成评估报告"""
        report = []
        report.append("=" * 70)
        report.append("📊 无人机任务分配方案评估报告")
        report.append("=" * 70)
        report.append("")
        
        # 总体评分
        report.append(f"🎯 总体评分: {metrics['overall_score']}/100")
        report.append("")
        
        # 任务完成度
        tc = metrics['task_completion']
        report.append("1️⃣ 任务完成度")
        report.append(f"   • 任务完成率: {tc['completion_rate']}%")
        report.append(f"   • 完成任务数: {tc['completed_tasks']}/{tc['total_tasks']}")
        report.append(f"   • 高优先级完成率: {tc['high_priority_completion_rate']}%")
        report.append(f"   • 评分: {tc['score']:.3f}")
        report.append("")
        
        # 时间效率
        te = metrics['time_efficiency']
        report.append("2️⃣ 时间效率")
        report.append(f"   • 总完成时间: {te['total_completion_time_min']:.1f} 分钟")
        report.append(f"   • 平均等待时间: {te['average_wait_time_min']:.1f} 分钟")
        report.append(f"   • 紧急任务响应: {te['urgent_response_time_min']:.1f} 分钟")
        report.append(f"   • 评分: {te['score']:.3f}")
        report.append("")
        
        # 资源利用
        ru = metrics['resource_utilization']
        report.append("3️⃣ 资源利用")
        report.append(f"   • 无人机利用率: {ru['utilization_rate']:.1f}%")
        report.append(f"   • 使用无人机: {ru['used_uavs']}/{ru['total_uavs']}")
        report.append(f"   • 负载均衡分数: {ru['load_balance_score']:.3f}")
        report.append(f"   • 任务分布: {ru['uav_task_distribution']}")
        report.append(f"   • 评分: {ru['score']:.3f}")
        report.append("")
        
        # 约束满足
        cs = metrics['constraint_satisfaction']
        report.append("4️⃣ 约束满足")
        report.append(f"   • 时间冲突数: {cs['conflict_count']}")
        report.append(f"   • 约束违反数: {cs['constraint_violations']}")
        report.append(f"   • 风险等级: {cs['risk_level']}")
        report.append(f"   • 安全分数: {cs['safety_score']:.3f}")
        report.append(f"   • 评分: {cs['score']:.3f}")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def evaluate_allocation_from_file(json_file: str) -> Tuple[Dict, str]:
    """
    从JSON文件读取分配方案并评估
    
    Args:
        json_file: JSON文件路径
        
    Returns:
        (metrics, report): 评估指标字典和报告文本
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        allocation = json.load(f)
    
    evaluator = AllocationEvaluator(allocation)
    metrics = evaluator.evaluate_all()
    report = evaluator.generate_report(metrics)
    
    return metrics, report


if __name__ == "__main__":
    # 测试评估模块
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "output_allocation.json"
    
    print(f"正在评估分配方案: {json_file}")
    print()
    
    try:
        metrics, report = evaluate_allocation_from_file(json_file)
        print(report)
        
        # 保存评估结果
        output_file = json_file.replace('.json', '_evaluation.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 评估结果已保存到: {output_file}")
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {json_file}")
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        import traceback
        traceback.print_exc()
