"""
거래 관련 모듈
"""

import logging
from typing import Dict, Any, Optional
from .client import BithumbClient


logger = logging.getLogger(__name__)


class Trading:
    """거래 관리 클래스"""

    def __init__(self, client: BithumbClient):
        """
        거래 관리 클래스 초기화

        Args:
            client: BithumbClient 인스턴스
        """
        self.client = client

    def _send_order(
        self,
        market: str,
        side: str,
        volume: float,
        price: Optional[float] = None,
        ord_type: str = "limit",
    ) -> Dict[str, Any]:
        """
        주문 전송 공통 함수

        Args:
            market: 마켓 코드 (예: 'KRW-BTC')
            side: 주문 종류 ('bid': 매수, 'ask': 매도)
            volume: 주문 수량
            price: 주문 가격 (시장가 주문시 None)
            ord_type: 주문 타입 ('limit': 지정가, 'market': 시장가)

        Returns:
            Dict[str, Any]: 주문 결과
        """
        data = {
            "market": market,
            "side": side,
            "volume": str(volume),
            "ord_type": ord_type,
        }

        if ord_type == "limit" and price is not None:
            data["price"] = str(price)

        return self.client.post("/v1/orders", data)

    def _send_market_order(
        self, market: str, side: str, volume: float
    ) -> Dict[str, Any]:
        """
        시장가 주문 전송

        Args:
            market: 마켓 코드
            side: 주문 종류
            volume: 주문 수량

        Returns:
            Dict[str, Any]: 주문 결과
        """
        return self._send_order(market, side, volume, ord_type="market")

    def place_buy_order(
        self, market: str, volume: float, price: float, ord_type: str = "limit"
    ) -> Dict[str, Any]:
        """
        매수 주문

        Args:
            market: 마켓 코드 (예: 'KRW-BTC')
            volume: 주문 수량
            price: 주문 가격
            ord_type: 주문 타입 ('limit': 지정가, 'market': 시장가)

        Returns:
            Dict[str, Any]: 주문 결과
        """
        return self._send_order(market, "bid", volume, price, ord_type)

    def place_sell_order(
        self,
        market: str,
        volume: float,
        price: Optional[float] = None,
        ord_type: str = "limit",
    ) -> Dict[str, Any]:
        """
        매도 주문 - 시장가 지원

        Args:
            market: 마켓 코드 (예: 'KRW-BTC')
            volume: 주문 수량
            price: 주문 가격 (시장가 주문시 None)
            ord_type: 주문 타입 ('limit': 지정가, 'market': 시장가)

        Returns:
            Dict[str, Any]: 주문 결과
        """
        if ord_type == "market":
            return self._send_market_order(market, "ask", volume)
        else:
            return self._send_order(market, "ask", volume, price, ord_type)

    def cancel_order(self, order_uuid: str) -> Dict[str, Any]:
        """
        주문 취소

        Args:
            order_uuid: 주문 UUID

        Returns:
            Dict[str, Any]: 취소 결과
        """
        params = {"uuid": order_uuid}
        return self.client.delete("/v1/order", params)

    def get_order_status(self, order_uuid: str) -> str:
        """
        개별 주문 상태 조회

        Args:
            order_uuid: 주문 UUID

        Returns:
            str: 주문 상태 ("wait", "done", "cancel", "error", "unknown")
        """
        params = {"uuid": order_uuid}
        result = self.client.get("/v1/order", params)

        if "error" in result:
            return "error"

        return result.get("state", "unknown")

    def get_orders(
        self, market: Optional[str] = None, state: str = "wait"
    ) -> Dict[str, Any]:
        """
        주문 목록 조회

        Args:
            market: 마켓 코드 (전체 조회시 None)
            state: 주문 상태 ("wait", "done", "cancel")

        Returns:
            Dict[str, Any]: 주문 목록
        """
        params = {"state": state}
        if market:
            params["market"] = market

        return self.client.get("/v1/orders", params)

    def get_order_chance(self, market: str) -> Dict[str, Any]:
        """
        주문 가능 정보 조회

        Args:
            market: 마켓 코드

        Returns:
            Dict[str, Any]: 주문 가능 정보
        """
        params = {"market": market}
        return self.client.get("/v1/orders/chance", params)
