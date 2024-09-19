import subprocess
import sys
import platform
import logging
import os

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_celery_worker():
    """启动 Celery worker"""
    python_executable = sys.executable
    system = platform.system()

    if system == "Windows":
        command = [python_executable, '-m', 'celery', '-A', 'app.celery', 'worker', '--loglevel=info', '-P', 'eventlet']
    elif system == "Linux":
        command = [python_executable, '-m', 'celery', '-A', 'app.celery', 'worker', '--loglevel=info', '-P', 'eventlet']
    else:
        raise RuntimeError("Unsupported operating system")

    logger.info(f"启动 Celery worker，使用命令: {' '.join(command)}")

    # 启动 Celery worker 并捕获输出
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    def stream_output(pipe, log_func):
        """持续打印子进程的输出"""
        for line in iter(pipe.readline, ''):
            if line:
                log_func(line.strip())
        pipe.close()

    # 创建线程来处理子进程的输出
    import threading
    stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, logger.info))
    stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, logger.error))

    stdout_thread.start()
    stderr_thread.start()

    # 等待子进程结束
    process.wait()
    stdout_thread.join()
    stderr_thread.join()


if __name__ == '__main__':
    run_celery_worker()
