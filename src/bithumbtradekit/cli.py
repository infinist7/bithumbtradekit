"""
명령행 인터페이스 (CLI)
"""

import click
import json
import pandas as pd
from typing import Optional
from .client import BithumbClient
from .market import MarketData
from .account import Account
from .trading import Trading


@click.group()
@click.option(
    "--access-key", envvar="BITHUMB_ACCESS_KEY", help="Bithumb API Access Key"
)
@click.option(
    "--secret-key", envvar="BITHUMB_SECRET_KEY", help="Bithumb API Secret Key"
)
@click.pass_context
def main(ctx, access_key: Optional[str], secret_key: Optional[str]):
    """Bithumb 자동매매 도구"""
    ctx.ensure_object(dict)
    if access_key and secret_key:
        ctx.obj["client"] = BithumbClient(access_key, secret_key)
    else:
        ctx.obj["client"] = None


@main.group()
def market():
    """시장 데이터 조회"""
    pass


@market.command()
def codes():
    """거래 가능한 코인 목록 조회"""
    try:
        result = MarketData.get_market_codes()
        data = json.loads(result)
        click.echo("📊 거래 가능한 코인 목록:")
        for item in data[:10]:  # 상위 10개만 출력
            click.echo(f"  {item.get('market', 'N/A')}")
        click.echo(f"... 총 {len(data)}개 코인")
    except Exception as e:
        click.echo(f"❌ 오류: {e}")


@market.command()
@click.argument("coin")
def price(coin: str):
    """특정 코인의 현재가 조회"""
    try:
        current_price = MarketData.get_current_price(coin)
        click.echo(f"💰 {coin.upper()} 현재가: {current_price:,.0f}원")
    except Exception as e:
        click.echo(f"❌ 오류: {e}")


@market.command()
@click.argument("coin")
@click.option(
    "--period",
    "-p",
    default="daily",
    type=click.Choice(["minutes", "daily", "weekly", "monthly"]),
    help="조회 기간",
)
@click.option("--count", "-c", default=10, help="조회할 데이터 개수")
def candle(coin: str, period: str, count: int):
    """캔들 데이터 조회"""
    try:
        if period == "minutes":
            df = MarketData.get_minutes_data(coin, count)
        elif period == "daily":
            df = MarketData.get_daily_data(coin, count)
        elif period == "weekly":
            df = MarketData.get_weekly_data(coin, count)
        elif period == "monthly":
            df = MarketData.get_monthly_data(coin, count)

        click.echo(f"📈 {coin.upper()} {period} 캔들 데이터 (최근 {count}개):")
        click.echo(df.tail().to_string(index=False))
    except Exception as e:
        click.echo(f"❌ 오류: {e}")


@main.group()
@click.pass_context
def account(ctx):
    """계좌 관리"""
    if not ctx.obj["client"]:
        click.echo("❌ API 키가 설정되지 않았습니다.")
        click.echo("환경변수 BITHUMB_ACCESS_KEY, BITHUMB_SECRET_KEY를 설정하거나")
        click.echo("--access-key, --secret-key 옵션을 사용하세요.")
        ctx.exit(1)


@account.command()
@click.pass_context
def balance(ctx):
    """계좌 잔고 조회"""
    try:
        client = ctx.obj["client"]
        acc = Account(client)

        krw_balance = acc.get_krw_balance()
        click.echo(f"💰 KRW 잔고: {krw_balance:,.0f}원")

        all_balances = acc.get_all_balances()
        if all_balances:
            click.echo("\n🪙 보유 코인:")
            for item in all_balances:
                if item["currency"] != "KRW":
                    click.echo(f"  {item['currency']}: {item['balance']:,.8f}")
                    if item["avg_buy_price"] > 0:
                        click.echo(f"    평균매수가: {item['avg_buy_price']:,.0f}원")
    except Exception as e:
        click.echo(f"❌ 오류: {e}")


@main.group()
@click.pass_context
def trade(ctx):
    """거래 관리"""
    if not ctx.obj["client"]:
        click.echo("❌ API 키가 설정되지 않았습니다.")
        ctx.exit(1)


@trade.command()
@click.argument("market")
@click.argument("volume", type=float)
@click.argument("price", type=float)
@click.pass_context
def buy(ctx, market: str, volume: float, price: float):
    """매수 주문"""
    try:
        client = ctx.obj["client"]
        trading = Trading(client)

        result = trading.place_buy_order(market, volume, price)
        if "error" in result:
            click.echo(f"❌ 매수 주문 실패: {result['error']}")
        else:
            click.echo(f"✅ 매수 주문 성공:")
            click.echo(f"  주문 UUID: {result.get('uuid', 'N/A')}")
            click.echo(f"  마켓: {market}")
            click.echo(f"  수량: {volume}")
            click.echo(f"  가격: {price:,.0f}원")
    except Exception as e:
        click.echo(f"❌ 오류: {e}")


@trade.command()
@click.argument("market")
@click.argument("volume", type=float)
@click.option("--price", type=float, help="지정가 (시장가 주문시 생략)")
@click.pass_context
def sell(ctx, market: str, volume: float, price: Optional[float]):
    """매도 주문"""
    try:
        client = ctx.obj["client"]
        trading = Trading(client)

        ord_type = "limit" if price else "market"
        result = trading.place_sell_order(market, volume, price, ord_type)

        if "error" in result:
            click.echo(f"❌ 매도 주문 실패: {result['error']}")
        else:
            click.echo(f"✅ 매도 주문 성공:")
            click.echo(f"  주문 UUID: {result.get('uuid', 'N/A')}")
            click.echo(f"  마켓: {market}")
            click.echo(f"  수량: {volume}")
            if price:
                click.echo(f"  가격: {price:,.0f}원")
            else:
                click.echo("  타입: 시장가")
    except Exception as e:
        click.echo(f"❌ 오류: {e}")


@trade.command()
@click.pass_context
def orders(ctx):
    """미체결 주문 목록 조회"""
    try:
        client = ctx.obj["client"]
        trading = Trading(client)

        result = trading.get_orders()
        if "error" in result:
            click.echo(f"❌ 주문 조회 실패: {result['error']}")
        else:
            orders = result
            if not orders:
                click.echo("📋 미체결 주문이 없습니다.")
            else:
                click.echo("📋 미체결 주문 목록:")
                for order in orders:
                    click.echo(f"  UUID: {order.get('uuid', 'N/A')}")
                    click.echo(f"  마켓: {order.get('market', 'N/A')}")
                    click.echo(f"  타입: {order.get('side', 'N/A')}")
                    click.echo(f"  수량: {order.get('volume', 'N/A')}")
                    click.echo(f"  가격: {order.get('price', 'N/A')}")
                    click.echo("  ---")
    except Exception as e:
        click.echo(f"❌ 오류: {e}")


if __name__ == "__main__":
    main()
