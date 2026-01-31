# AutoGen 多无人机任务分配系统

基于 AutoGen 框架的多智能体协作无人机任务智能分配系统

---

## 📖 项目简介

本项目将 **AutoGen 多智能体框架**应用于**无人机任务分配**场景，通过5个专业智能体的协作讨论，自动生成最优的任务分配方案。

### 核心特点

- ✅ **多智能体协作**：5个专业Agent分工明确、协同工作
- ✅ **智能冲突检测**：自动识别时间、空间、资源冲突
- ✅ **投票决策机制**：基于多方意见的民主决策
- ✅ **JSON标准输出**：便于系统对接和后续处理
- ✅ **轮数控制**：合理设置对话轮数，避免无限讨论

---

## 🤖 智能体团队

### 1. TaskAnalyzer（任务分析Agent）
**角色定位**：任务需求专家

**核心职责**：
- 解析输入的任务列表和约束条件
- 识别任务类型、优先级、时间窗口
- 提取关键约束（禁飞区、时间限制等）
- 对任务进行分类和排序

**输出示例**：
```
任务总数: 5个
- 紧急任务: 1个（T4-紧急侦察）
- 高优先级: 2个（T1-区域侦察, T2-物资运输）
- 中优先级: 1个（T3-目标监控）
- 低优先级: 1个（T5-设备投送）

关键约束:
- D区域禁飞（09:00-09:30）
- 所有任务需在时间窗口内完成
```

---

### 2. ResourceEvaluator（资源评估Agent）
**角色定位**：无人机能力专家

**核心职责**：
- 评估每架无人机的飞行能力（续航、速度、载重）
- 检查无人机当前状态（位置、电量）
- 分析无人机与任务类型的匹配度
- 识别资源瓶颈和限制

**输出示例**：
```
无人机能力评估:
- UAV-001: 侦察专家，速度最快(80km/h)，适合紧急任务
- UAV-002: 运输专家，载重最大(5kg)，适合物资运输
- UAV-003: 侦察型，位于B基地，适合附近区域任务
- UAV-004: 多用途，续航较短，适合短时任务

能力瓶颈: 运输能力有限（仅2架可运输）
```

---

### 3. SolutionGenerator（方案生成Agent）
**角色定位**：方案设计专家

**核心职责**：
- 基于任务分析和资源评估生成分配方案
- 考虑多目标优化（效率、成本、风险）
- 提供1-2个候选方案
- 说明每个方案的优缺点

**输出示例**：
```
【方案A - 优先级优先策略】
T4(紧急) → UAV-001 (08:00-08:20, 最快响应)
T1(高)   → UAV-003 (08:15-08:45, B基地最近)
T2(高)   → UAV-002 (08:30-09:10, 载重足够)
T3(中)   → UAV-004 (09:00-10:00, 多用途)
T5(低)   → UAV-002 (10:00-10:30, T2完成后)

优势: 所有高优先级任务都能及时完成
风险: UAV-002连续作业，电量可能紧张
```

---

### 4. ConflictDetector（冲突检测Agent）
**角色定位**：质量保证专家

**核心职责**：
- 检测时间冲突（同一无人机的任务时间重叠）
- 检测空间冲突（禁飞区、航线碰撞）
- 验证能力匹配（载重、续航是否满足）
- 识别约束违反

**输出示例**：
```
冲突检测结果:

✅ 时间冲突: 无
✅ 空间冲突: 无（T2在08:30开始，避开D区禁飞时段）
✅ 能力匹配: 通过
⚠️  潜在风险: UAV-002电量85%，连续执行两任务可能紧张

建议: 为T5准备备选无人机(UAV-004)
```

---

### 5. Arbitrator（仲裁Agent）
**角色定位**：最终决策者

**核心职责**：
- 汇总所有Agent的分析和建议
- 综合评估候选方案
- 做出最终决策
- 输出标准化JSON方案

**输出示例**：
```json
{
  "final_allocation": {
    "decision_time": "2024-01-23 10:30:00",
    "total_tasks": 5,
    "assignments": [
      {
        "task_id": "T4",
        "assigned_uav": "UAV-001",
        "start_time": "08:00",
        "priority": "紧急"
      },
      ...
    ],
    "risk_assessment": "整体风险可控，建议监控UAV-002电量"
  }
}
```

---

## 🔄 协作流程

```
用户输入任务需求
       ↓
┌─────────────────────────────────────────┐
│  第1轮（初始分析）                       │
├─────────────────────────────────────────┤
│  TaskAnalyzer      → 解析任务           │
│  ResourceEvaluator → 评估资源           │
│  SolutionGenerator → 生成初始方案       │
│  ConflictDetector  → 检测问题           │
│  Arbitrator        → 初步评估           │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│  第2轮（方案优化）[如有冲突]             │
├─────────────────────────────────────────┤
│  SolutionGenerator → 修改方案           │
│  ConflictDetector  → 再次检测           │
│  Arbitrator        → 综合判断           │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│  第3轮（最终决策）                       │
├─────────────────────────────────────────┤
│  Arbitrator → 输出最终JSON方案          │
│            → 说"TERMINATE"              │
└─────────────────────────────────────────┘
       ↓
   JSON方案输出
```

---

## 🚀 快速开始

### 1. 环境准备

确保已安装依赖包：

```bash
pip install -r requirements.txt
```

### 2. 配置 API

创建 `.env` 文件：

```bash
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_ID=gpt-4o
```

> 💡 支持多种API提供商，详见 `API_CONFIG_GUIDE.md`

