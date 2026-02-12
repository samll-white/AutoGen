"""
智能体消融实验（Ablation Study）
验证每个智能体的必要性和贡献
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from evaluation_metrics import AllocationEvaluator


class AblationExperiment:
    """智能体消融实验管理类"""
    
    def __init__(self):
        self.results = {}
        self.output_dir = "ablation_results"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 实验配置
        self.configurations = {
            '3-agent': {
                'name': '3智能体（最小配置）',
                'agents': ['TaskAnalyzer', 'SolutionGenerator', 'Arbitrator'],
                'description': '缺少资源评估和冲突检测',
                'expected': '基础分配能力，可能资源匹配不合理且有冲突'
            },
            '4-agent-v1': {
                'name': '4智能体-V1（无资源评估）',
                'agents': ['TaskAnalyzer', 'SolutionGenerator', 'ConflictDetector', 'Arbitrator'],
                'description': '去掉ResourceEvaluator',
                'expected': '有冲突检测但资源匹配可能不合理'
            },
            '4-agent-v2': {
                'name': '4智能体-V2（无冲突检测）',
                'agents': ['TaskAnalyzer', 'ResourceEvaluator', 'SolutionGenerator', 'Arbitrator'],
                'description': '去掉ConflictDetector',
                'expected': '资源评估良好但可能产生冲突'
            },
            '5-agent': {
                'name': '5智能体（完整配置-基准）',
                'agents': ['TaskAnalyzer', 'ResourceEvaluator', 'SolutionGenerator', 
                          'ConflictDetector', 'Arbitrator'],
                'description': '完整配置',
                'expected': '最优表现'
            },
            '6-agent': {
                'name': '6智能体（增强配置）',
                'agents': ['TaskAnalyzer', 'ResourceEvaluator', 'SolutionGenerator', 
                          'ConflictDetector', 'PathPlanner', 'Arbitrator'],
                'description': '增加PathPlanner路径规划',
                'expected': '路径优化能力提升'
            }
        }
        
        # 加载默认任务描述
        self.task_description = self._load_default_task()
    
    def _load_default_task(self) -> str:
        """加载默认任务描述"""
        return """
多无人机任务分配场景

【可用无人机】
1. UAV-001（侦察型）
   - 最大飞行时间：120分钟
   - 最大速度：80 km/h
   - 载重能力：0 kg
   - 当前状态：A基地，电量100%

2. UAV-002（运输型）
   - 最大飞行时间：90分钟
   - 最大速度：60 km/h
   - 载重能力：5 kg
   - 当前状态：A基地，电量85%

3. UAV-003（侦察型）
   - 最大飞行时间：100分钟
   - 最大速度：70 km/h
   - 载重能力：0 kg
   - 当前状态：B基地，电量90%

4. UAV-004（多用途）
   - 最大飞行时间：80分钟
   - 最大速度：65 km/h
   - 载重能力：2 kg
   - 当前状态：A基地，电量95%

【待分配任务】
1. T1 - 区域侦察（高优先级）
   - 时间窗口：08:00-10:00
   - 预计用时：30分钟
   - 位置：C区域

2. T2 - 物资运输（高优先级）
   - 时间窗口：08:30-09:30
   - 预计用时：40分钟
   - 载重需求：3kg

3. T3 - 目标监控（中优先级）
   - 时间窗口：09:00-12:00
   - 预计用时：60分钟

4. T4 - 紧急侦察（紧急）
   - 时间窗口：08:00-08:30
   - 预计用时：20分钟

5. T5 - 设备投送（低优先级）
   - 时间窗口：10:00-12:00
   - 预计用时：30分钟
   - 载重需求：1kg

【约束条件】
1. 禁飞区：D区域在09:00-09:30为临时禁飞区
2. 并发限制：每架无人机同时只能执行一个任务
3. 返航要求：任务完成后需返回基地

请为以上任务生成最优分配方案。
"""
    
    def _get_llm_client(self):
        """获取LLM客户端"""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ 错误：未找到API密钥！\n"
                "请确保 .env 文件中设置了 DEEPSEEK_API_KEY\n"
                "例如：DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx"
            )
        
        return OpenAIChatCompletionClient(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def create_task_analyzer(self) -> AssistantAgent:
        """创建任务分析智能体"""
        system_message = """你是任务分析专家。
