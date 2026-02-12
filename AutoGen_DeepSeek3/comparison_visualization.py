"""
对比实验可视化模块
生成AutoGen vs 基线算法的对比图表
"""

import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


class ComparisonVisualizer:
    """对比实验可视化器"""
    
    def __init__(self, comparison_file='comparison_results/autogen_vs_greedy_comparison.json'):
        """
        初始化可视化器
        
        Args:
            comparison_file: 对比结果JSON文件路径
        """
        self.comparison_file = comparison_file
        self.output_dir = "comparison_visualizations"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 加载对比数据
        self.load_data()
    
    def load_data(self):
        """加载对比数据"""
        with open(self.comparison_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def plot_overall_comparison(self):
        """绘制总体对比条形图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        algorithms = self.data['algorithms']
        scores = [self.data[algo]['overall_score'] for algo in algorithms]
        
        colors = ['#2E86AB', '#A23B72']
        bars = ax.bar(algorithms, scores, color=colors, edgecolor='black', linewidth=2)
        
        # 添加数值标签
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.2f}',
                   ha='center', va='bottom', size=14, weight='bold')
        
        ax.set_ylabel('总体评分', size=14, weight='bold')
        ax.set_title('AutoGen vs 贪心算法 - 总体评分对比', size=16, weight='bold')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        # 添加标签
        algorithm_labels = ['AutoGen\n(多智能体)', '贪心算法\n(传统方法)']
        ax.set_xticklabels(algorithm_labels)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/1_overall_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 总体对比图: {self.output_dir}/1_overall_comparison.png")
    
    def plot_radar_comparison(self):
        """绘制雷达图对比"""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        categories = ['任务完成率', '时间效率', '资源利用', '约束满足']
        
        # 获取数据
        autogen_scores = [
            self.data['autogen']['task_completion_rate'],
            self.data['autogen']['time_efficiency'],
            self.data['autogen']['resource_utilization'],
            self.data['autogen']['constraint_satisfaction']
        ]
        
        greedy_scores = [
            self.data['greedy']['task_completion_rate'],
            self.data['greedy']['time_efficiency'],
            self.data['greedy']['resource_utilization'],
            self.data['greedy']['constraint_satisfaction']
        ]
        
        # 闭合图形
        autogen_scores += autogen_scores[:1]
        greedy_scores += greedy_scores[:1]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        # 绘制
        ax.plot(angles, autogen_scores, 'o-', linewidth=2, 
               label='AutoGen', color='#2E86AB')
        ax.fill(angles, autogen_scores, alpha=0.25, color='#2E86AB')
        
        ax.plot(angles, greedy_scores, 's-', linewidth=2, 
               label='贪心算法', color='#A23B72')
        ax.fill(angles, greedy_scores, alpha=0.25, color='#A23B72')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=12)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], size=10)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.title('AutoGen vs 贪心算法 - 多维度对比', 
                 size=16, weight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/2_radar_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 雷达对比图: {self.output_dir}/2_radar_comparison.png")
    
    def plot_metrics_comparison(self):
        """绘制各指标详细对比"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        categories = ['任务完成率', '时间效率', '资源利用', '约束满足']
        autogen_scores = [
            self.data['autogen']['task_completion_rate'],
            self.data['autogen']['time_efficiency'],
            self.data['autogen']['resource_utilization'],
            self.data['autogen']['constraint_satisfaction']
        ]
        
        greedy_scores = [
            self.data['greedy']['task_completion_rate'],
            self.data['greedy']['time_efficiency'],
            self.data['greedy']['resource_utilization'],
            self.data['greedy']['constraint_satisfaction']
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, autogen_scores, width, 
                      label='AutoGen', color='#2E86AB', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, greedy_scores, width, 
                      label='贪心算法', color='#A23B72', edgecolor='black', linewidth=1.5)
        
        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', size=11, weight='bold')
        
        ax.set_xlabel('评估维度', size=13, weight='bold')
        ax.set_ylabel('评分', size=13, weight='bold')
        ax.set_title('AutoGen vs 贪心算法 - 各维度详细对比', size=16, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 105)
        ax.legend(fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/3_metrics_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 指标对比图: {self.output_dir}/3_metrics_comparison.png")
    
    def plot_advantage_analysis(self):
        """绘制优势分析图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：评分差异
        categories = ['任务完成率', '时间效率', '资源利用', '约束满足']
        
        differences = [
            self.data['autogen']['task_completion_rate'] - self.data['greedy']['task_completion_rate'],
            self.data['autogen']['time_efficiency'] - self.data['greedy']['time_efficiency'],
            self.data['autogen']['resource_utilization'] - self.data['greedy']['resource_utilization'],
            self.data['autogen']['constraint_satisfaction'] - self.data['greedy']['constraint_satisfaction']
        ]
        
        colors = ['green' if d > 0 else 'red' for d in differences]
        
        bars = ax1.barh(categories, differences, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # 添加数值标签
        for bar, diff in zip(bars, differences):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{diff:+.1f}',
                    ha='left' if diff > 0 else 'right',
                    va='center', size=11, weight='bold')
        
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=2)
        ax1.set_xlabel('评分差异 (AutoGen - 贪心)', size=12, weight='bold')
        ax1.set_title('AutoGen相对优势分析', size=14, weight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # 右图：优劣势总结
        autogen_wins = sum(1 for d in differences if d > 0)
        greedy_wins = len(differences) - autogen_wins
        
        labels = ['AutoGen\n领先', '贪心算法\n领先']
        sizes = [autogen_wins, greedy_wins]
        colors_pie = ['#2E86AB', '#A23B72']
        explode = (0.1, 0) if autogen_wins > greedy_wins else (0, 0.1)
        
        ax2.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
               autopct='%1.0f项', shadow=True, startangle=90,
               textprops={'size': 13, 'weight': 'bold'})
        ax2.set_title('优势维度统计', size=14, weight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/4_advantage_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 优势分析图: {self.output_dir}/4_advantage_analysis.png")
    
    def plot_comprehensive_dashboard(self):
        """绘制综合对比仪表盘"""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. AutoGen总分
        ax1 = fig.add_subplot(gs[0, 0])
        score = self.data['autogen']['overall_score']
        color = '#2E86AB'
        ax1.text(0.5, 0.5, f'{score:.1f}', 
                ha='center', va='center', size=50, weight='bold', color=color)
        ax1.text(0.5, 0.15, 'AutoGen\n总体评分', 
                ha='center', va='center', size=12, weight='bold')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        
        # 2. 贪心算法总分
        ax2 = fig.add_subplot(gs[0, 1])
        score = self.data['greedy']['overall_score']
        color = '#A23B72'
        ax2.text(0.5, 0.5, f'{score:.1f}', 
                ha='center', va='center', size=50, weight='bold', color=color)
        ax2.text(0.5, 0.15, '贪心算法\n总体评分', 
                ha='center', va='center', size=12, weight='bold')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        
        # 3. 评分差异
        ax3 = fig.add_subplot(gs[0, 2])
        diff = self.data['comparison']['score_difference']
        color = 'green' if diff > 0 else 'red'
        ax3.text(0.5, 0.5, f'{diff:+.1f}', 
                ha='center', va='center', size=45, weight='bold', color=color)
        ax3.text(0.5, 0.15, '评分差异\n(AutoGen-贪心)', 
                ha='center', va='center', size=11, weight='bold')
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.axis('off')
        
        # 4. 各维度对比条形图
        ax4 = fig.add_subplot(gs[1, :])
        categories = ['任务完成率', '时间效率', '资源利用', '约束满足']
        autogen_scores = [
            self.data['autogen']['task_completion_rate'],
            self.data['autogen']['time_efficiency'],
            self.data['autogen']['resource_utilization'],
            self.data['autogen']['constraint_satisfaction']
        ]
        greedy_scores = [
            self.data['greedy']['task_completion_rate'],
            self.data['greedy']['time_efficiency'],
            self.data['greedy']['resource_utilization'],
            self.data['greedy']['constraint_satisfaction']
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax4.bar(x - width/2, autogen_scores, width, label='AutoGen', 
               color='#2E86AB', edgecolor='black', linewidth=1.5)
        ax4.bar(x + width/2, greedy_scores, width, label='贪心算法', 
               color='#A23B72', edgecolor='black', linewidth=1.5)
        
        ax4.set_xlabel('评估维度', size=12, weight='bold')
        ax4.set_ylabel('评分', size=12, weight='bold')
        ax4.set_title('各维度详细对比', size=14, weight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(categories)
        ax4.set_ylim(0, 105)
        ax4.legend(fontsize=11)
        ax4.grid(axis='y', alpha=0.3)
        
        # 5. 任务完成统计
        ax5 = fig.add_subplot(gs[2, 0])
        autogen_tasks = self.data['autogen']['metrics']['task_completion']
        labels = ['已完成', '未完成']
        sizes = [autogen_tasks['completed_tasks'], 
                autogen_tasks['total_tasks'] - autogen_tasks['completed_tasks']]
        ax5.pie(sizes, labels=labels, colors=['#2E86AB', '#E5E5E5'],
               autopct='%1.0f', textprops={'size': 10})
        ax5.set_title('AutoGen任务完成', size=12, weight='bold')
        
        # 6. 贪心算法任务完成统计
        ax6 = fig.add_subplot(gs[2, 1])
        greedy_tasks = self.data['greedy']['metrics']['task_completion']
        sizes = [greedy_tasks['completed_tasks'], 
                greedy_tasks['total_tasks'] - greedy_tasks['completed_tasks']]
        ax6.pie(sizes, labels=labels, colors=['#A23B72', '#E5E5E5'],
               autopct='%1.0f', textprops={'size': 10})
        ax6.set_title('贪心算法任务完成', size=12, weight='bold')
        
        # 7. 结论
        ax7 = fig.add_subplot(gs[2, 2])
        winner = self.data['comparison']['winner']
        winner_text = 'AutoGen' if winner == 'autogen' else '贪心算法'
        color = '#2E86AB' if winner == 'autogen' else '#A23B72'
        
        ax7.text(0.5, 0.6, '🏆', 
                ha='center', va='center', size=60)
        ax7.text(0.5, 0.3, winner_text, 
                ha='center', va='center', size=18, weight='bold', color=color)
        ax7.text(0.5, 0.1, '表现最优', 
                ha='center', va='center', size=12)
        ax7.set_xlim(0, 1)
        ax7.set_ylim(0, 1)
        ax7.axis('off')
        
        # 总标题
        fig.suptitle('AutoGen vs 贪心算法 - 综合对比仪表盘', 
                    size=18, weight='bold', y=0.98)
        
        plt.savefig(f'{self.output_dir}/5_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 综合仪表盘: {self.output_dir}/5_comprehensive_dashboard.png")
    
    def visualize_all(self):
        """生成所有对比图表"""
        print("\n🎨 生成对比可视化图表...")
        
        self.plot_overall_comparison()
        self.plot_radar_comparison()
        self.plot_metrics_comparison()
        self.plot_advantage_analysis()
        self.plot_comprehensive_dashboard()
        
        print(f"\n✅ 所有图表已保存到: {self.output_dir}/")


if __name__ == "__main__":
    print("=" * 70)
    print("对比实验可视化")
    print("=" * 70)
    
    try:
        visualizer = ComparisonVisualizer()
        visualizer.visualize_all()
        
        print("\n" + "="*70)
        print("✨ 可视化完成！")
        print("="*70)
        print("\n生成的图表:")
        print("  1. 1_overall_comparison.png - 总体评分对比")
        print("  2. 2_radar_comparison.png - 雷达图对比")
        print("  3. 3_metrics_comparison.png - 各指标详细对比")
        print("  4. 4_advantage_analysis.png - 优势分析")
        print("  5. 5_comprehensive_dashboard.png - 综合仪表盘")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: 未找到对比结果文件")
        print("   请先运行: python comparison_experiments.py")
    except Exception as e:
        print(f"\n❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()
