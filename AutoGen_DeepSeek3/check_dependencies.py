"""
依赖包检查脚本
检查AutoGen项目所需的所有Python包是否已安装
"""

import sys

def check_package(package_name, import_name=None):
    """
    检查单个包是否已安装
    
    Args:
        package_name: 包的显示名称
        import_name: 实际导入的模块名（如果与包名不同）
    """
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name:<30} - 已安装")
        return True
    except ImportError as e:
        print(f"❌ {package_name:<30} - 未安装")
        print(f"   错误详情: {e}")
        return False

def check_specific_import(description, import_statement):
    """
    检查特定的导入语句是否能成功执行
    
    Args:
        description: 检查项描述
        import_statement: 导入语句
    """
    try:
        exec(import_statement)
        print(f"✅ {description:<30} - 可用")
        return True
    except Exception as e:
        print(f"❌ {description:<30} - 失败")
        print(f"   错误详情: {e}")
        return False

def main():
    print("=" * 70)
    print("🔍 AutoGen 项目依赖包检查")
    print("=" * 70)
    print()
    
    results = []
    
    # 基础依赖
    print("📦 基础依赖包:")
    print("-" * 70)
    results.append(check_package("python-dotenv", "dotenv"))
    results.append(check_package("requests"))
    results.append(check_package("asyncio"))
    print()
    
    # OpenAI 相关
    print("🤖 OpenAI 相关:")
    print("-" * 70)
    results.append(check_package("openai"))
    print()
    
    # AutoGen 核心包
    print("🚀 AutoGen 核心包:")
    print("-" * 70)
    results.append(check_package("autogen-agentchat", "autogen_agentchat"))
    results.append(check_package("autogen-ext", "autogen_ext"))
    print()
    
    # AutoGen 特定模块检查
    print("🔧 AutoGen 关键模块:")
    print("-" * 70)
    results.append(check_specific_import(
        "OpenAI 模型客户端",
        "from autogen_ext.models.openai import OpenAIChatCompletionClient"
    ))
    results.append(check_specific_import(
        "智能体 (AssistantAgent)",
        "from autogen_agentchat.agents import AssistantAgent"
    ))
    results.append(check_specific_import(
        "智能体 (UserProxyAgent)",
        "from autogen_agentchat.agents import UserProxyAgent"
    ))
    results.append(check_specific_import(
        "团队聊天 (RoundRobinGroupChat)",
        "from autogen_agentchat.teams import RoundRobinGroupChat"
    ))
    results.append(check_specific_import(
        "终止条件",
        "from autogen_agentchat.conditions import TextMentionTermination"
    ))
    results.append(check_specific_import(
        "UI控制台",
        "from autogen_agentchat.ui import Console"
    ))
    print()
    
    # Streamlit 相关（用于 output.py）
    print("🌐 Web应用相关 (用于output.py):")
    print("-" * 70)
    results.append(check_package("streamlit"))
    print()
    
    # 可选依赖
    print("📊 可选依赖包:")
    print("-" * 70)
    results.append(check_package("pandas"))
    results.append(check_package("plotly"))
    print()
    
    # 统计结果
    print("=" * 70)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"📊 检查结果统计:")
    print(f"   总计: {total} 项")
    print(f"   ✅ 通过: {passed} 项")
    print(f"   ❌ 失败: {failed} 项")
    print("=" * 70)
    print()
    
    # 给出建议
    if failed == 0:
        print("🎉 恭喜！所有依赖包都已正确安装！")
        print("✨ 你可以运行以下命令启动程序:")
        print("   python autogen_software_team.py")
    else:
        print("⚠️  发现缺失的依赖包！")
        print()
        print("📝 安装建议:")
        print()
        
        # 检查核心AutoGen包
        if not results[4] or not results[5]:  # autogen-agentchat 或 autogen-ext
            print("1️⃣ 安装 AutoGen 核心包:")
            print("   pip install autogen-agentchat autogen-ext")
            print()
        
        # 检查OpenAI
        if not results[3]:  # openai
            print("2️⃣ 安装 OpenAI SDK:")
            print("   pip install openai")
            print()
        
        # 检查基础包
        if not results[0]:  # python-dotenv
            print("3️⃣ 安装 python-dotenv:")
            print("   pip install python-dotenv")
            print()
        
        # 检查Streamlit
        if not results[-3]:  # streamlit
            print("4️⃣ 安装 Streamlit (用于output.py):")
            print("   pip install streamlit")
            print()
        
        print("💡 或者一次性安装所有依赖:")
        print("   pip install -r requirements.txt")
    
    print()
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
