@echo off
REM 注册功能环境设置和启动脚本 - Windows版本
REM 用于快速设置和启动注册功能所需的环境

echo ========================================
echo 注册功能环境设置和启动
echo ========================================
echo.

REM 检查Python是否安装
echo [1/5] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python已安装
echo.

REM 进入后端目录
echo [2/5] 进入后端目录...
cd /d "%~dp0backend"
if %errorlevel% neq 0 (
    echo ❌ 错误: 无法进入backend目录
    pause
    exit /b 1
)
echo ✅ 已进入backend目录
echo.

REM 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo [3/5] 激活虚拟环境...
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo [3/5] 跳过虚拟环境激活（未找到venv）
)
echo.

REM 安装依赖
echo [4/5] 安装Python依赖（包括flask-cors）...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 错误: 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装成功
echo.

REM 检查数据库配置
echo [5/5] 检查数据库配置...
if exist ".env" (
    echo ✅ 找到.env配置文件
    echo.
    echo 📋 当前数据库配置：
    type .env | findstr "DB_"
) else (
    echo ⚠️ 警告: 未找到.env文件
    echo 请创建.env文件并配置数据库连接信息
    echo.
    echo 示例配置：
    echo DB_HOST=localhost
    echo DB_PORT=3306
    echo DB_USERNAME=root
    echo DB_PASSWORD=your_password
    echo DB_NAME=bookstore_management_system
    echo SECRET_KEY=your-secret-key
)
echo.

echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 现在您可以：
echo.
echo 1. 启动后端服务:
echo    python app.py
echo.
echo 2. 测试注册API:
echo    python test_register.py
echo.
echo 3. 在另一个终端启动前端:
echo    cd ..\线上图书系统
echo    npm run dev
echo.
echo 按任意键继续...
pause >nul

REM 询问是否立即启动后端
echo.
echo ========================================
set /p start_backend="是否立即启动后端服务？(Y/N): "
if /i "%start_backend%"=="Y" (
    echo.
    echo 正在启动后端服务...
    echo 按 Ctrl+C 可以停止服务
    echo.
    python app.py
)

pause
