@echo off
chcp 65001 > nul
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║     AutoGen 多无人机任务分配系统 - 快速启动脚本                 ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo 正在检查依赖...
python check_dependencies.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ 依赖检查失败，请先安装依赖包
    echo 运行命令: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ✅ 依赖检查通过
echo.
echo 正在启动无人机任务分配系统...
echo ═══════════════════════════════════════════════════════════════════
echo.

python autogen_uav_allocation.py

echo.
echo ═══════════════════════════════════════════════════════════════════
echo 程序运行结束
echo.
pause
