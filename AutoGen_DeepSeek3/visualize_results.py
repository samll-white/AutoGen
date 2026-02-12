"""
无人机任务分配可视化模块
生成评估指标的可视化图表
"""

import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


class AllocationVisualizer:
    """分配方案可视化器"""
    
    def __init__(self, allocation: Dict, metrics: Dict):
        """
        初始化可视化器
        
        Args:
            allocation: 分配方案JSON
            metrics: 评估指标
        """
        self.allocation = allocation.get('final_allocation', allocation)
        self.metrics = metrics
        self.output_dir = "visualization_outputs"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def visualize_all(self, save_combined=True):
        """生成所有可视化图表"""
        print("🎨 正在生成可视化图表...")
        
        # 1. 总体评分雷达图
        self.plot_radar_chart()
        print("   ✓ 雷达图已生成")
        
        # 2. 任务完成度条形图
        self.plot_task_completion()
        print("   ✓ 任务完成度图已生成")
        
        # 3. 资源利用情况
        self.plot_resource_utilization()
        print("   ✓ 资源利用图已生成")
        
        # 4. 时间甘特图
        self.plot_gantt_chart()
        print("   ✓ 甘特图已生成")
        
        # 5. 综合仪表盘
        if save_combined:
            self.plot_dashboard()
            print("   ✓ 综合仪表盘已生成")
        
        print(f"\n✅ 所有图表已保存到目录: {self.output_dir}/")
    
    def plot_radar_chart(self):
        """绘制评估指标雷达图"""
        categories = ['任务完成度', '时间效率', '资源利用', '约束满足']
        scores = [
            self.metrics['task_completion']['score'],
            self.metrics['time_efficiency']['score'],
            self.metrics['resource_utilization']['score'],
            self.metrics['constraint_satisfaction']['score']
        ]
        
        # 转换为百分制
        scores = [s * 100 for s in scores]
        
        # 设置雷达图
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        scores += scores[:1]  # 闭合
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, scores, 'o-', linewidth=2, label='当前方案', color='#2E86AB')
        ax.fill(angles, scores, alpha=0.25, color='#2E86AB')
        
        # 添加参考线（理想值100分）
        ideal_scores = [100] * (len(categories) + 1)
        ax.plot(angles, ideal_scores, '--', linewidth=1, label='理想值', color='#A23B72', alpha=0.5)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=12)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], size=10)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.title(f'评估指标雷达图\n总分: {self.metrics["overall_score"]}/100', 
                  size=16, weight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/1_radar_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_task_completion(self):
        """绘制任务完成度分析图"""
        tc = self.metrics['task_completion']
        priority_breakdown = tc['priority_breakdown']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：优先级任务完成情况
        priorities = list(priority_breakdown.keys())
        total_counts = [priority_breakdown[p]['total'] for p in priorities]
        completed_counts = [priority_breakdown[p]['completed'] for p in priorities]
        
        x = np.arange(len(priorities))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, total_counts, width, label='总任务数', 
                       color='#A8DADC', edgecolor='black')
        bars2 = ax1.bar(x + width/2, completed_counts, width, label='已完成', 
                       color='#457B9D', edgecolor='black')
        
        ax1.set_xlabel('优先级', size=12, weight='bold')
        ax1.set_ylabel('任务数量', size=12, weight='bold')
        ax1.set_title('各优先级任务完成情况', size=14, weight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(priorities)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', size=10)
        
        # 右图：完成率饼图
        labels = ['已完成', '未完成']
        sizes = [tc['completed_tasks'], tc['total_tasks'] - tc['completed_tasks']]
        colors = ['#2A9D8F', '#E76F51']
        explode = (0.1, 0)
        
        ax2.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90,
               textprops={'size': 12, 'weight': 'bold'})
        ax2.set_title(f'总体完成率: {tc["completion_rate"]:.1f}%', 
                     size=14, weight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/2_task_completion.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_resource_utilization(self):
        """绘制资源利用情况"""
        ru = self.metrics['resource_utilization']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：无人机任务分配
        uav_distribution = ru['uav_task_distribution']
        uavs = list(uav_distribution.keys())
        task_counts = list(uav_distribution.values())
        
        colors_palette = ['#E63946', '#F1FAEE', '#A8DADC', '#457B9D']
        bars = ax1.bar(uavs, task_counts, color=colors_palette[:len(uavs)], 
                      edgecolor='black', linewidth=1.5)
        
        ax1.set_xlabel('无人机ID', size=12, weight='bold')
        ax1.set_ylabel('分配任务数', size=12, weight='bold')
        ax1.set_title('无人机任务分配情况', size=14, weight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}个任务',
                    ha='center', va='bottom', size=10, weight='bold')
        
        # 添加平均线
        avg_tasks = np.mean(task_counts)
        ax1.axhline(y=avg_tasks, color='red', linestyle='--', 
                   label=f'平均值: {avg_tasks:.1f}', linewidth=2)
        ax1.legend()
        
        # 右图：资源利用率指标
        metrics_names = ['无人机利用率', '负载均衡分数']
        metrics_values = [
            ru['utilization_rate'],
            ru['load_balance_score'] * 100
        ]
        
        bars = ax2.barh(metrics_names, metrics_values, 
                       color=['#2A9D8F', '#F4A261'], 
                       edgecolor='black', linewidth=1.5)
        
        ax2.set_xlabel('评分 (%)', size=12, weight='bold')
        ax2.set_title('资源利用效率指标', size=14, weight='bold')
        ax2.set_xlim(0, 100)
        ax2.grid(axis='x', alpha=0.3)
        
        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, metrics_values)):
            ax2.text(value + 2, bar.get_y() + bar.get_height()/2.,
                    f'{value:.1f}%',
                    ha='left', va='center', size=11, weight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/3_resource_utilization.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_gantt_chart(self):
        """绘制任务时间甘特图"""
        assignments = self.allocation.get('assignments', [])
        
        if not assignments:
            print("   ⚠️ 无任务分配，跳过甘特图生成")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 颜色映射
        priority_colors = {
            '紧急': '#E63946',
            '高': '#F4A261',
            '中': '#2A9D8F',
            '低': '#A8DADC'
        }
        
        # 解析时间
        def parse_time(time_str: str) -> float:
            try:
                t = datetime.strptime(time_str, '%H:%M')
                return t.hour + t.minute / 60
            except:
                return 8.0
        
        # 按无人机分组
        uav_tasks = {}
        for assignment in assignments:
            uav = assignment.get('assigned_uav', 'Unknown')
            if uav not in uav_tasks:
                uav_tasks[uav] = []
            
            start_time = parse_time(assignment.get('start_time', '08:00'))
            duration_str = assignment.get('estimated_duration', '30分钟')
            
            try:
                duration = int(''.join(filter(str.isdigit, duration_str))) / 60
            except:
                duration = 0.5
            
            uav_tasks[uav].append({
                'task_id': assignment.get('task_id', ''),
                'task_name': assignment.get('task_name', ''),
                'start': start_time,
                'duration': duration,
                'priority': assignment.get('priority', '中')
            })
        
        # 绘制甘特图
        y_pos = 0
        y_ticks = []
        y_labels = []
        
        for uav, tasks in sorted(uav_tasks.items()):
            y_ticks.append(y_pos)
            y_labels.append(uav)
            
            for task in tasks:
                color = priority_colors.get(task['priority'], '#A8DADC')
                ax.barh(y_pos, task['duration'], left=task['start'], 
                       height=0.6, color=color, edgecolor='black', 
                       linewidth=1.5, alpha=0.8)
                
                # 添加任务标签
                label_x = task['start'] + task['duration'] / 2
                ax.text(label_x, y_pos, task['task_id'],
                       ha='center', va='center', size=10, weight='bold',
                       color='white' if task['priority'] == '紧急' else 'black')
            
            y_pos += 1
        
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, size=11)
        ax.set_xlabel('时间 (小时)', size=12, weight='bold')
        ax.set_ylabel('无人机', size=12, weight='bold')
        ax.set_title('任务执行时间甘特图', size=16, weight='bold', pad=20)
        ax.set_xlim(7.5, 12.5)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # 添加时间刻度
        ax.set_xticks(range(8, 13))
        ax.set_xticklabels([f'{h}:00' for h in range(8, 13)])
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, edgecolor='black', label=priority)
                          for priority, color in priority_colors.items()]
        ax.legend(handles=legend_elements, loc='upper right', 
                 title='优先级', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/4_gantt_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_dashboard(self):
        """绘制综合评估仪表盘"""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. 总体评分（大号显示）
        ax1 = fig.add_subplot(gs[0, 0])
        score = self.metrics['overall_score']
        color = '#2A9D8F' if score >= 80 else '#F4A261' if score >= 60 else '#E63946'
        
        ax1.text(0.5, 0.5, f'{score:.1f}', 
                ha='center', va='center', size=60, weight='bold', color=color)
        ax1.text(0.5, 0.15, '总体评分', 
                ha='center', va='center', size=14, weight='bold')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        
        # 2. 任务完成率
        ax2 = fig.add_subplot(gs[0, 1])
        tc = self.metrics['task_completion']
        completion = tc['completion_rate']
        
        wedges, texts, autotexts = ax2.pie([completion, 100-completion], 
                                            colors=['#2A9D8F', '#E5E5E5'],
                                            autopct='%1.1f%%', startangle=90,
                                            textprops={'size': 14, 'weight': 'bold'})
        ax2.set_title(f'任务完成率\n{tc["completed_tasks"]}/{tc["total_tasks"]}', 
                     size=12, weight='bold')
        
        # 3. 无人机利用率
        ax3 = fig.add_subplot(gs[0, 2])
        ru = self.metrics['resource_utilization']
        utilization = ru['utilization_rate']
        
        wedges, texts, autotexts = ax3.pie([utilization, 100-utilization], 
                                            colors=['#457B9D', '#E5E5E5'],
                                            autopct='%1.1f%%', startangle=90,
                                            textprops={'size': 14, 'weight': 'bold'})
        ax3.set_title(f'无人机利用率\n{ru["used_uavs"]}/{ru["total_uavs"]}使用', 
                     size=12, weight='bold')
        
        # 4. 各维度评分条形图
        ax4 = fig.add_subplot(gs[1, :])
        categories = ['任务完成度', '时间效率', '资源利用', '约束满足']
        scores = [
            self.metrics['task_completion']['score'] * 100,
            self.metrics['time_efficiency']['score'] * 100,
            self.metrics['resource_utilization']['score'] * 100,
            self.metrics['constraint_satisfaction']['score'] * 100
        ]
        
        colors = ['#E63946', '#F4A261', '#2A9D8F', '#457B9D']
        bars = ax4.barh(categories, scores, color=colors, edgecolor='black', linewidth=1.5)
        
        ax4.set_xlabel('评分', size=12, weight='bold')
        ax4.set_title('各维度详细评分', size=14, weight='bold')
        ax4.set_xlim(0, 100)
        ax4.grid(axis='x', alpha=0.3)
        
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax4.text(score + 2, bar.get_y() + bar.get_height()/2.,
                    f'{score:.1f}',
                    ha='left', va='center', size=11, weight='bold')
        
        # 5. 优先级任务统计
        ax5 = fig.add_subplot(gs[2, 0])
        priority_breakdown = tc['priority_breakdown']
        priorities = list(priority_breakdown.keys())
        completed = [priority_breakdown[p]['completed'] for p in priorities]
        
        colors_pie = ['#E63946', '#F4A261', '#2A9D8F', '#A8DADC']
        ax5.pie(completed, labels=priorities, colors=colors_pie,
               autopct='%1.0f%%', textprops={'size': 10})
        ax5.set_title('已完成任务优先级分布', size=11, weight='bold')
        
        # 6. 时间效率指标
        ax6 = fig.add_subplot(gs[2, 1])
        te = self.metrics['time_efficiency']
        
        time_metrics = ['总完成时间', '平均等待时间', '紧急响应时间']
        time_values = [
            te.get('total_completion_time_min', 0),
            te.get('average_wait_time_min', 0),
            te.get('urgent_response_time_min', 0)
        ]
        
        ax6.bar(range(len(time_metrics)), time_values, 
               color=['#264653', '#2A9D8F', '#E76F51'],
               edgecolor='black', linewidth=1.5)
        ax6.set_xticks(range(len(time_metrics)))
        ax6.set_xticklabels(time_metrics, rotation=15, ha='right', size=9)
        ax6.set_ylabel('时间 (分钟)', size=10, weight='bold')
        ax6.set_title('时间效率指标', size=11, weight='bold')
        ax6.grid(axis='y', alpha=0.3)
        
        # 7. 风险评估
        ax7 = fig.add_subplot(gs[2, 2])
        cs = self.metrics['constraint_satisfaction']
        risk_level = cs['risk_level']
        safety_score = cs['safety_score'] * 100
        
        risk_colors = {'低': '#2A9D8F', '中': '#F4A261', '高': '#E63946', '未知': '#A8DADC'}
        risk_color = risk_colors.get(risk_level, '#A8DADC')
        
        ax7.text(0.5, 0.6, risk_level, 
                ha='center', va='center', size=40, weight='bold', color=risk_color)
        ax7.text(0.5, 0.3, f'风险等级', 
                ha='center', va='center', size=12, weight='bold')
        ax7.text(0.5, 0.1, f'安全分数: {safety_score:.0f}', 
                ha='center', va='center', size=10)
        ax7.set_xlim(0, 1)
        ax7.set_ylim(0, 1)
        ax7.axis('off')
        
        # 总标题
        fig.suptitle('无人机任务分配评估综合仪表盘', 
                    size=18, weight='bold', y=0.98)
        
        plt.savefig(f'{self.output_dir}/5_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 综合仪表盘: {self.output_dir}/5_dashboard.png")


def visualize_from_files(allocation_file: str, metrics_file: str = None):
    """
    从文件读取数据并生成可视化
    
    Args:
        allocation_file: 分配方案JSON文件
        metrics_file: 评估指标JSON文件（可选，如果不提供会自动计算）
    """
    # 读取分配方案
    with open(allocation_file, 'r', encoding='utf-8') as f:
        allocation = json.load(f)
    
    # 读取或计算评估指标
    if metrics_file and os.path.exists(metrics_file):
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
    else:
        # 自动计算评估指标
        from evaluation_metrics import AllocationEvaluator
        evaluator = AllocationEvaluator(allocation)
        metrics = evaluator.evaluate_all()
    
    # 生成可视化
    visualizer = AllocationVisualizer(allocation, metrics)
    visualizer.visualize_all()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        allocation_file = sys.argv[1]
        metrics_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        allocation_file = "output_allocation.json"
        metrics_file = "output_allocation_evaluation.json"
    
    print(f"📊 正在生成可视化图表...")
    print(f"   分配方案: {allocation_file}")
    if metrics_file:
        print(f"   评估指标: {metrics_file}")
    print()
    
    try:
        visualize_from_files(allocation_file, metrics_file)
        print("\n✅ 可视化完成！")
    except FileNotFoundError as e:
        print(f"❌ 文件不存在: {e}")
    except Exception as e:
        print(f"❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()
