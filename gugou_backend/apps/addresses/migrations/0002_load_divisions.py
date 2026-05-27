import os
import sqlite3

from django.conf import settings
from django.db import migrations


def load_divisions(apps, schema_editor):
    Division = apps.get_model("addresses", "Division")

    # 查找 data.sqlite：优先项目根目录，其次 /tmp
    candidates = [
        settings.BASE_DIR.parent / "data.sqlite",
        "/tmp/data.sqlite",
    ]
    db_path = None
    for p in candidates:
        p = str(p)
        if os.path.exists(p):
            # 排除 GitHub HTML 页面（以 < 开头）
            with open(p, "rb") as f:
                header = f.read(1)
                if header != b"<":
                    db_path = p
                    break

    if db_path is None:
        raise RuntimeError("未找到有效的 data.sqlite 文件。")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # 先查出所有 province → insert → 缓存 code -> Division instance
    code_map = {}

    # Level 1: 省
    for row in conn.execute("SELECT code, name FROM province"):
        d = Division(code=row["code"], name=row["name"], level=1, parent=None)
        code_map[row["code"]] = d

    # Level 2: 市
    for row in conn.execute("SELECT code, name, provinceCode FROM city"):
        parent = code_map.get(row["provinceCode"])
        d = Division(code=row["code"], name=row["name"], level=2, parent=parent)
        code_map[row["code"]] = d

    # Level 3: 区
    for row in conn.execute("SELECT code, name, cityCode FROM area"):
        parent = code_map.get(row["cityCode"])
        d = Division(code=row["code"], name=row["name"], level=3, parent=parent)
        code_map[row["code"]] = d

    conn.close()

    # bulk create all at once
    Division.objects.bulk_create(code_map.values(), batch_size=500)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("addresses", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_divisions, reverse_code=noop),
    ]
