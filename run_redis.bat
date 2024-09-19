@echo off
setlocal

REM 设置错误处理
set ERRORS=0

REM 设置 Redis 服务器的下载链接
set REDIS_URL=https://ghp.ci/https://github.com/xcgx/flask-celery-example/blob/main/redis-server.exe

REM 检查并下载 Redis 服务器
if not exist redis-server.exe (
    echo Downloading Redis server...
    powershell -Command "Invoke-WebRequest -Uri %REDIS_URL% -OutFile redis-server.exe"
    if %errorlevel% neq 0 (
        echo Error: Failed to download Redis server!
        set ERRORS=1
        goto :end
    )
)

REM 启动 Redis 服务器
echo Starting Redis server...
start "" cmd /c redis-server.exe

REM 等待 Redis 服务器启动
timeout /t 2 >nul

REM 检查 Redis 服务器是否启动成功
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo Redis server started successfully
) else (
    echo Error: Failed to start Redis server!
    set ERRORS=1
)

:end
if %ERRORS% neq 0 (
    echo There were errors during the execution. Please check the messages above.
)

endlocal
pause
