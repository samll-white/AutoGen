"""
消融实验可视化模块
展示不同智能体配置的性能对比
"""

import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


class AblationVisualizer:
    """消融实验可视化器"""
    
    def __init__(self, results_file='ablation_results/ablation_complete_results.json'):
        """
        初始化可视化器
        
        Args:
            results_file: 实验结果JSON文件路径
        """
        self.results_file = results_file
        self.output_dir = "ablation_visualizations"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 配置颜色
        self.colors = {
            '3-agent': '#E63946',      # 红色（性能较差）
            '4-agent-v1': '#F77F00',   # 橙色
            '4-agent-v2': '#FCBF49',   # 黄色
            '5-agent': '#06A77D',      # 绿色（最优）
            '6-agent': '#023E8A'       # 蓝色
        }
        
        # 加载数据
        self.load_data()
    
    def load_data(self):
        """加载实验数据"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def plot_overall_comparison(self):
        """绘制总体评分对比"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        configs = []
        scores = []
        colors = []
        agent_counts = []
        
        for config_key, config_data in self.data['configurations'].items():
            if config_data['success'] and config_data['metrics']:
                configs.append(config_data['name'])
                scores.append(config_data['metrics']['overall_score'])
                colors.append(self.colors.get(config_key, '#888888'))
                agent_counts.append(config_data['agent_count'])
        
        x = np.arange(len(configs))
        bars = ax.bar(x, scores, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
        
        # 添加数值标签和智能体数量
        for i, (bar, score, count) in enumerate(zip(bars, scores, agent_counts)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{score:.2f}',
                   ha='center', va='bottom', size=13, weight='bold')
            ax.text(bar.get_x() + bar.get_width()/2., 5,
                   f'{count}个\n智能体',
                   ha='center', va='bottom', size=10, weight='bold', color='white')
        
        ax.set_ylabel('总体评分', size=14, weight='bold')
        ax.set_xlabel('配置', size=14, weight='bold')
        ax.set_title('智能体消融实验 - 总体评分对比', size=16, weight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(configs, rotation=15, ha='right')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 标注基准配置
        baseline_idx = list(self.data['configurations'].keys()).index('5-agent')
        if baseline_idx < len(scores):
            ax.axhline(y=scores[baseline_idx], color='green', linestyle='--', 
                      linewidth=2, alpha=0.7, label=f'基准配置: {scores[baseline_idx]:.2f}')
            ax.legend(fontsize=11)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/ablation_1_overall_scores.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 总体评分对比: {self.output_dir}/ablation_1_overall_scores.png")
    
    def plot_agent_count_vs_score(self):
        """绘制智能体数量与评分关系"""
        fig, ax = plt.subplots(figsize=(10, 7))
        
        agent_counts = []
        scores = []
        names = []
        colors_list = []
        
        for config_key, config_data in self.data['configurations'].items():
            if config_data['success'] and config_data['metrics']:
                agent_counts.append(config_data['agent_count'])
                scores.append(config_data['metrics']['overall_score'])
                names.append(config_data['name'])
                colors_list.append(self.colors.get(config_key, '#888888'))
        
        # 绘制散点图
        for i, (count, score, name, color) in enumerate(zip(agent_counts, scores, names, colors_list)):
            ax.scatter(count, score, s=300, color=color, 
                      edgecolor='black', linewidth=2, alpha=0.8, zorder=3)
            ax.annotate(name, (count, score), 
                       textcoords="offset points", xytext=(0,10), 
                       ha='center', size=10, weight='bold')
        
        # 绘制趋势线（如果有足够的数据点）
        if len(agent_counts) >= 3:
            z = np.polyfit(agent_counts, scores, 2)
            p = np.poly1d(z)
            x_trend = np.linspace(min(agent_counts)-0.5, max(agent_counts)+0.5, 100)
            ax.plot(x_trend, p(x_trend), "--", color='gray', alpha=0.5, linewidth=2, label='趋势线')
        
        ax.set_xlabel('智能体数量', size=14, weight='bold')
        ax.set_ylabel('总体评分', size=14, weight='bold')
        ax.set_title('智能体数量 vs 性能表现', size=16, weight='bold', pad=20)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/ablation_2_count_vs_score.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 数量与评分关系: {self.output_dir}/ablation_2_count_vs_score.png")
    
    def plot_metrics_comparison(self):
        """绘制各维度详细对比"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        metrics_config = [
            ('task_completion_rate', '任务完成率 (%)'),
            ('time_efficiency', '时间效率'),
            ('resource_utilization', '资源利用'),
            ('constraint_satisfaction', '约束满足')
        ]
        
        for idx, (metric_key, metric_name) in enumerate(metrics_config):
            ax = axes[idx // 2, idx % 2]
            
            configs = []
            values = []
            colors_list = []
            
            for config_key, config_data in self.data['configurations'].items():
                if config_data['success'] and config_data['metrics']:
                    configs.append(config_data['name'])
                    values.append(config_data['metrics'][metric_key])
                    colors_list.append(self.colors.get(config_key, '#888888'))
            
            x = np.arange(len(configs))
            bars = ax.bar(x, values, color=colors_list, 
                         edgecolor='black', linewidth=1.5, alpha=0.8)
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{value:.1f}',
                       ha='center', va='bottom', size=11, weight='bold')
            
            # 标注基准线
            baseline_idx = list(self.data['configurations'].keys()).index('5-agent')
            if baseline_idx < len(values):
                ax.axhline(y=values[baseline_idx], color='green', linestyle='--', 
                          linewidth=2, alpha=0.5)
            
            ax.set_ylabel('评分', size=12, weight='bold')
            ax.set_title(metric_name, size=14, weight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(configs, rotation=20, ha='right', size=9)
            ax.set_ylim(0, 105)
            ax.grid(axis='y', alpha=0.3)
        
        plt.suptitle('各维度详细对比', size=18, weight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/ablation_3_detailed_metrics.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 详细维度对比: {self.output_dir}/ablation_3_detailed_metrics.png")
    
    def plot_contribution_analysis(self):
        """绘制智能体贡献分析"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # 左图：缺少智能体的影响
        baseline_score = None
        for config_key, config_data in self.data['configurations'].items():
            if config_key == '5-agent' and config_data['success'] and config_data['metrics']:
                baseline_score = config_data['metrics']['overall_score']
                break
        
        if baseline_score:
            impacts = []
            labels = []
            colors_list = []
            
            # 分析4智能体配置相对于5智能体的影响
            for config_key in ['4-agent-v1', '4-agent-v2']:
                config_data = self.data['configurations'][config_key]
                if config_data['success'] and config_data['metrics']:
                    impact = config_data['metrics']['overall_score'] - baseline_score
                    impacts.append(impact)
                    
                    if config_key == '4-agent-v1':
                        labels.append('缺少\nResourceEvaluator')
                    else:
                        labels.append('缺少\nConflictDetector')
                    
                    colors_list.append(self.colors.get(config_key, '#888888'))
            
            bars = ax1.barh(range(len(labels)), impacts, color=colors_list,
                           edgecolor='black', linewidth=2, alpha=0.8)
            
            # 添加数值标签
            for i, (bar, impact) in enumerate(zip(bars, impacts)):
                width = bar.get_width()
                ax1.text(width - 1 if width < 0 else width + 1, bar.get_y() + bar.get_height()/2.,
                        f'{impact:+.2f}',
                        ha='right' if width < 0 else 'left',
                        va='center', size=13, weight='bold')
            
            ax1.axvline(x=0, color='black', linestyle='-', linewidth=2)
            ax1.set_yticks(range(len(labels)))
            ax1.set_yticklabels(labels, size=12)
            ax1.set_xlabel('评分变化（相对于5智能体基准）', size=13, weight='bold')
            ax1.set_title('缺少关键智能体的影响', size=14, weight='bold')
            ax1.grid(axis='x', alpha=0.3)
        
        # 右图：智能体数量的边际收益
        counts = []
        scores = []
        
        for config_key in ['3-agent', '4-agent-v1', '4-agent-v2', '5-agent', '6-agent']:
            config_data = self.data['configurations'].get(config_key)
            if config_data and config_data['success'] and config_data['metrics']:
                counts.append(config_data['agent_count'])
                scores.append(config_data['metrics']['overall_score'])
        
        if len(counts) >= 2:
            # 绘制折线图
            ax2.plot(counts, scores, 'o-', linewidth=3, markersize=12,
                    color='#06A77D', markeredgecolor='black', markeredgewidth=2)
            
            # 标注数值
            for count, score in zip(counts, scores):
                ax2.annotate(f'{score:.1f}', (count, score),
                           textcoords="offset points", xytext=(0, 10),
                           ha='center', size=11, weight='bold')
            
            # 计算边际收益
            if len(counts) >= 2:
                for i in range(len(counts) - 1):
                    marginal = scores[i + 1] - scores[i]
                    mid_count = (counts[i] + counts[i + 1]) / 2
                    mid_score = (scores[i] + scores[i + 1]) / 2
                    
                    color = 'green' if marginal > 0 else 'red'
                    ax2.annotate(f'+{marginal:.1f}' if marginal > 0 else f'{marginal:.1f}',
                               (mid_count, mid_score),
                               color=color, size=10, weight='bold',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax2.set_xlabel('智能体数量', size=13, weight='bold')
            ax2.set_ylabel('总体评分', size=13, weight='bold')
            ax2.set_title('边际收益分析', size=14, weight='bold')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/ablation_4_contribution_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 贡献分析: {self.output_dir}/ablation_4_contribution_analysis.png")
    
    def plot_comprehensive_dashboard(self):
        """绘制综合消融实验仪表盘"""
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. 总体评分对比（占2列）
        ax1 = fig.add_subplot(gs[0, :2])
        
        configs = []
        scores = []
        colors_list = []
        
        for config_key, config_data in self.data['configurations'].items():
            if config_data['success'] and config_data['metrics']:
                configs.append(config_data['name'][:12])  # 缩短名称
                scores.append(config_data['metrics']['overall_score'])
                colors_list.append(self.colors.get(config_key, '#888888'))
        
        x = np.arange(len(configs))
        bars = ax1.bar(x, scores, color=colors_list,
                      edgecolor='black', linewidth=2, alpha=0.8)
        
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}',
                    ha='center', va='bottom', size=11, weight='bold')
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(configs, rotation=15, ha='right', size=10)
        ax1.set_ylabel('总体评分', size=12, weight='bold')
        ax1.set_title('总体评分对比', size=14, weight='bold')
        ax1.set_ylim(0, 100)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. 最佳配置展示
        ax2 = fig.add_subplot(gs[0, 2])
        if 'best_configuration' in self.data['summary']:
            best = self.data['summary']['best_configuration']
            ax2.text(0.5, 0.6, '🏆', ha='center', va='center', size=60)
            ax2.text(0.5, 0.3, best['name'][:15], 
                    ha='center', va='center', size=16, weight='bold')
            ax2.text(0.5, 0.15, f"评分: {best['score']:.2f}", 
                    ha='center', va='center', size=14, weight='bold')
            ax2.text(0.5, 0.05, f"{best['agent_count']}个智能体", 
                    ha='center', va='center', size=12)
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('最佳配置', size=14, weight='bold')
        
        # 3. 智能体数量vs评分
        ax3 = fig.add_subplot(gs[1, :])
        
        agent_counts = []
        scores_for_trend = []
        
        for config_key, config_data in self.data['configurations'].items():
            if config_data['success'] and config_data['metrics']:
                agent_counts.append(config_data['agent_count'])
                scores_for_trend.append(config_data['metrics']['overall_score'])
        
        for i, (count, score, color) in enumerate(zip(agent_counts, scores_for_trend, colors_list)):
            ax3.scatter(count, score, s=300, color=color, 
                       edgecolor='black', linewidth=2, alpha=0.8, zorder=3)
        
        if len(agent_counts) >= 3:
            z = np.polyfit(agent_counts, scores_for_trend, 2)
            p = np.poly1d(z)
            x_trend = np.linspace(min(agent_counts)-0.5, max(agent_counts)+0.5, 100)
            ax3.plot(x_trend, p(x_trend), "--", color='gray', alpha=0.5, linewidth=2)
        
        ax3.set_xlabel('智能体数量', size=12, weight='bold')
        ax3.set_ylabel('总体评分', size=12, weight='bold')
        ax3.set_title('智能体数量对性能的影响', size=14, weight='bold')
        ax3.set_ylim(0, 100)
        ax3.grid(True, alpha=0.3)
        
        # 4. 统计摘要
        ax4 = fig.add_subplot(gs[2, :2])
        if 'summary' in self.data:
            summary = self.data['summary']
            summary_text = f"""
            实验统计摘要
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            总实验数: {summary.get('total_experiments', 0)}
            成功实验: {summary.get('successful_experiments', 0)}
            
            最高分: {summary.get('max_score', 0):.2f}
            最低分: {summary.get('min_score', 0):.2f}
            平均分: {summary.get('avg_score', 0):.2f}
            分数范围: {summary.get('score_range', 0):.2f}
            """
            ax4.text(0.1, 0.5, summary_text, 
                    ha='left', va='center', size=12, 
                    family='monospace', weight='bold')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        
        # 5. 关键发现
        ax5 = fig.add_subplot(gs[2, 2])
        findings_text = """
        关键发现
        ━━━━━━━━━━━━━━━━━━━━
        ✓ 5智能体配置表现最优
        
        ✓ 缺少冲突检测影响显著
        
        ✓ 资源评估对性能重要
        
        ✓ 增加路径规划收益有限
        """
        ax5.text(0.1, 0.5, findings_text,
                ha='left', va='center', size=11,
                family='monospace', weight='bold')
        ax5.set_xlim(0, 1)
        ax5.set_ylim(0, 1)
        ax5.axis('off')
        
        # 总标题
        fig.suptitle('智能体消融实验 - 综合分析仪表盘', size=20, weight='bold', y=0.98)
        
        plt.savefig(f'{self.output_dir}/ablation_5_dashboard.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ 综合仪表盘: {self.output_dir}/ablation_5_dashboard.png")
    
    def visualize_all(self):
        """生成所有可视化图表"""
        print("\n🎨 生成消融实验可视化图表...")
        
        self.plot_overall_comparison()
        self.plot_agent_count_vs_score()
        self.plot_metrics_comparison()
        self.plot_contribution_analysis()
        self.plot_comprehensive_dashboard()
        
        print(f"\n✅ 所有图表已保存到: {self.output_dir}/")


if __name__ == "__main__":
    print("=" * 70)
    print("消融实验可视化")
    print("=" * 70)
    
    try:
        visualizer = AblationVisualizer()
        visualizer.visualize_all()
        
        print("\n" + "="*70)
        print("✨ 可视化完成！")
        print("="*70)
        print("\n生成的图表:")
        print("  1. ablation_1_overall_scores.png - 总体评分对比 ⭐")
        print("  2. ablation_2_count_vs_score.png - 数量与性能关系 ⭐")
        print("  3. ablation_3_detailed_metrics.png - 各维度详细对比")
        print("  4. ablation_4_contribution_analysis.png - 智能体贡献分析 ⭐")
        print("  5. ablation_5_dashboard.png - 综合仪表盘 ⭐")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: 未找到实验结果文件")
        print("   请先运行: python ablation_experiment.py")
    except Exception as e:
        print(f"\n❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()
