import functools
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any, Callable

# 计算项目根目录，logger.py 在 core 目录下，向上一级就是项目根目录
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 日志目录放在项目根目录下的 logs 文件夹
LOG_DIR = os.path.join(BASE_DIR, 'logs')
# 如果 logs 目录不存在，则创建它
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
# 日志输出格式，包含时间、日志级别、日志名称和日志内容
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
# 时间格式
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 创建顶级 logger 对象，名称统一为 order_management_system
logger = logging.getLogger('order_management_system')
# 如果已经添加过 handler，就不要重复初始化，避免重复打印
if not logger.handlers:
    # 日志默认级别为 INFO
    logger.setLevel(logging.INFO)

    # 控制台输出处理器，用于开发时直接输出到终端
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(console_handler)

    # 文件输出处理器，使用滚动文件，避免单个日志文件过大
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(file_handler)

    # 禁止向上级 logger 传播，避免重复输出
    logger.propagate = False


def get_logger(name: str | None = None) -> logging.Logger:
    """返回指定名称的 logger。"""
    if name:
        # 返回子 logger，便于模块化区分日志来源
        return logging.getLogger(f'order_management_system.{name}')
    return logger


def log_action(action: str | None = None, log_args: bool = True, level: int = logging.INFO) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """通用日志装饰器：记录方法开始、结束和异常。"""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            name = action or func.__name__
            if log_args:
                # 记录方法开始，并打印参数
                logger.log(level, '开始操作: %s args=%s kwargs=%s', name, args, kwargs)
            else:
                # 只记录操作名称
                logger.log(level, '开始操作: %s', name)
            try:
                result = func(*args, **kwargs)
                # 方法执行成功
                logger.log(level, '操作成功: %s', name)
                return result
            except Exception:
                # 捕获异常并记录堆栈
                logger.exception('操作失败: %s', name)
                raise
        return wrapper
    return decorator
