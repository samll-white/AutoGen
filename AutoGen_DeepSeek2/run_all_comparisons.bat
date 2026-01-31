@echo off
chcp 65001 > nul
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║       AutoGen vs 所有基线算法 - 对比实验启动脚本                ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo 步骤 1/3: 检查AutoGen结果文件
echo ══════════════════════════════════════════════════════════════════
echo.

if not exist "output_allocation.json" (
    echo ❌ 未找到 AutoGen 结果文件: output_allocation.json
    echo.
    echo 请先运行 AutoGen 算法:
    echo    python autogen_uav_allocation.py
    echo.
    echo 或双击运行:
    echo    run_uav_demo.bat
    echo.
    pause
    exit /b 1
)

echo ✅ 找到 AutoGen 结果文件
echo.

echo 步骤 2/3: 运行所有算法对比实验
echo ══════════════════════════════════════════════════════════════════
echo.
echo 对比算法:
echo   1️⃣ AutoGen - 多智能体协作
echo   2️⃣ 贪心算法 - 按优先级依次分配
echo   3️⃣ 随机分配 - 随机选择分配
echo   4️⃣ 遗传算法 - 进化搜索优化
echo   5️⃣ 整数规划 - 数学优化求解
echo.

python run_all_comparisons.py

echo.
echo ══════════════════════════════════════════════════════════════════
echo ✨ 所有对比实验完成！
echo ══════════════════════════════════════════════════════════════════
echo.
echo 📊 查看结果:
echo    • comparison_results\ (对比数据和LaTeX表格)
echo    • comparison_visualizations\ (6张可视化图表)
echo.
pause
