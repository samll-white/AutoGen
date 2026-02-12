"""
一键运行完整对比实验
AutoGen vs 贪心算法
"""

import sys
import os

def main():
    """主函数：运行完整对比实验流程"""
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║        AutoGen vs 贪心算法 - 完整对比实验流程                   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
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
    
    # 步骤2：运行对比实验
    print("步骤 2/3: 运行对比实验")
    print("="*70)
    print()
    
    try:
        from comparison_experiments import run_autogen_vs_greedy
        result = run_autogen_vs_greedy()
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
        from comparison_visualization import ComparisonVisualizer
        visualizer = ComparisonVisualizer()
        visualizer.visualize_all()
    except Exception as e:
        print(f"\n❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 完成
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    ✨ 对比实验完成！✨                           ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    print("📊 生成的文件:")
    print()
    print("📁 comparison_results/")
    print("   ├── autogen_vs_greedy_comparison.json  对比结果数据")
    print("   ├── allocation_greedy.json             贪心算法分配方案")
    print("   ├── evaluation_autogen.json            AutoGen评估结果")
    print("   └── evaluation_greedy.json             贪心算法评估结果")
    print()
    print("📁 comparison_visualizations/")
    print("   ├── 1_overall_comparison.png           总体评分对比")
    print("   ├── 2_radar_comparison.png             雷达图对比")
    print("   ├── 3_metrics_comparison.png           各指标详细对比")
    print("   ├── 4_advantage_analysis.png           优势分析")
    print("   └── 5_comprehensive_dashboard.png      综合仪表盘")
    print()
    
    # 显示关键结果
    print("🏆 关键结果:")
    print()
    
    autogen_score = result['autogen']['overall_score']
    greedy_score = result['greedy']['overall_score']
    winner = result['comparison']['winner']
    score_diff = abs(result['comparison']['score_difference'])
    
    print(f"   AutoGen 总分:  {autogen_score:.2f}/100")
    print(f"   贪心算法总分:  {greedy_score:.2f}/100")
    print()
    
    if winner == 'autogen':
        print(f"   🎯 AutoGen 表现更优，领先 {score_diff:.2f} 分")
    else:
        print(f"   ⚠️  贪心算法表现更优，领先 {score_diff:.2f} 分")
    
    print()
    print("💡 下一步:")
    print("   1. 查看可视化图表了解详细对比")
    print("   2. 阅读 comparison_results/autogen_vs_greedy_comparison.json")
    print("   3. 继续对比其他算法（遗传算法、整数规划、随机分配）")
    print()


if __name__ == "__main__":
    main()
