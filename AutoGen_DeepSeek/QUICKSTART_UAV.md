# 🚁 无人机任务分配系统 - 快速开始

## ⚡ 5分钟快速启动

### 步骤1️⃣：检查依赖

```bash
python check_dependencies.py
```

如果缺少依赖：
```bash
pip install -r requirements.txt
```

---

### 步骤2️⃣：配置API

创建 `.env` 文件（参考 `env_config_template.txt`）：

```bash
# 使用智谱AI（推荐，国内免费额度）
LLM_MODEL_ID=glm-4
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

**获取API密钥**：
- 智谱AI: https://open.bigmodel.cn/ （推荐）
- 通义千问: https://dashscope.aliyun.com/
- DeepSeek: https://platform.deepseek.com/

---

### 步骤3️⃣：运行系统

**Windows用户**：
```bash
run_uav_demo.bat
```

**或直接运行Python**：
```bash
python autogen_uav_allocation.py
```

---

### 步骤4️⃣：查看结果

程序运行后会生成：

- **output_allocation.json** - 最终分配方案
- **output_conversation.txt** - 完整对话记录

---

## 📋 默认任务场景

系统内置了一个示例场景：

**4架无人机**：
- UAV-001: 侦察型，速度80km/h
- UAV-002: 运输型，载重5kg
- UAV-003: 侦察型，位于B基地
- UAV-004: 多用途

**5个任务**：
- T4: 紧急侦察（08:00-08:30）⚡
- T1: 区域侦察（08:00-10:00）
- T2: 物资运输（08:30-09:30）
- T3: 目标监控（09:00-12:00）
- T5: 设备投送（10:00-12:00）

**约束条件**：
- D区域禁飞（09:00-09:30）
- 每架无人机同时只能执行一个任务

---

## 🤖 五个智能体协作流程

```
1️⃣ TaskAnalyzer（任务分析）
   └─> 解析5个任务，识别优先级和约束
   
2️⃣ ResourceEvaluator（资源评估）
   └─> 评估4架无人机的能力和状态
   
3️⃣ SolutionGenerator（方案生成）
   └─> 提出候选分配方案
   
4️⃣ ConflictDetector（冲突检测）
   └─> 检查时间/空间/能力冲突
   
5️⃣ Arbitrator（仲裁决策）
   └─> 输出最终JSON方案 + TERMINATE
```

---

## 📊 预期输出示例

```json
{
  "final_allocation": {
    "assignments": [
      {
        "task_id": "T4",
        "task_name": "紧急侦察",
        "assigned_uav": "UAV-001",
        "start_time": "08:00",
        "priority": "紧急"
      },
      {
        "task_id": "T2",
        "task_name": "物资运输",
        "assigned_uav": "UAV-002",
        "start_time": "08:30",
        "priority": "高"
      }
    ],
    "total_completion_time": "12:30",
    "risk_assessment": "整体风险可控"
  }
}
```

---

## 🎨 自定义任务

### 方法1：修改代码中的默认任务

编辑 `autogen_uav_allocation.py` 第308行的 `task_input` 变量。

### 方法2：参考JSON示例

查看 `uav_task_example.json` 了解标准格式。

---

## 🔧 常见问题

### ❓ 程序运行很慢？

**原因**：智能体在深度讨论

**正常**：通常需要2-5分钟完成（取决于模型速度）

---

### ❓ 没有输出JSON文件？

**检查**：
1. 查看 `output_conversation.txt` 是否有内容
2. 检查最后一条消息是否包含 "TERMINATE"
3. 查看终端输出是否有错误信息

**解决**：
- 增加对话轮数（修改 `MaxMessageTermination(20)` 为更大值）
- 使用更强的模型（如 gpt-4o）

---

### ❓ API调用失败？

**检查**：
1. `.env` 文件是否存在且配置正确
2. API Key是否有效
3. 账户是否有余额/额度

**测试API**：
```python
import os
from dotenv import load_dotenv
load_dotenv()
print(f"Model: {os.getenv('LLM_MODEL_ID')}")
print(f"API Key: {os.getenv('LLM_API_KEY')[:10]}...")
```

---

## 📚 进阶使用

### 查看完整文档
```bash
# 详细使用说明
README_UAV.md

# API配置指南
API_CONFIG_GUIDE.md
```

### 对比两个案例
```bash
# 软件开发团队
python autogen_software_team.py

# 无人机任务分配
python autogen_uav_allocation.py
```

---

## 💡 核心优势

✅ **5个专业智能体协作** - 分工明确，各司其职  
✅ **自动冲突检测** - 识别时间/空间/资源冲突  
✅ **投票决策机制** - 基于多方意见的民主决策  
✅ **轮数控制** - 最多20轮，避免无限讨论  
✅ **标准JSON输出** - 便于系统对接  

---

## 🎯 适用场景

- 🚁 多无人机任务调度
- 🤖 多机器人协作
- 🚗 车辆路径规划
- 📦 物流配送优化
- 🏭 生产任务分配

---

## 📞 获取帮助

遇到问题？
1. 查看 `README_UAV.md` 完整文档
2. 检查 `API_CONFIG_GUIDE.md` 配置说明
3. 查看终端错误信息
4. 检查 `output_conversation.txt` 对话记录

---

**祝你使用愉快！🎉**
