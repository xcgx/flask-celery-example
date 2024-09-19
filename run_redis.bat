@echo off
setlocal

REM 设置错误处理
set ERRORS=0

REM 检查并下载 Redis
if not exist redis-stable (
    echo Downloading Redis...
    powershell -Command "Invoke-WebRequest -Uri https://github.com/xcgx/flask-celery-example/blob/main/redis-windows-7.4.0.zip -OutFile redis-stable.zip"
    if %errorlevel% neq 0 (
        echo Error: Failed to download Redis!
        set ERRORS=1
        goto :end
    )
    echo Extracting Redis...
    powershell -Command "Expand-Archive -Path redis-stable.zip -DestinationPath ."
    if %errorlevel% neq 0 (
        echo Error: Failed to extract Redis!
        set ERRORS=1
        goto :end
    )
    del redis-stable.zip
)

REM 进入 Redis 目录
cd redis-6.2.6

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
