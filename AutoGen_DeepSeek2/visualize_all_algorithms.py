"""
多算法对比可视化模块
生成AutoGen vs 4种基线算法的对比图表
"""

import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


class MultiAlgorithmVisualizer:
    """多算法对比可视化器"""
    
    def __init__(self, comparison_file='comparison_results/all_algorithms_comparison.json'):
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
        
        # 算法配置
        self.algo_config = {
            'autogen': {'name': 'AutoGen', 'color': '#2E86AB', 'marker': 'o'},
            'greedy': {'name': '贪心算法', 'color': '#A23B72', 'marker': 's'},
            'random': {'name': '随机分配', 'color': '#F18F01', 'marker': '^'},
            'genetic': {'name': '遗传算法', 'color': '#C73E1D', 'marker': 'D'},
            'ip': {'name': '整数规划', 'color': '#6A994E', 'marker': 'v'}
        }
        
        # 加载对比数据
        self.load_data()
    
    def load_data(self):
        """加载对比数据"""
        with open(self.comparison_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def plot_overall_comparison(self):
        """绘制总体评分对比条形图"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        algorithms = self.data['algorithms']
        scores = [self.data['results'][algo]['overall_score'] for algo in algorithms]
        names = [self.algo_config[algo]['name'] for algo in algorithms]
        colors = [self.algo_config[algo]['color'] for algo in algorithms]
        
        bars = ax.bar(range(len(algorithms)), scores, color=colors, 
                     edgecolor='black', linewidth=2, alpha=0.8)
        
        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, scores)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{score:.2f}',
                   ha='center', va='bottom', size=13, weight='bold')
        
        ax.set_ylabel('总体评分', size=14, weight='bold')
        ax.set_xlabel('算法', size=14, weight='bold')
        ax.set_title('所有算法总体评分对比', size=16, weight='bold', pad=20)
        ax.set_xticks(range(len(algorithms)))
        ax.set_xticklabels(names, rotation=15, ha='right')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 添加平均线
        avg_score = np.mean(scores)
        ax.axhline(y=avg_score, color='red', linestyle='--', 
                  linewidth=2, alpha=0.7, label=f'平均分: {avg_score:.2f}')
        ax.legend(fontsize=11)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/all_1_overall_scores.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 总体评分对比: {self.output_dir}/all_1_overall_scores.png")
    
    def plot_radar_comparison(self):
        """绘制多算法雷达图对比"""
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
        
        categories = ['任务完成率', '时间效率', '资源利用', '约束满足']
        num_vars = len(categories)
        
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        
        # 绘制每个算法
        for algo in self.data['algorithms']:
            result = self.data['results'][algo]
            values = [
                result['task_completion_rate'],
                result['time_efficiency'],
                result['resource_utilization'],
                result['constraint_satisfaction']
            ]
            values += values[:1]
            
            config = self.algo_config[algo]
            ax.plot(angles, values, config['marker'] + '-', 
                   linewidth=2.5, label=config['name'], 
                   color=config['color'], markersize=8)
            ax.fill(angles, values, alpha=0.15, color=config['color'])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=13)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], size=11)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.title('多算法性能雷达图对比', size=18, weight='bold', pad=30)
        plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=12)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/all_2_radar_chart.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 雷达图对比: {self.output_dir}/all_2_radar_chart.png")
    
    def plot_metrics_heatmap(self):
        """绘制评估指标热力图"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        algorithms = self.data['algorithms']
        metrics = ['任务完成率', '时间效率', '资源利用', '约束满足', '总体评分']
        
        # 构建数据矩阵
        data_matrix = []
        for algo in algorithms:
            result = self.data['results'][algo]
            row = [
                result['task_completion_rate'],
                result['time_efficiency'],
                result['resource_utilization'],
                result['constraint_satisfaction'],
                result['overall_score']
            ]
            data_matrix.append(row)
        
        data_matrix = np.array(data_matrix)
        
        # 绘制热力图
        im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        
        # 设置刻度
        ax.set_xticks(np.arange(len(metrics)))
        ax.set_yticks(np.arange(len(algorithms)))
        ax.set_xticklabels(metrics, size=12)
        ax.set_yticklabels([self.algo_config[a]['name'] for a in algorithms], size=12)
        
        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right", rotation_mode="anchor")
        
        # 添加数值
        for i in range(len(algorithms)):
            for j in range(len(metrics)):
                text = ax.text(j, i, f'{data_matrix[i, j]:.1f}',
                             ha="center", va="center", color="black", 
                             size=11, weight='bold')
        
        ax.set_title('算法性能热力图（数值越高越好）', size=16, weight='bold', pad=20)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('评分', size=12, weight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/all_3_heatmap.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 热力图: {self.output_dir}/all_3_heatmap.png")
    
    def plot_detailed_comparison(self):
        """绘制详细对比柱状图"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        metrics_config = [
            ('task_completion_rate', '任务完成率 (%)'),
            ('time_efficiency', '时间效率'),
            ('resource_utilization', '资源利用'),
            ('constraint_satisfaction', '约束满足')
        ]
        
        for idx, (metric_key, metric_name) in enumerate(metrics_config):
            ax = axes[idx // 2, idx % 2]
            
            algorithms = self.data['algorithms']
            values = [self.data['results'][algo][metric_key] for algo in algorithms]
            names = [self.algo_config[algo]['name'] for algo in algorithms]
            colors = [self.algo_config[algo]['color'] for algo in algorithms]
            
            bars = ax.bar(range(len(algorithms)), values, color=colors, 
                         edgecolor='black', linewidth=1.5, alpha=0.8)
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{value:.1f}',
                       ha='center', va='bottom', size=11, weight='bold')
            
            ax.set_ylabel('评分', size=12, weight='bold')
            ax.set_title(metric_name, size=14, weight='bold')
            ax.set_xticks(range(len(algorithms)))
            ax.set_xticklabels(names, rotation=20, ha='right', size=10)
            ax.set_ylim(0, 105)
            ax.grid(axis='y', alpha=0.3)
        
        plt.suptitle('各维度详细对比', size=18, weight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/all_4_detailed_metrics.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 详细对比图: {self.output_dir}/all_4_detailed_metrics.png")
    
    def plot_ranking_comparison(self):
        """绘制算法排名对比"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # 左图：按总分排序的横向条形图
        algorithms = self.data['algorithms']
        scores = [self.data['results'][algo]['overall_score'] for algo in algorithms]
        
        # 排序
        sorted_pairs = sorted(zip(algorithms, scores), key=lambda x: x[1])
        sorted_algos, sorted_scores = zip(*sorted_pairs)
        
        names = [self.algo_config[algo]['name'] for algo in sorted_algos]
        colors = [self.algo_config[algo]['color'] for algo in sorted_algos]
        
        y_pos = np.arange(len(sorted_algos))
        bars = ax1.barh(y_pos, sorted_scores, color=colors, 
                       edgecolor='black', linewidth=2, alpha=0.8)
        
        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, sorted_scores)):
            width = bar.get_width()
            rank = len(sorted_algos) - i
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
            ax1.text(width + 1, bar.get_y() + bar.get_height()/2.,
                    f'{score:.2f} {medal}',
                    ha='left', va='center', size=13, weight='bold')
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(names, size=12)
        ax1.set_xlabel('总体评分', size=13, weight='bold')
        ax1.set_title('算法排名（按总分）', size=14, weight='bold')
        ax1.set_xlim(0, 100)
        ax1.grid(axis='x', alpha=0.3)
        
        # 右图：运行时间对比
        runtimes = [self.data['results'][algo]['runtime'] for algo in algorithms]
        names_all = [self.algo_config[algo]['name'] for algo in algorithms]
        colors_all = [self.algo_config[algo]['color'] for algo in algorithms]
        
        bars2 = ax2.bar(range(len(algorithms)), runtimes, color=colors_all,
                       edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # 添加数值标签
        for bar, runtime in zip(bars2, runtimes):
            height = bar.get_height()
            if runtime < 1:
                label = f'{runtime*1000:.1f}ms'
            else:
                label = f'{runtime:.2f}s'
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    label,
                    ha='center', va='bottom', size=11, weight='bold')
        
        ax2.set_ylabel('运行时间 (秒)', size=13, weight='bold')
        ax2.set_title('算法运行时间对比', size=14, weight='bold')
        ax2.set_xticks(range(len(algorithms)))
        ax2.set_xticklabels(names_all, rotation=20, ha='right', size=10)
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_yscale('log')  # 使用对数刻度
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/all_5_ranking.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 排名对比图: {self.output_dir}/all_5_ranking.png")
    
    def plot_comprehensive_dashboard(self):
        """绘制综合对比仪表盘"""
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        algorithms = self.data['algorithms']
        
        # 1. 总分对比（占2列）
        ax1 = fig.add_subplot(gs[0, :2])
        scores = [self.data['results'][algo]['overall_score'] for algo in algorithms]
        names = [self.algo_config[algo]['name'] for algo in algorithms]
        colors = [self.algo_config[algo]['color'] for algo in algorithms]
        
        bars = ax1.bar(range(len(algorithms)), scores, color=colors,
                      edgecolor='black', linewidth=2, alpha=0.8)
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}',
                    ha='center', va='bottom', size=12, weight='bold')
        
        ax1.set_xticks(range(len(algorithms)))
        ax1.set_xticklabels(names, rotation=15, ha='right')
        ax1.set_ylabel('总体评分', size=12, weight='bold')
        ax1.set_title('总体评分对比', size=14, weight='bold')
        ax1.set_ylim(0, 100)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. 最佳算法展示（占2列）
        ax2 = fig.add_subplot(gs[0, 2:])
        best = self.data['summary']['best_algorithm']
        ax2.text(0.5, 0.6, '🏆', ha='center', va='center', size=80)
        ax2.text(0.5, 0.3, best['name'], 
                ha='center', va='center', size=24, weight='bold',
                color=self.algo_config[best['code']]['color'])
        ax2.text(0.5, 0.15, f"总分: {best['score']:.2f}", 
                ha='center', va='center', size=18, weight='bold')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('最佳算法', size=14, weight='bold')
        
        # 3-6. 各维度对比（4个子图）
        metrics_config = [
            ('task_completion_rate', '任务完成率'),
            ('time_efficiency', '时间效率'),
            ('resource_utilization', '资源利用'),
            ('constraint_satisfaction', '约束满足')
        ]
        
        for idx, (metric_key, metric_name) in enumerate(metrics_config):
            ax = fig.add_subplot(gs[1, idx])
            values = [self.data['results'][algo][metric_key] for algo in algorithms]
            
            bars = ax.bar(range(len(algorithms)), values, color=colors,
                         edgecolor='black', linewidth=1, alpha=0.8, width=0.6)
            
            ax.set_xticks(range(len(algorithms)))
            ax.set_xticklabels([n[:4] for n in names], size=9)
            ax.set_title(metric_name, size=11, weight='bold')
            ax.set_ylim(0, 105)
            ax.grid(axis='y', alpha=0.3)
        
        # 7. 统计摘要（占2列）
        ax7 = fig.add_subplot(gs[2, :2])
        summary_text = f"""
        统计摘要
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        最高分: {self.data['summary']['max_score']:.2f}
        最低分: {self.data['summary']['min_score']:.2f}
        平均分: {self.data['summary']['avg_score']:.2f}
        标准差: {self.data['summary']['std_score']:.2f}
        分数范围: {self.data['summary']['score_range']:.2f}
        
        参与算法: {len(algorithms)} 个
        """
        ax7.text(0.1, 0.5, summary_text, 
                ha='left', va='center', size=13, 
                family='monospace', weight='bold')
        ax7.set_xlim(0, 1)
        ax7.set_ylim(0, 1)
        ax7.axis('off')
        
        # 8. 算法排名（占2列）
        ax8 = fig.add_subplot(gs[2, 2:])
        sorted_pairs = sorted(
            [(algo, self.data['results'][algo]['overall_score']) 
             for algo in algorithms],
            key=lambda x: x[1],
            reverse=True
        )
        
        ranking_text = "算法排名\n" + "━"*30 + "\n"
        for rank, (algo, score) in enumerate(sorted_pairs, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            ranking_text += f"{medal} {self.algo_config[algo]['name']:<10} {score:>6.2f}分\n"
        
        ax8.text(0.1, 0.5, ranking_text,
                ha='left', va='center', size=13,
                family='monospace', weight='bold')
        ax8.set_xlim(0, 1)
        ax8.set_ylim(0, 1)
        ax8.axis('off')
        
        # 总标题
        fig.suptitle('多算法综合对比仪表盘', size=20, weight='bold', y=0.98)
        
        plt.savefig(f'{self.output_dir}/all_6_dashboard.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 综合仪表盘: {self.output_dir}/all_6_dashboard.png")
    
    def visualize_all(self):
        """生成所有对比图表"""
        print("\n🎨 生成多算法对比可视化图表...")
        
        self.plot_overall_comparison()
        self.plot_radar_comparison()
        self.plot_metrics_heatmap()
        self.plot_detailed_comparison()
        self.plot_ranking_comparison()
        self.plot_comprehensive_dashboard()
        
        print(f"\n✅ 所有图表已保存到: {self.output_dir}/")


if __name__ == "__main__":
    print("=" * 70)
    print("多算法对比可视化")
    print("=" * 70)
    
    try:
        visualizer = MultiAlgorithmVisualizer()
        visualizer.visualize_all()
        
        print("\n" + "="*70)
        print("✨ 可视化完成！")
        print("="*70)
        print("\n生成的图表:")
        print("  1. all_1_overall_scores.png - 总体评分对比 ⭐")
        print("  2. all_2_radar_chart.png - 雷达图对比 ⭐")
        print("  3. all_3_heatmap.png - 性能热力图 ⭐")
        print("  4. all_4_detailed_metrics.png - 各维度详细对比")
        print("  5. all_5_ranking.png - 排名和运行时间")
        print("  6. all_6_dashboard.png - 综合仪表盘 ⭐")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: 未找到对比结果文件")
        print("   请先运行: python comparison_all_algorithms.py")
    except Exception as e:
        print(f"\n❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()
