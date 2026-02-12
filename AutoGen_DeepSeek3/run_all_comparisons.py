"""
一键运行所有算法对比实验
AutoGen vs 贪心算法 vs 随机分配 vs 遗传算法 vs 整数规划
"""

import sys
import os


def main():
    """主函数：运行完整对比实验流程"""
    
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "AutoGen vs 所有基线算法 - 完整对比实验" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # 步骤1：检查AutoGen结果是否存在
    print("步骤 1/3: 检查AutoGen结果")
    print("="*70)
    
    if not os.path.exists('output_allocation.json'):
        print("❌ 未找到 AutoGen 结果文件: output_allocation.json")
        print("\n请先运行 AutoGen 算法:")
        print("   python autogen_uav_allocation.py")
        print("\n然后再运行本对比实验。")
        return
    
    print("✅ 找到 AutoGen 结果文件")
    print()
    
    # 步骤2：运行所有算法对比
    print("步骤 2/3: 运行所有算法对比")
    print("="*70)
    print("\n对比算法:")
    print("  1️⃣ AutoGen - 多智能体协作")
    print("  2️⃣ 贪心算法 - 按优先级依次分配")
    print("  3️⃣ 随机分配 - 随机选择分配")
    print("  4️⃣ 遗传算法 - 进化搜索优化")
    print("  5️⃣ 整数规划 - 数学优化求解")
    print()
    
    try:
        from comparison_all_algorithms import run_full_comparison
        results = run_full_comparison()
        
        if results is None:
            print("\n❌ 对比实验失败")
            return
    except Exception as e:
        print(f"\n❌ 对比实验运行失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # 步骤3：生成可视化
    print("步骤 3/3: 生成可视化图表")
    print("="*70)
    print()
    
    try:
        from visualize_all_algorithms import MultiAlgorithmVisualizer
        visualizer = MultiAlgorithmVisualizer()
        visualizer.visualize_all()
    except Exception as e:
        print(f"\n❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 完成
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "✨ 所有对比实验完成！✨" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    print("📊 生成的文件:")
    print()
    print("📁 comparison_results/")
    print("   ├── all_algorithms_comparison.json    所有算法对比数据 ⭐")
    print("   ├── comparison_table.tex              LaTeX表格（论文用）⭐")
    print("   ├── allocation_greedy.json            贪心算法分配方案")
    print("   ├── allocation_random.json            随机分配方案")
    print("   ├── allocation_genetic.json           遗传算法分配方案")
    print("   ├── allocation_ip.json                整数规划分配方案")
    print("   ├── evaluation_autogen.json           AutoGen评估结果")
    print("   ├── evaluation_greedy.json            贪心算法评估")
    print("   ├── evaluation_random.json            随机分配评估")
    print("   ├── evaluation_genetic.json           遗传算法评估")
    print("   └── evaluation_ip.json                整数规划评估")
    print()
    print("📁 comparison_visualizations/")
    print("   ├── all_1_overall_scores.png          总体评分对比 ⭐")
    print("   ├── all_2_radar_chart.png             雷达图对比 ⭐")
    print("   ├── all_3_heatmap.png                 性能热力图 ⭐")
    print("   ├── all_4_detailed_metrics.png        各维度详细对比")
    print("   ├── all_5_ranking.png                 排名和运行时间")
    print("   └── all_6_dashboard.png               综合仪表盘 ⭐")
    print()
    
    # 显示关键结果
    print("🏆 关键结果:")
    print()
    
    # 读取结果并显示
    import json
    with open('comparison_results/all_algorithms_comparison.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 按分数排序
    sorted_results = sorted(
        [(algo, data['results'][algo]['overall_score']) 
         for algo in data['algorithms']],
        key=lambda x: x[1],
        reverse=True
    )
    
    algo_names = {
        'autogen': 'AutoGen',
        'greedy': '贪心算法',
        'random': '随机分配',
        'genetic': '遗传算法',
        'ip': '整数规划'
    }
    
    print("   算法排名（按总分）:")
    for rank, (algo, score) in enumerate(sorted_results, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"  {rank}."
        print(f"   {medal} {algo_names[algo]:<12} {score:>6.2f}分")
    
    print()
    print(f"   📊 最高分: {data['summary']['max_score']:.2f}")
    print(f"   📊 最低分: {data['summary']['min_score']:.2f}")
    print(f"   📊 平均分: {data['summary']['avg_score']:.2f}")
    print(f"   📊 分数范围: {data['summary']['score_range']:.2f}")
    
    print()
    print("💡 下一步:")
    print("   1. 查看可视化图表了解详细对比")
    print("   2. 阅读 comparison_results/all_algorithms_comparison.json")
    print("   3. 使用 comparison_table.tex 插入论文")
    print("   4. 分析各算法的优劣势")
    print()
    
    # 生成简要对比表格
    print("📋 快速对比表格:")
    print()
    print(f"{'算法':<12} {'总分':<8} {'任务完成':<10} {'时间效率':<10} {'资源利用':<10} {'约束满足':<10}")
    print("-" * 70)
    
    for algo in data['algorithms']:
        result = data['results'][algo]
        print(f"{algo_names[algo]:<12} "
              f"{result['overall_score']:<8.2f} "
              f"{result['task_completion_rate']:<10.1f} "
              f"{result['time_efficiency']:<10.1f} "
              f"{result['resource_utilization']:<10.1f} "
              f"{result['constraint_satisfaction']:<10.1f}")
    
    print()


if __name__ == "__main__":
    main()
