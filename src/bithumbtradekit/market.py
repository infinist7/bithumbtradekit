"""
시장 데이터 조회 모듈
"""

import json
from typing import List, Dict, Any
import pandas as pd
import requests


class MarketData:
    """시장 데이터 조회 클래스"""

    @staticmethod
    def get_market_codes() -> str:
        """
        빗썸 거래 가능한 코인 목록 조회

        Returns:
            str: 마켓 코드 정보 JSON 문자열
        """
        url = "https://api.bithumb.com/v1/market/all?isDetails=false"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        return response.text

    @staticmethod
    def get_current_price(coin: str) -> float:
        """
        특정 코인의 현재가 조회

        Args:
            coin: 마켓 코드 (예: 'KRW-BTC', 'KRW-ETH')

        Returns:
            float: 현재가
        """
        url = f"https://api.bithumb.com/v1/ticker?markets={coin.upper()}"
        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        return data[0]["trade_price"]

    @staticmethod
    def _get_candle_data(url: str, coin: str, count: int = 30) -> pd.DataFrame:
        """
        캔들 데이터 조회 공통 함수

        Args:
            url: API 엔드포인트 URL
            coin: 마켓 코드 (예: 'KRW-BTC', 'KRW-ETH')
            count: 조회할 데이터 개수

        Returns:
            pd.DataFrame: 캔들 데이터
        """
        params = {"market": f"{coin.upper()}", "count": count}
        headers = {"accept": "application/json"}
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        # 정상 응답은 리스트, 에러 응답은 dict
        if isinstance(data, dict) and "status" in data and data["status"] != "0000":
            raise Exception(f"API 오류: {data.get('message', 'Unknown error')}")
        if not isinstance(data, list):
            raise Exception(f"API 응답이 리스트가 아님: {data}")

        df = pd.DataFrame(data)
        df = df.rename(
            columns={
                "candle_date_time_kst": "date",
                "opening_price": "open",
                "trade_price": "close",
                "high_price": "high",
                "low_price": "low",
                "candle_acc_trade_volume": "volume",
                "candle_acc_trade_price": "value",
                "change_rate": "change_rate",
            }
        )

        # 선택할 컬럼 리스트 (존재하는 것만)
        base_columns = ["date", "open", "close", "high", "low"]
        optional_columns = ["change_rate", "volume", "value"]
        columns = base_columns + [c for c in optional_columns if c in df.columns]

        df = df[columns]
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

    @staticmethod
    def get_minutes_data(coin: str, unit: int = 1, count: int = 30) -> pd.DataFrame:
        """
        분봉 데이터 조회

        Args:
            coin: 마켓 코드 (예: 'KRW-BTC', 'KRW-ETH')
            unit: 분봉 단위 (1, 3, 5, 10, 15, 30, 60, 240)
            count: 조회할 데이터 개수

        Returns:
            pd.DataFrame: 분봉 데이터
        """
        url = f"https://api.bithumb.com/v1/candles/minutes/{unit}"
        return MarketData._get_candle_data(url, coin, count)

    @staticmethod
    def get_daily_data(coin: str, count: int = 30) -> pd.DataFrame:
        """
        일봉 데이터 조회

        Args:
            coin: 마켓 코드 (예: 'KRW-BTC', 'KRW-ETH')
            count: 조회할 데이터 개수

        Returns:
            pd.DataFrame: 일봉 데이터
        """
        url = "https://api.bithumb.com/v1/candles/days"
        return MarketData._get_candle_data(url, coin, count)

    @staticmethod
    def get_weekly_data(coin: str, count: int = 30) -> pd.DataFrame:
        """
        주봉 데이터 조회

        Args:
            coin: 마켓 코드 (예: 'KRW-BTC', 'KRW-ETH')
            count: 조회할 데이터 개수

        Returns:
            pd.DataFrame: 주봉 데이터
        """
        url = "https://api.bithumb.com/v1/candles/weeks"
        return MarketData._get_candle_data(url, coin, count)

    @staticmethod
    def get_monthly_data(coin: str, count: int = 30) -> pd.DataFrame:
        """
        월봉 데이터 조회

        Args:
            coin: 마켓 코드 (예: 'KRW-BTC', 'KRW-ETH')
            count: 조회할 데이터 개수

        Returns:
            pd.DataFrame: 월봉 데이터
        """
        url = "https://api.bithumb.com/v1/candles/months"
        return MarketData._get_candle_data(url, coin, count)