### 3. 运行程序

```bash
python autogen_uav_allocation.py
```

### 4. 查看结果

程序会生成两个输出文件：

- `output_allocation.json` - 最终分配方案（JSON格式）
- `output_conversation.txt` - 完整对话记录（如果JSON提取失败）

---

## 📝 输入示例

### 方式1：使用默认示例

直接运行程序，使用内置的示例任务。

### 方式2：使用JSON文件

参考 `uav_task_example.json` 格式：

```json
{
  "available_uavs": [
    {
      "uav_id": "UAV-001",
      "type": "侦察型",
      "capabilities": {
        "max_flight_time": 120,
        "max_speed_kmh": 80
      },
      "current_status": {
        "location": "A基地",
        "battery_percent": 100
      }
    }
  ],
  "tasks": [
    {
      "task_id": "T1",
      "task_name": "区域侦察",
      "priority": "高",
      "time_window": {
        "start": "08:00",
        "end": "10:00"
      }
    }
  ]
}
```

### 方式3：自定义文本描述

修改 `autogen_uav_allocation.py` 中的 `task_input` 变量。

---

## 📊 输出格式

### JSON方案结构

```json
{
  "final_allocation": {
    "decision_time": "决策时间",
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
        "rationale": "速度最快，适合紧急任务"
      }
    ],
    "unassigned_tasks": [],
    "total_completion_time": "12:30",
    "risk_assessment": "风险评估说明",
    "notes": "其他重要说明"
  }
}
```

---

## ⚙️ 高级配置

### 调整对话轮数

在 `autogen_uav_allocation.py` 中修改：

```python
# 最大20轮对话（约3-4轮完整讨论）
termination = MaxMessageTermination(20) | TextMentionTermination("TERMINATE")
```

### 切换协作模式

```python
# 方式1: 轮询模式（当前使用）
from autogen_agentchat.teams import RoundRobinGroupChat
team_chat = RoundRobinGroupChat(participants=[...])

# 方式2: 选择器模式（更灵活）
from autogen_agentchat.teams import SelectorGroupChat
team_chat = SelectorGroupChat(
    participants=[...],
    model_client=model_client  # LLM动态选择下一个发言者
)
```

### 自定义智能体角色

修改 `create_xxx(model_client)` 函数中的 `system_message`。

---

## 🧪 测试场景

### 场景1：资源不足

```
5个任务，但只有3架无人机可用
预期: 高优先级任务优先分配，低优先级任务可能未分配
```

### 场景2：时间冲突

```
多个任务时间窗口重叠
预期: 冲突检测Agent发现问题，要求重新规划
```

### 场景3：能力不匹配

```
运输任务需要5kg载重，但所有无人机最大载重2kg
预期: 资源评估Agent指出瓶颈，方案生成Agent标记为无法分配
```

---

## 🐛 常见问题

### Q1: 智能体没有输出JSON？

**原因**：模型能力不足或prompt不够清晰

**解决**：
- 使用更强的模型（如 gpt-4o）
- 在Arbitrator的prompt中强调JSON格式要求

### Q2: 对话超过20轮还没结束？

**原因**：冲突检测Agent和方案生成Agent反复修改

**解决**：
- 增加 `max_turns` 值
- 简化任务场景
- 优化冲突检测的严格程度

### Q3: 生成的方案不合理？

**原因**：智能体之间缺乏充分讨论

**解决**：
- 增加对话轮数
- 在每个Agent的prompt中强调关键检查点
- 使用 SelectorGroupChat 让讨论更灵活

---

## 🎯 扩展方向

### 1. 添加更多智能体

- **PathPlanningAgent**：负责航线规划和避障
- **WeatherAgent**：评估天气对任务的影响
- **CostOptimizationAgent**：优化成本和能耗

### 2. 集成实时数据

```python
# 从真实无人机系统获取数据
def get_real_uav_status():
    # 调用无人机API
    pass
```

### 3. 可视化界面

- 使用 Streamlit 创建交互式界面
- 地图可视化任务分配
- 实时显示无人机状态

### 4. 强化学习优化

- 基于历史分配结果训练优化模型
- 学习最优分配策略

---

## 📚 相关资源

- [AutoGen 官方文档](https://microsoft.github.io/autogen/)
- [原软件团队案例](./autogen_software_team.py)
- [API配置指南](./API_CONFIG_GUIDE.md)

---

## 🤝 五个智能体设计

1️⃣ TaskAnalyzer（任务分析Agent）
   └─> 解析任务、识别优先级和约束

2️⃣ ResourceEvaluator（资源评估Agent）
   └─> 评估无人机能力和状态

3️⃣ SolutionGenerator（方案生成Agent）
   └─> 生成候选分配方案

4️⃣ ConflictDetector（冲突检测Agent）⭐ 核心创新
   └─> 检测时间/空间/资源冲突

5️⃣ Arbitrator（仲裁Agent）
   └─> 投票决策，输出JSON方案

## 🤝 协作流程（最多20轮）

输入任务 
  ↓
第1轮：初始分析 → 生成方案 → 检测冲突
  ↓
[有冲突？]
  ↓ 是
第2轮：修改方案 → 再次检测
  ↓ 否
第3轮：最终决策 → 输出JSON
  ↓
TERMINATE

## 🤝 使用场景

这个框架可以应用于：
🚁 多无人机/多机器人任务调度
🚗 车辆路径规划
📦 物流配送优化
🏭 生产任务分配
👥 团队人员排班
💾 云资源调度