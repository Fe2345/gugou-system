"""
ID 编号生成器。

编码规则（沿用系统设计报告）：
  User       U + 年月日 + 4位递增号          U202604270001
  Admin      A + 4位递增数                  A0001
  Product    G + 年月日 + 4位流水号           G202604270001
  Asset      AS + 年月日时分秒 + 4位随机数     AS202604271530010001
  Order      O + 年月日时分秒 + 4位随机数      O202604271530010001
  Payment    P + 用户ID + 4位流水号           PU2026042700010001
  Exchange   E + 年月日 + 4位流水号           E202604270001
  Team       T + 年月日 + 4位流水号           T202604270001

注意：原始设计中 Product ID 包含卖家ID，DESIGN.md 已修正为独立流水号。
      原始设计中 Asset ID 为 AS + 用户ID，DESIGN.md 已修正为全局唯一编号。
"""

import random
import string
from datetime import datetime


def _today():
    return datetime.now().strftime("%Y%m%d")


def _now():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _seq(num: int) -> str:
    return str(num).zfill(4)


def _rand(n: int = 4) -> str:
    return "".join(random.choices(string.digits, k=n))


def generate_user_id(seq: int) -> str:
    """U + 年月日 + 4位递增号，例如 U202604270001"""
    return f"U{_today()}{_seq(seq)}"


def generate_admin_id(seq: int) -> str:
    """A + 4位递增数，例如 A0001"""
    return f"A{_seq(seq)}"


def generate_product_id(seq: int) -> str:
    """G + 年月日 + 4位流水号，例如 G202604270001"""
    return f"G{_today()}{_seq(seq)}"


def generate_asset_id() -> str:
    """AS + 年月日时分秒 + 4位随机数，例如 AS202604271530010001"""
    return f"AS{_now()}{_rand()}"


def generate_order_id() -> str:
    """O + 年月日时分秒 + 4位随机数，例如 O202604271530010001"""
    return f"O{_now()}{_rand()}"


def generate_payment_id(user_id: str, seq: int) -> str:
    """P + 用户ID + 4位流水号，例如 PU2026042700010001"""
    return f"P{user_id}{_seq(seq)}"


def generate_exchange_id(seq: int) -> str:
    """E + 年月日 + 4位流水号，例如 E202604270001"""
    return f"E{_today()}{_seq(seq)}"


def generate_team_id(seq: int) -> str:
    """T + 年月日 + 4位流水号，例如 T202604270001"""
    return f"T{_today()}{_seq(seq)}"
