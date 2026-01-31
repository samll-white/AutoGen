"""
完整对比实验：AutoGen vs 4种基线算法
包括：贪心算法、随机分配、遗传算法、整数规划
"""

import json
import time
from datetime import datetime
from baseline_algorithms import run_baseline_algorithm, TaskAllocationProblem
from evaluation_metrics import AllocationEvaluator
import os
import numpy as np


class AllAlgorithmsComparison:
    """所有算法对比实验管理类"""
    
    def __init__(self):
        self.results = {}
        self.output_dir = "comparison_results"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 算法配置
        self.algorithms = {
            'autogen': {'name': 'AutoGen', 'color': '#2E86AB'},
            'greedy': {'name': '贪心算法', 'color': '#A23B72'},
            'random': {'name': '随机分配', 'color': '#F18F01'},
            'genetic': {'name': '遗传算法', 'color': '#C73E1D'},
            'ip': {'name': '整数规划', 'color': '#6A994E'}
        }
    
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
        print(f"运行 {self.algorithms[algorithm_name]['name']} ({algorithm_name.upper()})")
        print('='*70)
        
        start_time = time.time()
        
        problem = TaskAllocationProblem.from_default_scenario()
        result = run_baseline_algorithm(algorithm_name, problem)
        
        runtime = time.time() - start_time
        
        # 保存结果
        output_file = f'{self.output_dir}/allocation_{algorithm_name}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {self.algorithms[algorithm_name]['name']} 完成")
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
        print(f"\n评估 {self.algorithms[algorithm_name]['name']}...")
        
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
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "AutoGen vs 所有基线算法对比实验" + " " * 21 + "║")
        print("╚" + "═" * 68 + "╝")
        print(f"\n实验时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n对比算法：")
        print("  1. AutoGen - 多智能体协作")
        print("  2. 贪心算法 - 按优先级依次分配")
        print("  3. 随机分配 - 随机选择分配")
        print("  4. 遗传算法 - 进化搜索优化")
        print("  5. 整数规划 - 数学优化求解")
        
        # 1. 加载AutoGen结果
        print(f"\n{'='*70}")
        print("1️⃣ 加载 AutoGen 算法结果")
        print('='*70)
        
        autogen_result = self.load_autogen_result()
        if autogen_result is None:
            print("\n❌ 错误：未找到AutoGen结果")
            print("   请先运行: python autogen_uav_allocation.py")
            return None
        
        self.results['autogen'] = {
            'result': autogen_result,
            'runtime': 0,  # AutoGen的运行时间需要单独记录
            'algorithm': 'autogen'
        }
        print("✅ AutoGen 结果加载成功")
        
        # 2. 运行所有基线算法
        baseline_algos = ['greedy', 'random', 'genetic', 'ip']
        
        for i, algo_name in enumerate(baseline_algos, 2):
            print(f"\n{'='*70}")
            print(f"{i}️⃣ 运行 {self.algorithms[algo_name]['name']}")
            print('='*70)
            self.results[algo_name] = self.run_baseline(algo_name)
        
        # 3. 评估所有算法
        print(f"\n{'='*70}")
        print("📊 评估所有算法")
        print('='*70)
        
        for algo_name in self.algorithms.keys():
            if algo_name in self.results:
                metrics = self.evaluate_result(self.results[algo_name]['result'], algo_name)
                self.results[algo_name]['metrics'] = metrics
        
        # 4. 生成对比报告
        self.generate_comparison_report()
        
        # 5. 保存完整对比结果
        self.save_all_results()
        
        return self.results
    
    def generate_comparison_report(self):
        """生成对比报告"""
        print(f"\n{'='*70}")
        print("📈 对比实验报告")
        print('='*70)
        
        # 创建对比表格
        print(f"\n{'算法':<12} {'总分':<10} {'任务完成':<10} {'时间效率':<10} {'资源利用':<10} {'约束满足':<10}")
        print('-' * 70)
        
        for algo_name in self.algorithms.keys():
            if algo_name in self.results:
                algo_display = self.algorithms[algo_name]['name']
                metrics = self.results[algo_name]['metrics']
                
                print(f"{algo_display:<12} "
                      f"{metrics['overall_score']:<10.2f} "
                      f"{metrics['task_completion']['completion_rate']:<10.1f} "
                      f"{metrics['time_efficiency']['score']*100:<10.1f} "
                      f"{metrics['resource_utilization']['score']*100:<10.1f} "
                      f"{metrics['constraint_satisfaction']['score']*100:<10.1f}")
        
        # 找出最佳算法
        best_algo = max(
            [(name, data['metrics']['overall_score']) 
             for name, data in self.results.items()],
            key=lambda x: x[1]
        )
        
        print(f"\n🏆 最佳算法: {self.algorithms[best_algo[0]]['name']}")
        print(f"   总体评分: {best_algo[1]:.2f}/100")
        
        # 排名
        print("\n📊 算法排名：")
        sorted_algos = sorted(
            [(name, data['metrics']['overall_score']) 
             for name, data in self.results.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        for rank, (algo_name, score) in enumerate(sorted_algos, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            print(f"   {medal} {self.algorithms[algo_name]['name']:<12} - {score:.2f}分")
    
    def save_all_results(self):
        """保存所有对比结果"""
        # 创建完整对比数据
        comparison_data = {
            'experiment_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'algorithms': list(self.results.keys()),
            'algorithm_names': {k: v['name'] for k, v in self.algorithms.items()},
            'results': {},
            'summary': {}
        }
        
        # 收集所有算法的结果
        for algo_name, data in self.results.items():
            metrics = data['metrics']
            comparison_data['results'][algo_name] = {
                'algorithm_name': self.algorithms[algo_name]['name'],
                'overall_score': metrics['overall_score'],
                'task_completion_rate': metrics['task_completion']['completion_rate'],
                'time_efficiency': metrics['time_efficiency']['score'] * 100,
                'resource_utilization': metrics['resource_utilization']['score'] * 100,
                'constraint_satisfaction': metrics['constraint_satisfaction']['score'] * 100,
                'runtime': data['runtime'],
                'completed_tasks': metrics['task_completion']['completed_tasks'],
                'total_tasks': metrics['task_completion']['total_tasks'],
                'detailed_metrics': metrics
            }
        
        # 生成统计摘要
        scores = [data['metrics']['overall_score'] for data in self.results.values()]
        comparison_data['summary'] = {
            'max_score': max(scores),
            'min_score': min(scores),
            'avg_score': np.mean(scores),
            'std_score': np.std(scores),
            'score_range': max(scores) - min(scores)
        }
        
        # 找出最佳算法
        best_algo = max(self.results.items(), 
                       key=lambda x: x[1]['metrics']['overall_score'])
        comparison_data['summary']['best_algorithm'] = {
            'name': self.algorithms[best_algo[0]]['name'],
            'code': best_algo[0],
            'score': best_algo[1]['metrics']['overall_score']
        }
        
        # 保存JSON格式
        output_file = f'{self.output_dir}/all_algorithms_comparison.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 完整对比结果已保存到: {output_file}")
    
    def generate_latex_table(self):
        """生成LaTeX格式的对比表格（用于论文）"""
        latex_code = "\\begin{table}[htbp]\n"
        latex_code += "\\centering\n"
        latex_code += "\\caption{算法性能对比}\n"
        latex_code += "\\begin{tabular}{lcccccc}\n"
        latex_code += "\\hline\n"
        latex_code += "算法 & 总分 & 任务完成率 & 时间效率 & 资源利用 & 约束满足 & 运行时间(秒) \\\\\n"
        latex_code += "\\hline\n"
        
        for algo_name in self.algorithms.keys():
            if algo_name in self.results:
                algo_display = self.algorithms[algo_name]['name']
                metrics = self.results[algo_name]['metrics']
                runtime = self.results[algo_name]['runtime']
                
                latex_code += f"{algo_display} & "
                latex_code += f"{metrics['overall_score']:.2f} & "
                latex_code += f"{metrics['task_completion']['completion_rate']:.1f}\\% & "
                latex_code += f"{metrics['time_efficiency']['score']*100:.1f} & "
                latex_code += f"{metrics['resource_utilization']['score']*100:.1f} & "
                latex_code += f"{metrics['constraint_satisfaction']['score']*100:.1f} & "
                latex_code += f"{runtime:.3f} \\\\\n"
        
        latex_code += "\\hline\n"
        latex_code += "\\end{tabular}\n"
        latex_code += "\\end{table}\n"
        
        # 保存LaTeX代码
        latex_file = f'{self.output_dir}/comparison_table.tex'
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        
        print(f"✅ LaTeX表格已保存到: {latex_file}")
        
        return latex_code


def run_full_comparison():
    """运行完整的对比实验"""
    exp = AllAlgorithmsComparison()
    results = exp.run_all_algorithms()
    
    if results:
        # 生成LaTeX表格
        print(f"\n{'='*70}")
        print("📝 生成论文表格")
        print('='*70)
        exp.generate_latex_table()
        
        print("\n" + "="*70)
        print("✨ 对比实验完成！")
        print("="*70)
        print("\n查看结果:")
        print("  • comparison_results/all_algorithms_comparison.json (完整数据)")
        print("  • comparison_results/comparison_table.tex (LaTeX表格)")
        print("  • comparison_results/allocation_*.json (各算法分配方案)")
        print("  • comparison_results/evaluation_*.json (各算法评估结果)")
        
        return results
    else:
        print("\n❌ 对比实验失败")
        return None


if __name__ == "__main__":
    run_full_comparison()