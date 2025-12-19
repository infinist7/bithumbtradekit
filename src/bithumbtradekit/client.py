"""
Bithumb API 클라이언트 클래스
"""

import hashlib
import time
import uuid
from urllib.parse import urlencode
from typing import Optional, Dict, Any
import jwt
import requests


class BithumbClient:
    """빗썸 API 클라이언트"""

    def __init__(self, access_key: str, secret_key: str):
        """
        빗썸 API 클라이언트 초기화

        Args:
            access_key: API 액세스 키
            secret_key: API 시크릿 키
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.api_url = "https://api.bithumb.com"

    def _create_headers(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """JWT 인증 헤더 생성"""
        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
            "timestamp": round(time.time() * 1000),
        }

        if params:
            query = urlencode(params).encode()
            hash_obj = hashlib.sha512()
            hash_obj.update(query)
            query_hash = hash_obj.hexdigest()

            payload.update(
                {
                    "query_hash": query_hash,
                    "query_hash_alg": "SHA512",
                }
            )

        jwt_token = jwt.encode(payload, self.secret_key)
        return {"Authorization": f"Bearer {jwt_token}"}

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """GET 요청"""
        headers = self._create_headers(params)
        try:
            response = requests.get(
                self.api_url + endpoint, params=params, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """POST 요청"""
        headers = self._create_headers(data)
        try:
            response = requests.post(
                self.api_url + endpoint, json=data, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """DELETE 요청"""
        headers = self._create_headers(params)
        try:
            response = requests.delete(
                self.api_url + endpoint, params=params, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
