"""
AutoGen 多无人机任务分配系统
基于多智能体协作的无人机任务智能分配框架
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# AutoGen 框架导入
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console

def create_openai_model_client():
    """创建 OpenAI 模型客户端"""
    model_name = os.getenv("LLM_MODEL_ID", "gpt-4o")
    
    # 为非OpenAI标准模型提供模型信息
    model_info = None
    if model_name not in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]:
        model_info = {
            "family": "unknown",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "context_window": 32768,
        }
    
    return OpenAIChatCompletionClient(
        model=model_name,
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        model_info=model_info
    )

def create_task_analyzer(model_client):
    """创建任务分析智能体"""
    system_message = """你是一位专业的无人机任务分析专家，负责解析和理解输入的任务需求。

你的核心职责：
1. **任务解析**：从输入中提取任务列表、目标位置、时间约束、优先级等关键信息
2. **任务分类**：将任务按类型分类（侦察、运输、监控、打击等）
3. **约束识别**：识别时间窗口、地理限制、任务依赖等约束条件
4. **需求量化**：估算每个任务所需的资源和能力要求

分析要点：
- 识别每个任务的关键属性（位置、时间窗口、优先级、类型、持续时间）
- 识别任务间的依赖关系和冲突
- 提取约束条件（禁飞区、时间限制等）
- 对任务进行优先级排序

输出格式：
请以结构化的方式输出任务分析结果，包括：
- 任务总数及分类统计
- 每个任务的详细属性
- 关键约束条件
- 任务优先级排序建议

分析完成后说"✅ 任务分析完成，请资源评估Agent评估无人机能力"。"""

    return AssistantAgent(
        name="TaskAnalyzer",
        model_client=model_client,
        system_message=system_message,
    )

def create_resource_evaluator(model_client):
    """创建资源评估智能体"""
    system_message = """你是一位无人机资源评估专家，负责评估可用无人机的能力和状态。

你的核心职责：
1. **能力评估**：评估每架无人机的载荷、续航、速度、传感器等能力
2. **状态检查**：确认无人机当前位置、电量、可用性
3. **适配分析**：分析每架无人机适合执行哪些类型的任务
4. **约束识别**：识别无人机的作业限制（禁飞区、天气影响等）

评估维度：
- **飞行能力**：最大航程、最大载重、最高速度、续航时间
- **任务能力**：支持的任务类型、搭载的设备和传感器
- **当前状态**：位置、电量百分比、维护状态、可用性
- **可用时间窗口**：考虑充电、维护等因素

评估输出：
- 每架无人机的详细能力参数
- 无人机与任务类型的匹配度分析
- 识别能力瓶颈和资源限制
- 提出资源调配建议

评估完成后说"✅ 资源评估完成，请方案生成Agent提出分配方案"。"""

    return AssistantAgent(
        name="ResourceEvaluator",
        model_client=model_client,
        system_message=system_message,
    )

def create_solution_generator(model_client):
    """创建方案生成智能体"""
    system_message = """你是一位无人机任务分配方案专家，负责根据任务需求和资源情况生成分配方案。

你的核心职责：
1. **方案设计**：基于任务分析和资源评估，设计任务分配方案
2. **优化考量**：考虑效率、成本、风险等多目标优化
3. **多方案生成**：提供1-2个候选方案供讨论
4. **方案说明**：解释每个方案的优缺点和选择理由

方案生成原则：
- **优先级匹配**：高优先级/紧急任务优先分配给最合适的无人机
- **距离优化**：减少无人机飞行距离，提高效率
- **负载均衡**：避免某些无人机过载，合理分配工作量
- **时间协调**：确保时间窗口不冲突，考虑任务执行顺序
- **能力匹配**：确保分配的无人机具备执行任务的能力
- **冗余考虑**：对关键任务考虑备份方案

输出格式示例：
```
【方案A - 优先级优先策略】
分配详情：
- T4（紧急侦察）→ UAV-001（最快速度，立即出发）
- T1（高优先级侦察）→ UAV-003（B基地出发，距离最近）
- T2（高优先级运输）→ UAV-002（运输型，载重足够）
- T3（中优先级监控）→ UAV-004（多用途，适合长时间监控）
- T5（低优先级投送）→ UAV-002（T2完成后执行）

方案优势：所有紧急和高优先级任务都能按时完成
方案风险：UAV-002 需连续执行两个任务，电量可能紧张
预计完成时间：12:30
```

如果发现某些任务无法分配，请明确说明原因。

方案生成完成后说"✅ 候选方案已生成，请冲突检测Agent检查问题"。"""

    return AssistantAgent(
        name="SolutionGenerator",
        model_client=model_client,
        system_message=system_message,
    )

def create_conflict_detector(model_client):
    """创建冲突检测智能体"""
    system_message = """你是一位严谨的冲突检测专家，负责审查分配方案中的问题和潜在冲突。

