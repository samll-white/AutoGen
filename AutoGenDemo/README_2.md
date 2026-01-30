# AutoGen 多智能体协作案例集

本目录包含 AutoGen 框架的完整实战案例，展示了如何使用 AutoGen 构建多智能体协作系统。

## 📁 项目列表

### 1️⃣ 软件开发团队协作案例
- `autogen_software_team.py` - 软件开发团队主程序
- `output.py` - 团队协作生成的比特币价格应用示例

### 2️⃣ 多无人机任务分配系统 🚁 **NEW**
- `autogen_uav_allocation.py` - 无人机任务分配主程序
- `uav_task_example.json` - 任务输入示例
- `README_UAV.md` - 详细使用文档

### 📚 公共文件
- `requirements.txt` - 依赖包列表
- `README.md` - 本说明文档
- `API_CONFIG_GUIDE.md` - API配置指南
- `check_dependencies.py` - 依赖检查工具

## 🚀 两个案例对比

| 维度 | 软件开发团队 | 无人机任务分配 |
|-----|------------|--------------|
| **应用场景** | 软件工程 | 任务调度 |
| **智能体数量** | 4个 | 5个 |
| **协作模式** | 需求→开发→审查→测试 | 分析→评估→生成→检测→仲裁 |
| **输出结果** | Python代码 | JSON分配方案 |
| **终止方式** | 用户测试完成 | 投票决策 |
| **对话轮数** | 最多20轮 | 最多20轮(3-4轮循环) |
| **核心特点** | 代码生成与审查 | 冲突检测与投票 |

### 案例1：软件开发团队 💻

- **多智能体协作**：演示产品经理、工程师、代码审查员、用户代理的完整协作流程
- **真实开发场景**：从需求分析到代码实现的完整软件开发生命周期
- **自动化流程**：智能体间自动传递任务，无需人工干预
- **代码生成与审查**：自动生成可运行的代码并进行质量审查

### 案例2：无人机任务分配 🚁 **NEW**

- **五角色协作**：任务分析、资源评估、方案生成、冲突检测、仲裁决策
- **智能冲突检测**：自动识别时间、空间、资源冲突
- **投票决策机制**：基于多方意见的民主决策
- **JSON标准输出**：便于系统对接和后续处理
- **轮数控制**：合理设置对话轮数，避免无限讨论

## 🛠️ 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并配置以下参数：

```bash
# LLM 配置
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_ID=gpt-4
```

### 3. 验证环境

确保可以正常调用 LLM API：

```python
import os
from dotenv import load_dotenv
load_dotenv()

print(f"API Key: {os.getenv('LLM_API_KEY')[:10]}...")
print(f"Base URL: {os.getenv('LLM_BASE_URL')}")
print(f"Model: {os.getenv('LLM_MODEL_ID')}")
```

## 🎯 运行案例

### 案例1：启动软件开发团队协作

```bash
python autogen_software_team.py
```

### 案例2：启动无人机任务分配系统 🚁

```bash
python autogen_uav_allocation.py
```

> 📖 详细使用说明请查看 `README_UAV.md`

### 预期输出流程

1. **🔧 模型客户端初始化**
2. **👥 智能体团队创建**
3. **🚀 团队协作启动**
4. **💬 智能体对话过程**：
   - ProductManager：需求分析和技术规划
   - Engineer：代码实现
   - CodeReviewer：代码审查和优化建议
   - UserProxy：用户测试和反馈
5. **✅ 协作完成**

## 👥 智能体角色说明

### 🎯 ProductManager（产品经理）
- **职责**：需求分析、技术规划、风险评估
- **输出**：功能模块划分、技术选型建议、验收标准
- **特点**：注重用户体验和产品可行性

### 💻 Engineer（软件工程师）
- **职责**：代码实现、技术方案设计
- **输出**：完整的可运行代码
- **特点**：精通 Python、Streamlit、API 集成

### 🔍 CodeReviewer（代码审查员）
- **职责**：代码质量检查、安全性审查
- **输出**：代码审查报告、优化建议
- **特点**：关注代码规范、性能和安全性

### 👤 UserProxy（用户代理）
- **职责**：代表用户需求、执行测试、提供反馈
- **输出**：测试结果、用户反馈
- **特点**：从用户角度验证功能

## 📊 案例演示：比特币价格应用

### 应用功能
- ✅ 实时显示比特币当前价格（USD）
- ✅ 显示24小时价格变化趋势
- ✅ 提供价格刷新功能
- ✅ 错误处理和加载状态
- ✅ 简洁美观的 Streamlit 界面

### 技术栈
- **前端框架**：Streamlit
- **数据源**：CoinGecko API
- **编程语言**：Python
- **HTTP 请求**：requests

### 运行生成的应用

```bash
streamlit run output.py
```

## 🔧 自定义配置

### 修改智能体角色

可以通过修改 `system_message` 来自定义智能体的行为：

```python
def create_product_manager(model_client):
    system_message = """
    你是一位经验丰富的产品经理...
    # 在这里自定义角色描述
    """
    return AssistantAgent(
        name="ProductManager",
        model_client=model_client,
        system_message=system_message,
    )
```

### 调整协作流程

可以修改参与者列表和终止条件：

```python
team_chat = RoundRobinGroupChat(
    participants=[
        product_manager,
        engineer, 
        code_reviewer,
        user_proxy
    ],
    termination_condition=TextMentionTermination("TERMINATE"),
    max_turns=20,  # 调整最大轮次
)
```

## 🐛 常见问题

### Q: 智能体没有开始对话？
A: 检查以下几点：
- 确认 API Key 配置正确
- 检查网络连接
- 验证模型名称是否正确

### Q: 协作过程中断？
A: 可能原因：
- API 调用限制
- 网络超时
- 模型响应异常

### Q: 生成的代码无法运行？
A: 建议：
- 检查依赖包是否完整安装
- 验证 API 接口是否可用
- 查看错误日志进行调试

## 📚 扩展学习

### 相关章节
- 第四章：智能体经典范式构建
- 第七章：构建你的Agent框架
- 第十二章：多智能体协作与通信

### 进阶实践
- 尝试添加更多智能体角色（如测试工程师、UI设计师）
- 实现更复杂的应用场景
- 集成更多的工具和API
- 优化智能体间的协作策略

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个案例：
- 报告 Bug 或问题
- 提出新的功能建议
- 分享你的实践经验
- 优化代码实现

---

*本案例是 Hello-Agents 教程的一部分，更多内容请参考项目主页。*