职责：解析和分析任务需求。
输出：
1. 任务优先级排序
2. 关键约束识别
3. 资源需求分析
保持简洁，不要输出JSON。"""
        
        return AssistantAgent(
            "TaskAnalyzer",
            model_client=self._get_llm_client(),
            system_message=system_message
        )
    
    def create_resource_evaluator(self) -> AssistantAgent:
        """创建资源评估智能体"""
        system_message = """你是资源评估专家。
职责：评估无人机能力和可用性。
输出：
1. 各无人机的能力评估
2. 任务-无人机匹配度分析
3. 资源瓶颈识别
保持简洁，不要输出JSON。"""
        
        return AssistantAgent(
            "ResourceEvaluator",
            model_client=self._get_llm_client(),
            system_message=system_message
        )
    
    def create_solution_generator(self) -> AssistantAgent:
        """创建方案生成智能体"""
        system_message = """你是方案生成专家。
职责：生成任务分配方案。
要求：必须输出JSON格式的分配方案。
输出格式：
{
  "final_allocation": {
    "assignments": [
      {
        "task_id": "T1",
        "task_name": "任务名",
        "assigned_uav": "UAV-001",
        "start_time": "08:00",
        "estimated_duration": "30分钟",
        "priority": "高",
        "rationale": "分配理由"
      }
    ],
    "unassigned_tasks": [],
    "total_completion_time": "10:00"
  }
}
重要：最后必须输出完整JSON，不要其他内容。"""
        
        return AssistantAgent(
            "SolutionGenerator",
            model_client=self._get_llm_client(),
            system_message=system_message
        )
    
    def create_conflict_detector(self) -> AssistantAgent:
        """创建冲突检测智能体"""
        system_message = """你是冲突检测专家。
职责：检查方案中的冲突和问题。
输出：
1. 时间冲突检测
2. 资源冲突检测
3. 约束违反检测
4. 改进建议
保持简洁，不要输出JSON。"""
        
        return AssistantAgent(
            "ConflictDetector",
            model_client=self._get_llm_client(),
            system_message=system_message
        )
    
    def create_path_planner(self) -> AssistantAgent:
        """创建路径规划智能体"""
        system_message = """你是路径规划专家。
职责：优化无人机飞行路径。
输出：
1. 飞行路径优化建议
2. 时间估算优化
3. 能耗优化建议
保持简洁，不要输出JSON。"""
        
        return AssistantAgent(
            "PathPlanner",
            model_client=self._get_llm_client(),
            system_message=system_message
        )
    
    def create_arbitrator(self) -> AssistantAgent:
        """创建仲裁智能体"""
        system_message = """你是最终仲裁者。
