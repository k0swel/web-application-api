import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from flask import request

class AccessErrorLogger:
    """
    Логгер с разделением на access и error логи
    
    Access логи: stdout + файл access.log
    Error логи: stderr + файл error.log
    """
    def __init__(self, 
                 log_dir: str = "logs",
                 access_log_file: str = "access.log",
                 error_log_file: str = "error.log",
                 max_bytes: int = 10_485_760,  # 10 MB
                 backup_count: int = 5):
        
        self.log_dir = Path(log_dir)
        self.access_log_file = self.log_dir / access_log_file
        self.error_log_file = self.log_dir / error_log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем корневой логгер
        self.logger = logging.getLogger("api")
        self.logger.setLevel(logging.DEBUG)
                
        # Настраиваем обработчики
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка всех обработчиков логов"""
        
        # Формат для access логов
        access_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Формат для error логов (более подробный)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        
        # 1. Access в stdout 
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(access_formatter)
        stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)  # Только INFO и DEBUG
        self.logger.addHandler(stdout_handler)
        
        # 2. Access в файл 
        access_file_handler = RotatingFileHandler(
            self.access_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        access_file_handler.setLevel(logging.INFO)
        access_file_handler.setFormatter(access_formatter)
        access_file_handler.addFilter(lambda record: record.levelno < logging.WARNING)
        self.logger.addHandler(access_file_handler)
        
        
        # 1. Error в stderr
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.setFormatter(error_formatter)
        self.logger.addHandler(stderr_handler)
        
        # 2. Error в файл
        error_file_handler = RotatingFileHandler(
            self.error_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.WARNING)
        error_file_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_file_handler)
    
    def get_logger(self):
        """Получить настроенный логгер"""
        return self.logger


logger = AccessErrorLogger().get_logger() # создаём логгер для логирования действий