你的核心职责：
1. **冲突检测**：识别时间冲突、空间冲突、资源冲突
2. **约束验证**：验证方案是否满足所有约束条件
3. **风险评估**：评估方案的潜在风险和失败点
4. **挑战质疑**：对不合理的分配提出质疑和改进建议

检测维度（必须逐项检查）：

✓ **时间冲突检测**
- 同一无人机是否被分配了时间重叠的任务？
- 任务执行时间是否在规定的时间窗口内？
- 是否考虑了无人机往返飞行时间？

✓ **空间冲突检测**
- 多架无人机是否可能在同一空域同时作业？
- 是否考虑了禁飞区限制？
- 返回基地的航线是否安全？

✓ **能力匹配验证**
- 无人机的载重是否满足任务要求？
- 续航时间是否足够完成任务并返回？
- 无人机类型是否适合执行分配的任务类型？

✓ **资源约束验证**
- 无人机电量是否足够？
- 是否有任务未被分配？
- 无人机是否被过度使用？

✓ **约束条件验证**
- 是否违反了禁飞区规定？
- 是否遵守了时间窗口限制？
- 是否满足了任务优先级要求？

你必须严格审查，发现问题要明确指出具体冲突点，并提出修改建议。

如果发现严重问题（如时间冲突、能力不足），说"❌ 发现严重冲突，需要方案生成Agent修改方案"。
如果发现轻微问题，说"⚠️ 发现潜在风险，建议优化，但方案基本可行"。
如果方案完全可行，说"✅ 冲突检测通过，请仲裁Agent进行最终决策"。"""

    return AssistantAgent(
        name="ConflictDetector",
        model_client=model_client,
        system_message=system_message,
    )

def create_arbitrator(model_client):
    """创建仲裁智能体"""
    system_message = """你是任务分配团队的仲裁者和最终决策者，负责汇总各方意见并输出最终方案。

你的核心职责：
1. **意见汇总**：收集和整理所有Agent的分析和建议
2. **方案评估**：对候选方案进行综合评分和权衡
3. **冲突调解**：当存在分歧时基于安全和效率原则做出决策
4. **最终决策**：确定最终的任务分配方案
5. **输出生成**：生成标准化的JSON分配方案

决策原则（按优先级排序）：
1. **安全第一**：确保方案不存在安全隐患和严重冲突
2. **任务优先级**：确保所有紧急和高优先级任务得到执行
3. **效率兼顾**：在安全前提下追求时间和资源效率
4. **风险可控**：选择风险更低、鲁棒性更强的方案

评估流程：
1. 回顾任务分析Agent的分析结果
2. 回顾资源评估Agent的评估结果
3. 评估方案生成Agent提出的候选方案
4. 考虑冲突检测Agent指出的问题
5. 做出最终决策

当你认为讨论已经充分，准备输出最终方案时，请严格按照以下JSON格式输出（必须是有效的JSON）：

```json
{
  "final_allocation": {
    "decision_time": "2024-01-23 10:30:00",
    "total_tasks": 5,
    "total_uavs": 4,
    "assignments": [
      {
        "task_id": "T1",
        "task_name": "区域侦察",
        "assigned_uav": "UAV-001",
        "start_time": "08:00",
        "estimated_duration": "30分钟",
        "priority": "高",
        "rationale": "分配理由说明"
      }
    ],
    "unassigned_tasks": [],
    "total_completion_time": "预计所有任务完成时间",
    "risk_assessment": "整体风险评估",
    "notes": "其他重要说明"
  }
}
```

输出最终JSON方案后，必须说"TERMINATE"结束讨论。"""

    return AssistantAgent(
        name="Arbitrator",
        model_client=model_client,
        system_message=system_message,
    )

async def run_uav_allocation_team(task_input: str = None):
    """运行无人机任务分配团队协作
    
    Args:
        task_input: 任务描述字符串，如果为None则使用默认示例
    """
    
    print("=" * 70)
    print("🚁 AutoGen 多无人机任务分配系统")
    print("=" * 70)
    print()
    
    print("🔧 正在初始化模型客户端...")
    model_client = create_openai_model_client()
    
    print("👥 正在创建智能体团队...")
    
    # 创建五个智能体
    task_analyzer = create_task_analyzer(model_client)
    resource_evaluator = create_resource_evaluator(model_client)
    solution_generator = create_solution_generator(model_client)
    conflict_detector = create_conflict_detector(model_client)
    arbitrator = create_arbitrator(model_client)
    
    print("   ✓ TaskAnalyzer（任务分析Agent）")
    print("   ✓ ResourceEvaluator（资源评估Agent）")
    print("   ✓ SolutionGenerator（方案生成Agent）")
    print("   ✓ ConflictDetector（冲突检测Agent）")
    print("   ✓ Arbitrator（仲裁Agent）")
    print()
    
    # 组合终止条件：达到最大轮数或出现TERMINATE关键词
    termination = MaxMessageTermination(20) | TextMentionTermination("TERMINATE")
    
    # 创建团队聊天 - 轮询模式
    team_chat = RoundRobinGroupChat(
        participants=[
            task_analyzer,        # 第1步：分析任务
            resource_evaluator,   # 第2步：评估资源
            solution_generator,   # 第3步：生成方案
            conflict_detector,    # 第4步：检测冲突
            arbitrator,           # 第5步：仲裁决策
        ],
        termination_condition=termination,
    )
    
    # 使用默认任务或自定义任务
    if task_input is None:
        task_input = """
