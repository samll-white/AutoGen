@echo off
chcp 65001 > nul
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║        AutoGen vs 贪心算法 - 对比实验启动脚本                   ║
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

echo 步骤 2/3: 运行对比实验
echo ══════════════════════════════════════════════════════════════════
echo.

python run_comparison.py

echo.
echo ══════════════════════════════════════════════════════════════════
echo ✨ 对比实验完成！
echo ══════════════════════════════════════════════════════════════════
echo.
echo 📊 查看结果:
echo    • comparison_results\ (对比数据)
echo    • comparison_visualizations\ (可视化图表)
echo.
pause
