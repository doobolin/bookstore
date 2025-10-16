@echo off
chcp 65001 >nul
echo ========================================
echo 启动后端服务
echo ========================================
echo.

cd /d "%~dp0"

echo [检查] Python 环境...
python --version
echo.

echo [检查] 必要的依赖...
python -c "import flask; import flask_cors; import pymysql; print('所有依赖已安装')"
if %errorlevel% neq 0 (
    echo [错误] 缺少依赖，正在安装...
    pip install -r requirements.txt
)
echo.

echo [信息] 后端服务配置:
echo - 地址: http://localhost:5000
echo - API路径: http://localhost:5000/api
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.
echo ========================================
echo 正在启动...
echo ========================================
echo.

python app.py

pause
