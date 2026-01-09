# Bithumb Trader

🚀 **Bithumb API 2.0 기반 코인 매매 도구**

빗썸(Bithumb) 거래소의 공식 API를 활용하여 코인 매매를 수행할 수 있는 Python 패키지입니다.

## ✨ 주요 기능

- 📊 **시장 데이터 조회**: 실시간 가격, 캔들 데이터 (분/일/주/월봉)
- 💰 **계좌 확인**: 잔고 조회, 보유 코인 현황
- 📈 **거래**: 지정가/시장가 매수/매도, 주문 관리

## 📦 설치 방법

### pip로 설치 (권장)

```bash
pip install bithumb-trader
```

### 개발 버전 설치

```bash
git clone https://github.com/infinist/bithumbtradekit.git
cd bithumb-trader
pip install -e .
```

## 🔧 설정 방법

### 1. API 키 발급

1. [빗썸 웹사이트](https://www.bithumb.com)에 로그인
2. 고객센터 → API 관리에서 API 키 발급
3. Access Key와 Secret Key를 안전한 곳에 보관

## 🚀 사용 방법
### Python 코드에서 사용

```python
from bithumb_trader import BithumbClient, MarketData, Account, Trading

# 클라이언트 초기화
client = BithumbClient(access_key="your_access_key", secret_key="your_secret_key")

# 시장 데이터 조회
price = MarketData.get_current_price("BTC")
print(f"비트코인 현재가: {price:,.0f}원")

daily_data = MarketData.get_daily_data("BTC", count=10)
print(daily_data.head())

# 계좌 관리
account = Account(client)
krw_balance = account.get_krw_balance()
print(f"KRW 잔고: {krw_balance:,.0f}원")

btc_balance, avg_price = account.get_coin_balance("BTC")
print(f"BTC 보유량: {btc_balance}")

# 거래 실행
trading = Trading(client)

# 매수 주문
buy_result = trading.place_buy_order("KRW-BTC", 0.001, 50000000)
print(f"매수 주문 결과: {buy_result}")

# 매도 주문 (시장가)
sell_result = trading.place_sell_order("KRW-ETH", 0.1, ord_type="market")
print(f"매도 주문 결과: {sell_result}")
```

## 📚 API 문서

### MarketData 클래스

- `get_market_codes()`: 거래 가능한 마켓 코드 목록
- `get_current_price(coin)`: 특정 코인 현재가
- `get_minutes_data(coin, count)`: 분봉 데이터
- `get_daily_data(coin, count)`: 일봉 데이터
- `get_weekly_data(coin, count)`: 주봉 데이터
- `get_monthly_data(coin, count)`: 월봉 데이터

### Account 클래스

- `get_krw_balance()`: KRW 잔고 조회
- `get_coin_balance(coin)`: 특정 코인 잔고 조회
- `get_all_balances()`: 전체 자산 조회

### Trading 클래스

- `place_buy_order(market, volume, price)`: 매수 주문
- `place_sell_order(market, volume, price)`: 매도 주문
- `cancel_order(order_uuid)`: 주문 취소
- `get_order_status(order_uuid)`: 주문 상태 조회
- `get_orders()`: 주문 목록 조회

## ⚠️ 주의사항

- **실거래 위험**: 이 도구는 실제 자산을 거래합니다. 소액·테스트 환경에서 충분히 검증한 뒤 사용하세요.
- **API 및 최소금액**: 빗썸 API 호출 한도와 이용 약관을 준수하고, 빗썸의 최소 주문 금액(5,000원)을 확인하세요.
- **API 키 보안**: API 키/시크릿 키를 코드나 공개 저장소에 노출하지 마세요. 유출로 인한 손실은 전적으로 사용자 책임입니다.
- **시장·기술 리스크**: 가격 급변, 네트워크 오류, 버그, 거래소 정책 변경 등으로 인해 원금 전액 손실이나 오작동이 발생할 수 있습니다.

### 책임 한계 및 면책

- 이 패키지는 투자·재무 자문이 아니라, 빗썸 API 연동을 위한 기술적 도구입니다.
- 이 패키지는 “있는 그대로(as is)” 제공되며, 안정성·정확성·수익 가능성에 대해 어떤 보증도 하지 않습니다.
- 이 패키지 사용(또는 사용 불가)으로 인해 발생하는 모든 손실·손해·비용에 대해 패키지 제공자는 어떠한 법적 책임도 지지 않습니다.
