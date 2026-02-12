"""
一键运行消融实验
验证每个智能体的必要性
"""

import sys
import asyncio


async def main():
    """主函数：运行完整消融实验流程"""
    
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "智能体消融实验 - 完整流程" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    print("实验目的:")
    print("  验证每个智能体的必要性和对整体性能的贡献")
    print()
    
    print("实验配置:")
    print("  1️⃣ 3智能体（最小配置） - 缺少资源评估和冲突检测")
    print("  2️⃣ 4智能体-V1（无资源评估） - 资源匹配可能不合理")
    print("  3️⃣ 4智能体-V2（无冲突检测） - 可能产生冲突")
    print("  4️⃣ 5智能体（完整配置） - 基准表现 ⭐")
    print("  5️⃣ 6智能体（增强配置） - 增加路径规划")
    print()
    
    # 步骤1：运行消融实验
    print("步骤 1/2: 运行消融实验")
    print("="*70)
    print("\n⚠️  注意：这将运行5个配置，预计需要10-25分钟")
    print("   每个配置都会调用LLM API，请确保API密钥已配置")
    print()
    
    input("按Enter键开始实验...")
    
    try:
        from ablation_experiment import run_ablation_study
        results = await run_ablation_study()
        
        if not results:
            print("\n❌ 消融实验失败")
            return
    except Exception as e:
        print(f"\n❌ 消融实验运行失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # 步骤2：生成可视化
    print("步骤 2/2: 生成可视化图表")
    print("="*70)
    print()
    
    try:
        from ablation_visualizer import AblationVisualizer
        visualizer = AblationVisualizer()
        visualizer.visualize_all()
    except Exception as e:
        print(f"\n❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 完成
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 22 + "✨ 消融实验完成！✨" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    print("📊 生成的文件:")
    print()
    print("📁 ablation_results/")
    print("   ├── ablation_complete_results.json    完整实验数据 ⭐")
    print("   ├── allocation_3-agent.json            3智能体分配方案")
    print("   ├── allocation_4-agent-v1.json         4智能体-V1方案")
    print("   ├── allocation_4-agent-v2.json         4智能体-V2方案")
    print("   ├── allocation_5-agent.json            5智能体方案（基准）")
    print("   ├── allocation_6-agent.json            6智能体方案")
    print("   └── evaluation_*.json                  各配置评估结果")
    print()
    print("📁 ablation_visualizations/")
    print("   ├── ablation_1_overall_scores.png      总体评分对比 ⭐")
    print("   ├── ablation_2_count_vs_score.png      数量与性能关系 ⭐")
    print("   ├── ablation_3_detailed_metrics.png    各维度详细对比")
    print("   ├── ablation_4_contribution_analysis.png 智能体贡献分析 ⭐")
    print("   └── ablation_5_dashboard.png           综合仪表盘 ⭐")
    print()
    
    # 显示关键结果
    print("🏆 关键结果:")
    print()
    
    import json
    try:
        with open('ablation_results/ablation_complete_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 显示各配置评分
        print("   各配置评分:")
        for config_key in ['3-agent', '4-agent-v1', '4-agent-v2', '5-agent', '6-agent']:
            config_data = data['configurations'].get(config_key)
            if config_data and config_data['success'] and config_data['metrics']:
                score = config_data['metrics']['overall_score']
                name = config_data['name']
                agent_count = config_data['agent_count']
                print(f"   • {name:<30} {agent_count}智能体  {score:>6.2f}分")
        
        print()
        if 'best_configuration' in data['summary']:
            best = data['summary']['best_configuration']
            print(f"   🎯 最佳配置: {best['name']}")
            print(f"      智能体数: {best['agent_count']}")
            print(f"      评分: {best['score']:.2f}")
        
        print()
        print(f"   📊 分数范围: {data['summary'].get('score_range', 0):.2f}")
        print(f"   📊 平均分: {data['summary'].get('avg_score', 0):.2f}")
    
    except Exception as e:
        print(f"   ⚠️  无法读取结果: {e}")
    
    print()
    print("💡 下一步:")
    print("   1. 查看可视化图表分析每个智能体的贡献")
    print("   2. 阅读 ablation_results/ablation_complete_results.json")
    print("   3. 将结果用于论文的消融实验章节")
    print("   4. 分析哪些智能体是必要的，哪些是可选的")
    print()


if __name__ == "__main__":
    asyncio.run(main())
