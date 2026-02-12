"""
对比实验脚本：AutoGen vs 基线算法
"""

import json
import time
from datetime import datetime
from baseline_algorithms import run_baseline_algorithm, TaskAllocationProblem
from evaluation_metrics import AllocationEvaluator
import os


class ComparisonExperiments:
    """对比实验管理类"""
    
    def __init__(self):
        self.results = {}
        self.output_dir = "comparison_results"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_autogen_result(self, filename='output_allocation.json'):
        """加载AutoGen算法的结果"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 未找到AutoGen结果文件: {filename}")
            print("   请先运行 python autogen_uav_allocation.py 生成结果")
            return None
    
    def run_baseline(self, algorithm_name: str) -> dict:
        """运行基线算法"""
        print(f"\n{'='*70}")
        print(f"运行 {algorithm_name.upper()} 算法")
        print('='*70)
        
        start_time = time.time()
        
        problem = TaskAllocationProblem.from_default_scenario()
        result = run_baseline_algorithm(algorithm_name, problem)
        
        runtime = time.time() - start_time
        
        # 保存结果
        output_file = f'{self.output_dir}/allocation_{algorithm_name}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {algorithm_name.upper()} 完成")
        print(f"   运行时间: {runtime:.3f} 秒")
        print(f"   完成任务: {len(result['final_allocation']['assignments'])}/{result['final_allocation']['total_tasks']}")
        print(f"   保存到: {output_file}")
        
        return {
            'result': result,
            'runtime': runtime,
            'algorithm': algorithm_name
        }
    
    def evaluate_result(self, result: dict, algorithm_name: str) -> dict:
        """评估单个算法的结果"""
        print(f"\n评估 {algorithm_name.upper()} 算法...")
        
        evaluator = AllocationEvaluator(result)
        metrics = evaluator.evaluate_all()
        
        # 保存评估结果
        eval_file = f'{self.output_dir}/evaluation_{algorithm_name}.json'
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        
        print(f"   总体评分: {metrics['overall_score']:.2f}/100")
        
        return metrics
    
    def run_all_algorithms(self):
        """运行所有算法并评估"""
        print("=" * 70)
        print("AutoGen vs 基线算法对比实验")
        print("=" * 70)
        print(f"\n实验时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        algorithms = {
            'autogen': None,  # 从文件加载
            'greedy': self.run_baseline,
            'random': self.run_baseline,
            'genetic': self.run_baseline,
            'ip': self.run_baseline,
        }
        
        # 1. 运行所有算法
        for algo_name, run_func in algorithms.items():
            if algo_name == 'autogen':
                print(f"\n{'='*70}")
                print("加载 AUTOGEN 算法结果")
                print('='*70)
                
                result = self.load_autogen_result()
                if result is None:
                    print("⚠️ 跳过AutoGen算法（结果文件不存在）")
                    continue
                
                self.results[algo_name] = {
                    'result': result,
                    'runtime': 0,  # AutoGen的运行时间需要单独记录
                    'algorithm': algo_name
                }
                print("✅ AutoGen 结果加载成功")
            else:
                self.results[algo_name] = run_func(algo_name)
        
        # 2. 评估所有算法
        print(f"\n{'='*70}")
        print("评估所有算法")
        print('='*70)
        
        for algo_name, data in self.results.items():
            metrics = self.evaluate_result(data['result'], algo_name)
            self.results[algo_name]['metrics'] = metrics
        
        # 3. 生成对比报告
        self.generate_comparison_report()
        
        return self.results
    
    def generate_comparison_report(self):
        """生成对比报告"""
        print(f"\n{'='*70}")
        print("对比实验报告")
        print('='*70)
        
        # 创建对比表格
        print(f"\n{'算法':<15} {'总分':<10} {'任务完成率':<12} {'时间效率':<12} {'资源利用':<12} {'约束满足':<12}")
        print('-' * 90)
        
        for algo_name, data in self.results.items():
            metrics = data['metrics']
            print(f"{algo_name.upper():<15} "
                  f"{metrics['overall_score']:<10.2f} "
                  f"{metrics['task_completion']['completion_rate']:<12.1f} "
                  f"{metrics['time_efficiency']['score']*100:<12.1f} "
                  f"{metrics['resource_utilization']['score']*100:<12.1f} "
                  f"{metrics['constraint_satisfaction']['score']*100:<12.1f}")
        
        # 保存完整对比结果
        comparison_data = {
            'experiment_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'algorithms': list(self.results.keys()),
            'results': {}
        }
        
        for algo_name, data in self.results.items():
            comparison_data['results'][algo_name] = {
                'overall_score': data['metrics']['overall_score'],
                'task_completion_rate': data['metrics']['task_completion']['completion_rate'],
                'time_efficiency': data['metrics']['time_efficiency']['score'],
                'resource_utilization': data['metrics']['resource_utilization']['score'],
                'constraint_satisfaction': data['metrics']['constraint_satisfaction']['score'],
                'runtime': data['runtime'],
                'completed_tasks': data['metrics']['task_completion']['completed_tasks'],
                'total_tasks': data['metrics']['task_completion']['total_tasks'],
            }
        
        # 保存JSON格式
        report_file = f'{self.output_dir}/comparison_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 对比报告已保存到: {report_file}")
        
        # 找出最佳算法
        best_algo = max(self.results.items(), 
                       key=lambda x: x[1]['metrics']['overall_score'])
        
        print(f"\n🏆 最佳算法: {best_algo[0].upper()}")
        print(f"   总体评分: {best_algo[1]['metrics']['overall_score']:.2f}/100")


def run_autogen_vs_greedy():
    """运行AutoGen vs 贪心算法的对比实验"""
    print("=" * 70)
    print("AutoGen vs 贪心算法对比实验")
    print("=" * 70)
    
    exp = ComparisonExperiments()
    
    # 1. 加载AutoGen结果
    print("\n1️⃣ 加载AutoGen算法结果...")
    autogen_result = exp.load_autogen_result()
    
    if autogen_result is None:
        print("\n❌ 错误：未找到AutoGen结果")
        print("   请先运行: python autogen_uav_allocation.py")
        return
    
    # 2. 运行贪心算法
    print("\n2️⃣ 运行贪心算法...")
    greedy_data = exp.run_baseline('greedy')
    
    # 3. 评估两种算法
    print(f"\n{'='*70}")
    print("3️⃣ 评估算法性能")
    print('='*70)
    
    autogen_metrics = exp.evaluate_result(autogen_result, 'autogen')
    greedy_metrics = exp.evaluate_result(greedy_data['result'], 'greedy')
    
    # 4. 生成对比报告
    print(f"\n{'='*70}")
    print("4️⃣ 对比结果")
    print('='*70)
    
    print(f"\n{'指标':<25} {'AutoGen':<15} {'贪心算法':<15} {'差异':<15}")
    print('-' * 70)
    
    # 总体评分
    diff = autogen_metrics['overall_score'] - greedy_metrics['overall_score']
    print(f"{'总体评分':<25} "
          f"{autogen_metrics['overall_score']:<15.2f} "
          f"{greedy_metrics['overall_score']:<15.2f} "
          f"{diff:+.2f}")
    
    # 任务完成率
    ac_rate = autogen_metrics['task_completion']['completion_rate']
    gc_rate = greedy_metrics['task_completion']['completion_rate']
    diff = ac_rate - gc_rate
    print(f"{'任务完成率 (%)':<25} "
          f"{ac_rate:<15.1f} "
          f"{gc_rate:<15.1f} "
          f"{diff:+.1f}")
    
    # 时间效率
    at_eff = autogen_metrics['time_efficiency']['score'] * 100
    gt_eff = greedy_metrics['time_efficiency']['score'] * 100
    diff = at_eff - gt_eff
    print(f"{'时间效率':<25} "
          f"{at_eff:<15.1f} "
          f"{gt_eff:<15.1f} "
          f"{diff:+.1f}")
    
    # 资源利用
    ar_util = autogen_metrics['resource_utilization']['score'] * 100
    gr_util = greedy_metrics['resource_utilization']['score'] * 100
    diff = ar_util - gr_util
    print(f"{'资源利用':<25} "
          f"{ar_util:<15.1f} "
          f"{gr_util:<15.1f} "
          f"{diff:+.1f}")
    
    # 约束满足
    ac_sat = autogen_metrics['constraint_satisfaction']['score'] * 100
    gc_sat = greedy_metrics['constraint_satisfaction']['score'] * 100
    diff = ac_sat - gc_sat
    print(f"{'约束满足':<25} "
          f"{ac_sat:<15.1f} "
          f"{gc_sat:<15.1f} "
          f"{diff:+.1f}")
    
    # 保存对比结果
    comparison_result = {
        'experiment_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'algorithms': ['autogen', 'greedy'],
        'autogen': {
            'overall_score': autogen_metrics['overall_score'],
            'task_completion_rate': ac_rate,
            'time_efficiency': at_eff,
            'resource_utilization': ar_util,
            'constraint_satisfaction': ac_sat,
            'metrics': autogen_metrics
        },
        'greedy': {
            'overall_score': greedy_metrics['overall_score'],
            'task_completion_rate': gc_rate,
            'time_efficiency': gt_eff,
            'resource_utilization': gr_util,
            'constraint_satisfaction': gc_sat,
            'runtime': greedy_data['runtime'],
            'metrics': greedy_metrics
        },
        'comparison': {
            'score_difference': autogen_metrics['overall_score'] - greedy_metrics['overall_score'],
            'winner': 'autogen' if autogen_metrics['overall_score'] > greedy_metrics['overall_score'] else 'greedy'
        }
    }
    
    # 保存结果
    output_file = f'{exp.output_dir}/autogen_vs_greedy_comparison.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 对比结果已保存到: {output_file}")
    
    # 结论
    print(f"\n{'='*70}")
    print("📊 结论")
    print('='*70)
    
    winner = comparison_result['comparison']['winner']
    score_diff = abs(comparison_result['comparison']['score_difference'])
    
    if winner == 'autogen':
        print(f"🏆 AutoGen算法表现更优，领先 {score_diff:.2f} 分")
    else:
        print(f"⚠️ 贪心算法表现更优，领先 {score_diff:.2f} 分")
    
    return comparison_result


if __name__ == "__main__":
    # 运行AutoGen vs 贪心算法对比
    result = run_autogen_vs_greedy()
    
    print("\n" + "="*70)
    print("✨ 对比实验完成！")
    print("="*70)
    print("\n查看结果:")
    print("  • comparison_results/autogen_vs_greedy_comparison.json")
    print("  • comparison_results/allocation_greedy.json")
    print("  • comparison_results/evaluation_autogen.json")
    print("  • comparison_results/evaluation_greedy.json")
