"""
统一响应工具
============
标准化整个系统的所有API返回格式

没有这个的话，每个开发各写各的返回格式，
前端开发天天哭。

为什么需要统一返回？
  1. 前端只需要一套拦截器逻辑
  2. 再也没有 code=0/code=200/code=1 不一致
  3. 再也没有 data/result/list 命名混乱
  4. 带时间戳方便排查问题
"""
import time


def success(data=None, msg: str = "操作成功") -> dict:
    """
    统一成功响应
    所有成功的API返回都调用这个函数
    
    :param data: 返回给前端的业务数据, 可选 (删除等操作可以不传)
    :param msg: 用户友好提示信息, 默认"操作成功"
    :return: 标准格式的字典
    
    示例:
        return success(user, "登录成功")
        return success(msg="删除成功")  # 没有data的场景
    """
    return {
        "code": 200,      # 约定: 200 = 完全成功
        "msg": msg,       # 用户友好的提示文案
        "data": data,     # 实际业务数据
        "timestamp": int(time.time())  # 服务器时间戳, 排查问题用
    }


def fail(msg: str = "操作失败", code: int = 400, data=None) -> dict:
    """
    统一失败响应
    所有已知的业务失败都调用这个函数
    
    标准错误码约定:
      400=参数错误, 401=未登录, 403=无权限, 404=资源不存在
    
    重要: 未处理的异常永远不要用这个!
          全局异常处理器会自动捕获
    
    示例:
        return fail("用户名已存在", 400)
        return fail("余额不足")
    """
    return {
        "code": code,     # 具体错误码
        "msg": msg,       # 给用户看的错误信息
        "data": data,     # 可选的错误详情
        "timestamp": int(time.time())
    }