职责：综合所有意见，输出最终方案。
要求：必须输出JSON格式的最终方案。
输出格式：
{
  "final_allocation": {
    "decision_time": "时间戳",
    "total_tasks": 5,
    "total_uavs": 4,
    "assignments": [方案列表],
    "unassigned_tasks": [],
    "total_completion_time": "10:00",
    "risk_assessment": "风险评估",
    "notes": "备注"
  }
}
重要：最后必须输出完整JSON，说"TERMINATE"结束。"""
        
        return AssistantAgent(
            "Arbitrator",
            model_client=self._get_llm_client(),
            system_message=system_message
        )
    
    async def run_configuration(self, config_name: str) -> Dict[str, Any]:
        """运行指定配置的实验"""
        config = self.configurations[config_name]
        
        print(f"\n{'='*70}")
        print(f"运行配置: {config['name']}")
        print(f"智能体: {', '.join(config['agents'])}")
        print(f"说明: {config['description']}")
        print('='*70)
        
        start_time = time.time()
        
        # 创建智能体
        agents = []
        agent_creators = {
            'TaskAnalyzer': self.create_task_analyzer,
            'ResourceEvaluator': self.create_resource_evaluator,
            'SolutionGenerator': self.create_solution_generator,
            'ConflictDetector': self.create_conflict_detector,
            'PathPlanner': self.create_path_planner,
            'Arbitrator': self.create_arbitrator
        }
        
        for agent_name in config['agents']:
            agents.append(agent_creators[agent_name]())
        
        # 创建团队
        termination = MaxMessageTermination(20) | TextMentionTermination("TERMINATE")
        team = RoundRobinGroupChat(agents, termination_condition=termination)
        
        # 运行对话
        try:
            result = await team.run(task=self.task_description)
            
            runtime = time.time() - start_time
            
            # 提取结果
            allocation_result = self._extract_allocation(result)
            
            if allocation_result:
                # 保存结果
                output_file = f'{self.output_dir}/allocation_{config_name}.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(allocation_result, f, ensure_ascii=False, indent=2)
                
                print(f"\n✅ {config['name']} 完成")
                print(f"   运行时间: {runtime:.2f}秒")
                print(f"   分配任务: {len(allocation_result.get('final_allocation', {}).get('assignments', []))}/5")
                print(f"   保存到: {output_file}")
                
                return {
                    'config_name': config_name,
                    'config': config,
                    'result': allocation_result,
                    'runtime': runtime,
                    'success': True
                }
            else:
                print(f"\n❌ {config['name']} 失败：未能提取有效分配方案")
                return {
                    'config_name': config_name,
                    'config': config,
                    'result': None,
                    'runtime': runtime,
                    'success': False
                }
        
        except Exception as e:
            runtime = time.time() - start_time
            print(f"\n❌ {config['name']} 运行失败: {e}")
            return {
                'config_name': config_name,
                'config': config,
                'result': None,
                'runtime': runtime,
                'success': False,
                'error': str(e)
            }
    
    def _extract_allocation(self, result) -> Dict:
        """从对话结果中提取分配方案"""
        import re
        
        # 获取最后几条消息
        messages = []
        for msg in result.messages[-5:]:
            if hasattr(msg, 'content'):
                messages.append(msg.content)
        
        # 尝试提取JSON
        for msg in reversed(messages):
            if isinstance(msg, str):
                # 查找JSON块
                json_match = re.search(r'\{[\s\S]*"final_allocation"[\s\S]*\}', msg)
                if json_match:
                    try:
                        allocation = json.loads(json_match.group())
                        return allocation
                    except:
                        continue
        
        return None
    
    async def run_all_experiments(self):
        """运行所有消融实验"""
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "智能体消融实验" + " " * 28 + "║")
        print("╚" + "═" * 68 + "╝")
        print(f"\n实验时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n实验配置:")
        for i, (config_name, config) in enumerate(self.configurations.items(), 1):
            print(f"  {i}. {config['name']}")
            print(f"     智能体数: {len(config['agents'])}")
            print(f"     预期: {config['expected']}")
        
        # 运行所有配置
        for config_name in self.configurations.keys():
            result = await self.run_configuration(config_name)
            self.results[config_name] = result
        
        # 评估所有结果
        self.evaluate_all_results()
        
        # 生成对比报告
        self.generate_comparison_report()
        
        # 保存完整结果
        self.save_complete_results()
        
        return self.results
    
    def evaluate_all_results(self):
        """评估所有实验结果"""
        print(f"\n{'='*70}")
        print("评估所有配置")
        print('='*70)
        
        for config_name, data in self.results.items():
            if data['success'] and data['result']:
                print(f"\n评估 {data['config']['name']}...")
                
                try:
                    evaluator = AllocationEvaluator(data['result'])
                    metrics = evaluator.evaluate_all()
                    
                    # 保存评估结果
                    eval_file = f'{self.output_dir}/evaluation_{config_name}.json'
                    with open(eval_file, 'w', encoding='utf-8') as f:
                        json.dump(metrics, f, ensure_ascii=False, indent=2)
                    
                    data['metrics'] = metrics
                    print(f"   总体评分: {metrics['overall_score']:.2f}/100")
                
                except Exception as e:
                    print(f"   ❌ 评估失败: {e}")
                    data['metrics'] = None
            else:
                print(f"\n跳过 {data['config']['name']}（运行失败）")
                data['metrics'] = None
    
    def generate_comparison_report(self):
        """生成对比报告"""
        print(f"\n{'='*70}")
        print("消融实验对比报告")
        print('='*70)
        
        # 表格头
        print(f"\n{'配置':<20} {'智能体数':<10} {'总分':<10} {'任务完成':<10} {'时间效率':<10} {'资源利用':<10}")
        print('-' * 70)
        
        # 显示结果
        for config_name in self.configurations.keys():
            data = self.results[config_name]
            config = data['config']
            
            if data['success'] and data['metrics']:
                metrics = data['metrics']
                print(f"{config['name']:<20} "
                      f"{len(config['agents']):<10} "
                      f"{metrics['overall_score']:<10.2f} "
                      f"{metrics['task_completion']['completion_rate']:<10.1f} "
                      f"{metrics['time_efficiency']['score']*100:<10.1f} "
                      f"{metrics['resource_utilization']['score']*100:<10.1f}")
            else:
                print(f"{config['name']:<20} "
                      f"{len(config['agents']):<10} "
                      f"{'失败':<10} "
                      f"{'-':<10} "
                      f"{'-':<10} "
                      f"{'-':<10}")
        
        # 找出最佳配置
        best_config = None
        best_score = -1
        
        for config_name, data in self.results.items():
            if data['success'] and data['metrics']:
                score = data['metrics']['overall_score']
                if score > best_score:
                    best_score = score
                    best_config = (config_name, data)
        
        if best_config:
            print(f"\n🏆 最佳配置: {best_config[1]['config']['name']}")
            print(f"   总体评分: {best_score:.2f}/100")
            print(f"   智能体数: {len(best_config[1]['config']['agents'])}")
    
    def save_complete_results(self):
        """保存完整实验结果"""
        complete_results = {
            'experiment_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'configurations': {},
            'summary': {}
        }
        
        # 收集所有配置的结果
        for config_name, data in self.results.items():
            config_data = {
                'name': data['config']['name'],
                'agents': data['config']['agents'],
                'agent_count': len(data['config']['agents']),
                'description': data['config']['description'],
                'expected': data['config']['expected'],
                'runtime': data['runtime'],
                'success': data['success']
            }
            
            if data['success'] and data['metrics']:
                config_data['metrics'] = {
                    'overall_score': data['metrics']['overall_score'],
                    'task_completion_rate': data['metrics']['task_completion']['completion_rate'],
                    'time_efficiency': data['metrics']['time_efficiency']['score'] * 100,
                    'resource_utilization': data['metrics']['resource_utilization']['score'] * 100,
                    'constraint_satisfaction': data['metrics']['constraint_satisfaction']['score'] * 100
                }
            else:
                config_data['metrics'] = None
            
            complete_results['configurations'][config_name] = config_data
        
        # 生成摘要
        successful_configs = [(name, data) for name, data in self.results.items() 
                             if data['success'] and data['metrics']]
        
        if successful_configs:
            scores = [data['metrics']['overall_score'] for _, data in successful_configs]
            complete_results['summary'] = {
                'total_experiments': len(self.configurations),
                'successful_experiments': len(successful_configs),
                'max_score': max(scores),
                'min_score': min(scores),
                'avg_score': sum(scores) / len(scores),
                'score_range': max(scores) - min(scores)
            }
            
            # 找出最佳配置
            best = max(successful_configs, key=lambda x: x[1]['metrics']['overall_score'])
            complete_results['summary']['best_configuration'] = {
                'name': best[1]['config']['name'],
                'config_key': best[0],
                'agent_count': len(best[1]['config']['agents']),
                'score': best[1]['metrics']['overall_score']
            }
        
        # 保存JSON
        output_file = f'{self.output_dir}/ablation_complete_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 完整实验结果已保存到: {output_file}")


async def run_ablation_study():
    """运行消融实验"""
    experiment = AblationExperiment()
    results = await experiment.run_all_experiments()
    
    print("\n" + "="*70)
    print("✨ 消融实验完成！")
    print("="*70)
    print("\n查看结果:")
    print("  • ablation_results/ablation_complete_results.json (完整数据)")
    print("  • ablation_results/allocation_*.json (各配置分配方案)")
    print("  • ablation_results/evaluation_*.json (各配置评估结果)")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_ablation_study())
