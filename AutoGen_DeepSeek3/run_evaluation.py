"""
独立评估和可视化脚本
用于对已有的分配方案进行评估和可视化
"""

import sys
import json
from evaluation_metrics import AllocationEvaluator, evaluate_allocation_from_file
from visualize_results import AllocationVisualizer


def main():
    """主函数"""
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     无人机任务分配方案评估和可视化工具                          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # 获取输入文件
    if len(sys.argv) > 1:
        allocation_file = sys.argv[1]
    else:
        allocation_file = "output_allocation.json"
    
    print(f"📂 读取分配方案: {allocation_file}")
    print()
    
    try:
        # 1. 评估分配方案
        print("=" * 70)
        print("📊 第一步：评估分配方案")
        print("=" * 70)
        print()
        
        metrics, report = evaluate_allocation_from_file(allocation_file)
        
        # 显示评估报告
        print(report)
        
        # 保存评估结果
        eval_file = allocation_file.replace('.json', '_evaluation.json')
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        print(f"\n💾 评估结果已保存到: {eval_file}")
        
        # 2. 生成可视化
        print()
        print("=" * 70)
        print("🎨 第二步：生成可视化图表")
        print("=" * 70)
        print()
        
        # 读取分配方案
        with open(allocation_file, 'r', encoding='utf-8') as f:
            allocation = json.load(f)
        
        # 创建可视化器
        visualizer = AllocationVisualizer(allocation, metrics)
        visualizer.visualize_all()
        
        print()
        print("=" * 70)
        print("✅ 评估和可视化完成！")
        print("=" * 70)
        print()
        print("📊 生成的文件：")
        print(f"   • 评估报告: {eval_file}")
        print(f"   • 可视化图表: visualization_outputs/")
        print(f"     - 1_radar_chart.png (雷达图)")
        print(f"     - 2_task_completion.png (任务完成度)")
        print(f"     - 3_resource_utilization.png (资源利用)")
        print(f"     - 4_gantt_chart.png (甘特图)")
        print(f"     - 5_dashboard.png (综合仪表盘)")
        print()
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {allocation_file}")
        print()
        print("使用方法:")
        print(f"  python {sys.argv[0]} [分配方案JSON文件]")
        print()
        print("示例:")
        print(f"  python {sys.argv[0]} output_allocation.json")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
