import logging
import sys
from logging.handlers import RotatingFileHandler

# 로그 레벨 설정
LOG_LEVEL = "DEBUG"

# 로그 포맷 설정
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 로그 파일 경로 설정
INFO_LOG_FILE = "/var/www/html/logs/my-app-info.log"
ERROR_LOG_FILE = "/var/www/html/logs/my-app-error.log"

# 로거 생성
logger = logging.getLogger("my-app")
logger.setLevel(LOG_LEVEL)

# 핸들러: INFO 및 DEBUG 로그 전용 (stdout)
info_handler = logging.StreamHandler(sys.stdout)
info_handler.setLevel(logging.INFO)  # INFO 레벨 이상의 로그
info_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# 핸들러: ERROR 및 CRITICAL 로그 전용 (stderr)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setLevel(logging.ERROR)  # ERROR 레벨 이상의 로그
error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# 핸들러: INFO 로그 파일 저장
info_file_handler = RotatingFileHandler(INFO_LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
info_file_handler.setLevel(logging.INFO)
info_file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# 핸들러: ERROR 로그 파일 저장
error_file_handler = RotatingFileHandler(ERROR_LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# 로거에 핸들러 추가
logger.addHandler(info_handler)       # stdout
logger.addHandler(error_handler)      # stderr
logger.addHandler(info_file_handler)  # 파일 저장 (INFO)
logger.addHandler(error_file_handler) # 파일 저장 (ERROR)
