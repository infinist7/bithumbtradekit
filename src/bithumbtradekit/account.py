"""
계좌 관리 모듈
"""

import logging
import traceback
from typing import Dict, Any, List, Tuple, Optional
from .client import BithumbClient


logger = logging.getLogger(__name__)


class Account:
    """계좌 관리 클래스"""

    def __init__(self, client: BithumbClient):
        """
        계좌 관리 클래스 초기화

        Args:
            client: BithumbClient 인스턴스
        """
        self.client = client
        self.avg_buy_prices = {}  # 평균매수가 저장용

    def get_account_info(self) -> Dict[str, Any]:
        """
        빗썸 API를 사용하여 계좌 정보를 조회

        Returns:
            Dict[str, Any]: 계좌 정보
        """
        try:
            response = self.client.get("/v1/accounts")
            if "error" in response:
                logger.error(f"❌ API 호출 오류: {response['error']}")
                return {"error": response["error"]}
            return response
        except Exception as e:
            logger.error(f"❗ 예외 발생: {e}")
            traceback.print_exc()
            return {"error": str(e)}

    def get_krw_balance(self) -> float:
        """
        KRW 계좌 잔고 조회

        Returns:
            float: KRW 잔고
        """
        try:
            account_info = self.get_account_info()
            if "error" in account_info:
                logger.error(f"❌ 계좌 조회 실패: {account_info['error']}")
                return 0

            cash = [j["balance"] for j in account_info if j["currency"] == "KRW"]
            return float(cash[0]) if cash else 0
        except Exception as e:
            logger.error(f"❌ 계좌 조회 중 오류: {e}")
            traceback.print_exc()
            return 0

    def get_coin_balance(self, coin: str) -> Tuple[Optional[float], Optional[float]]:
        """
        특정 코인의 보유 수량 및 평균매수가 조회

        Args:
            coin: 코인 심볼 (예: 'BTC', 'ETH')

        Returns:
            Tuple[Optional[float], Optional[float]]: (보유수량, 평균매수가)
            - None: API 에러 시
            - (0, 0): 해당 코인 미보유 시
        """
        try:
            account_info = self.get_account_info()
            if "error" in account_info:
                logger.error(f"❌ 계좌 조회 실패: {account_info['error']}")
                return None, None  # API 에러 시 None 반환으로 에러와 정상(0,0) 구분

            coin_info = [j for j in account_info if j["currency"] == coin]
            if coin_info:
                balance = float(coin_info[0]["balance"])
                avg_price = float(coin_info[0].get("avg_buy_price", 0))

                # API에서 평균매수가를 가져온 경우 저장
                if avg_price > 0 and balance > 0:
                    self.avg_buy_prices[coin] = avg_price
                    logger.info(
                        f"📊 {coin} API 평균매수가 업데이트: {avg_price:,.0f}원"
                    )

                return balance, avg_price
            else:
                return 0, 0  # 해당 코인 보유하지 않음 (정상 상황)
        except Exception as e:
            logger.error(f"❌ {coin} 잔고 조회 중 오류: {e}")
            traceback.print_exc()
            return None, None  # 예외 발생 시 None 반환

    def get_all_balances(self) -> List[Dict[str, Any]]:
        """
        모든 자산 잔고 조회

        Returns:
            List[Dict[str, Any]]: 모든 자산 정보 리스트
        """
        account_info = self.get_account_info()
        if "error" in account_info:
            return []

        balances = []
        for asset in account_info:
            if float(asset["balance"]) > 0:
                balances.append(
                    {
                        "currency": asset["currency"],
                        "balance": float(asset["balance"]),
                        "avg_buy_price": float(asset.get("avg_buy_price", 0)),
                        "locked": float(asset.get("locked", 0)),
                    }
                )

        return balances
