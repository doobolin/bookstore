@echo off
chcp 65001 >nul
echo ========================================
echo 后端服务快速启动指南
echo ========================================
echo.
echo [完成] flask-cors 已成功安装！
echo.
echo 现在您可以通过以下方式启动后端：
echo.
echo ----------------------------------------
echo 方式 1: 使用启动脚本 (推荐)
echo ----------------------------------------
echo.
echo    双击运行: start_backend.bat
echo.
echo    或在命令行执行:
echo    cd D:\AAA\backend
echo    start_backend.bat
echo.
echo ----------------------------------------
echo 方式 2: 直接运行 Python
echo ----------------------------------------
echo.
echo    cd D:\AAA\backend
echo    python app.py
echo.
echo ========================================
echo 下一步操作
echo ========================================
echo.
echo 1. 启动后端服务（上面任选一种方式）
echo.
echo 2. 打开新终端，启动前端服务:
echo    cd D:\AAA\线上图书系统
echo    npm run dev
echo.
echo 3. 测试注册功能:
echo    - 浏览器访问: http://localhost:5173/register
echo    - 或运行测试脚本: python test_register.py
echo.
echo ========================================
set /p start="是否立即启动后端服务? (Y/N): "
if /i "%start%"=="Y" (
    echo.
    echo 正在启动后端服务...
    call start_backend.bat
) else (
    echo.
    echo 您可以随时运行 start_backend.bat 启动服务
)

pause
