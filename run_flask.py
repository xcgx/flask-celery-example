import os
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_flask_app():
    """启动 Flask 应用"""
    logger.info("启动 Flask 应用")
    os.system('python app.py')

if __name__ == '__main__':
    run_flask_app()
