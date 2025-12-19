"""
Bithumb API 2.0 기반 코인 자동매매 도구

이 패키지는 빗썸(Bithumb) 거래소의 API를 활용하여
코인 자동매매를 수행할 수 있는 기능들을 제공합니다.
"""

__version__ = "0.1.0"
__author__ = "infinist"
__email__ = "infinist@naver.com"

from .client import BithumbClient
from .market import MarketData
from .trading import Trading
from .account import Account

__all__ = [
    "BithumbClient",
    "MarketData",
    "Trading",
    "Account",
]
