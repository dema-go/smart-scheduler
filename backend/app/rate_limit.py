"""
API 限流配置
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建限流器
limiter = Limiter(key_func=get_remote_address)

# 限流规则
RATE_LIMITS = {
    "default": "100/minute",  # 默认：每分钟 100 次
    "auth": "10/minute",       # 认证：每分钟 10 次
    "generate": "5/minute",    # 生成排班：每分钟 5 次
    "export": "10/minute",     # 导出：每分钟 10 次
}
