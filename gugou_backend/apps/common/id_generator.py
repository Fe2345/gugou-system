"""
ID 编号生成器。

编码规则:
  User       U + 年月日 + 4位递增号          U202604270001
  Admin      A + 4位递增数                  A0001
  Product    G + 年月日 + 4位流水号           G202604270001
  Asset      AS + 年月日时分秒 + 4位递增号     AS202604271530010001
  Order      O + 年月日时分秒 + 4位递增号      O202604271530010001
  Payment    P + 用户ID + 4位流水号           PU2026042700010001
  Exchange   E + 年月日 + 4位流水号           E202604270001
  Team       T + 年月日 + 4位流水号           T202604270001

所有序号通过 Redis INCR 原子递增，避免并发碰撞。
随机数字段改为序号以保证在高并发下绝对唯一。
"""

from datetime import datetime

from .sequences import next_seq


def _today():
    return datetime.now().strftime("%Y%m%d")


def _now():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _seq(num: int) -> str:
    return str(num).zfill(4)


def generate_user_id() -> str:
    """U + 年月日 + 4位递增号"""
    seq = next_seq(f"uid:{_today()}")
    return f"U{_today()}{_seq(seq)}"


def generate_admin_id() -> str:
    """A + 4位递增数"""
    seq = next_seq("admin")
    return f"A{_seq(seq)}"


def generate_product_id() -> str:
    """G + 年月日 + 4位流水号"""
    seq = next_seq(f"pid:{_today()}")
    return f"G{_today()}{_seq(seq)}"


def generate_asset_id() -> str:
    """AS + 年月日时分秒 + 4位递增号"""
    seq = next_seq(f"asset:{_now()}")
    return f"AS{_now()}{_seq(seq)}"


def generate_order_id() -> str:
    """O + 年月日时分秒 + 4位递增号"""
    seq = next_seq(f"order:{_now()}")
    return f"O{_now()}{_seq(seq)}"


def generate_payment_id(user_id: str) -> str:
    """P + 用户ID + 4位流水号"""
    seq = next_seq(f"payment:{user_id}")
    return f"P{user_id}{_seq(seq)}"


def generate_exchange_id() -> str:
    """E + 年月日 + 4位流水号"""
    seq = next_seq(f"exchange:{_today()}")
    return f"E{_today()}{_seq(seq)}"


def generate_team_id() -> str:
    """T + 年月日 + 4位流水号"""
    seq = next_seq(f"team:{_today()}")
    return f"T{_today()}{_seq(seq)}"


def generate_price_record_id() -> str:
    """PR + 年月日时分秒 + 4位流水号"""
    seq = next_seq(f"price:{_now()}")
    return f"PR{_now()}{_seq(seq)}"
