import logging
import os

# 로깅 설정 초기화
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 로거 생성
logger = logging.getLogger("my_app_logger")

# 파일 핸들러 설정
error_handler = logging.FileHandler('/var/www/html/logs/my-app-error.log')
error_handler.setLevel(logging.WARNING)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

info_handler = logging.FileHandler('/var/www/html/logs/my-app-out.log')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# 핸들러를 로거에 추가
logger.addHandler(error_handler)
logger.addHandler(info_handler)