【无人机任务分配问题】

## 可用无人机资源：
1. **UAV-001**：侦察型，续航120分钟，最大速度80km/h，当前位置A基地，电量100%
2. **UAV-002**：运输型，续航90分钟，载重5kg，最大速度60km/h，当前位置A基地，电量85%
3. **UAV-003**：侦察型，续航100分钟，最大速度70km/h，当前位置B基地，电量90%
4. **UAV-004**：多用途，续航80分钟，载重2kg，最大速度65km/h，当前位置A基地，电量95%

## 待分配任务：
1. **T1-区域侦察**：对C区域进行侦察，预计需要30分钟，优先级：高，时间窗口：08:00-10:00
2. **T2-物资运输**：从A基地运输医疗物资(3kg)到D点，优先级：高，时间窗口：08:30-09:30
3. **T3-目标监控**：对E点目标持续监控60分钟，优先级：中，时间窗口：09:00-12:00
4. **T4-紧急侦察**：对F区域紧急侦察，预计20分钟，优先级：紧急，时间窗口：08:00-08:30
5. **T5-设备投送**：向G点投送通信设备(1kg)，优先级：低，时间窗口：10:00-12:00

## 约束条件：
- D区域为临时禁飞区（09:00-09:30）
- 每架无人机同一时间只能执行一个任务
- 任务完成后无人机需返回最近基地
- 无人机从基地到各任务点的飞行时间约10-15分钟

## 要求：
请团队协作分析并生成最优的任务分配方案，输出标准JSON格式。
"""
    
    print("📋 任务描述：")
    print(task_input)
    print()
    print("🚀 启动多智能体协作...")
    print("=" * 70)
    print()
    
    # 执行团队协作
    result = await Console(team_chat.run_stream(task=task_input))
    
    print()
    print("=" * 70)
    print("✅ 团队协作完成！")
    print("=" * 70)
    
    return result

def extract_json_from_result(result):
    """从协作结果中提取JSON分配方案"""
    try:
        # 遍历所有消息，查找JSON内容
        for message in result.messages:
            content = message.content
            if "final_allocation" in content:
                # 尝试提取JSON
                import re
                json_match = re.search(r'\{[\s\S]*"final_allocation"[\s\S]*\}', content)
                if json_match:
                    json_str = json_match.group(0)
                    allocation = json.loads(json_str)
                    return allocation
        return None
    except Exception as e:
        print(f"⚠️ JSON提取失败: {e}")
        return None

def save_allocation_result(result, output_file="output_allocation.json"):
    """保存分配结果到JSON文件"""
    try:
        allocation = extract_json_from_result(result)
        if allocation:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(allocation, f, ensure_ascii=False, indent=2)
            print(f"\n💾 分配方案已保存到: {output_file}")
            return True
        else:
            print("\n⚠️ 未能提取到有效的JSON分配方案")
            # 保存原始对话记录
            with open("output_conversation.txt", "w", encoding="utf-8") as f:
                for msg in result.messages:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"发言者: {msg.source}\n")
                    f.write(f"内容: {msg.content}\n")
            print("💾 对话记录已保存到: output_conversation.txt")
            return False
    except Exception as e:
        print(f"\n❌ 保存失败: {e}")
        return False

# 主程序入口
if __name__ == "__main__":
    try:
        print()
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║     AutoGen 多无人机任务分配系统 - 多智能体协作框架             ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print()
        
        # 运行异步协作流程
        result = asyncio.run(run_uav_allocation_team())
        
        print()
        print("📊 协作统计：")
        print(f"   • 对话轮数: {len(result.messages)} 条消息")
        print(f"   • 参与智能体: 5个（任务分析、资源评估、方案生成、冲突检测、仲裁）")
        print(f"   • 任务状态: 协作完成")
        
        # 保存结果
        save_allocation_result(result)
        
        print()
        print("✨ 系统运行完成！")
        print()
        
    except ValueError as e:
        print(f"❌ 配置错误：{e}")
        print("请检查 .env 文件中的配置是否正确")
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
