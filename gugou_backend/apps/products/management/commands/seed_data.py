"""填充测试数据。用法: python manage.py seed_data"""

import json
import random
from datetime import timedelta
from pathlib import Path

from django.utils import timezone

from django.core.management.base import BaseCommand

from apps.common.id_generator import generate_user_id, generate_product_id, generate_asset_id, generate_price_record_id
from apps.accounts.models import User
from apps.products.models import Product
from apps.assets.models import UserAsset
from apps.pricing.models import PriceRecord


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class Command(BaseCommand):
    help = "填充商品、资产、价格测试数据"

    def handle(self, *args, **options):
        self._seed_user()
        self._seed_products()
        self._seed_assets()
        self._seed_prices()

    def _seed_user(self):
        if User.objects.filter(phone="13800000000").exists():
            self.stdout.write("  User 13800000000 already exists, skip")
            return
        uid = generate_user_id()
        user = User(user_id=uid, phone="13800000000", nickname="测试用户", role="user")
        user.set_password("123456")
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Created user: {uid} (13800000000 / 123456)"))

    def _seed_products(self):
        json_path = BASE_DIR / "seed_products.json"
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f"找不到: {json_path}"))
            return

        with open(json_path, encoding="utf-8") as f:
            products = json.load(f)

        created = 0
        for item in products:
            pid = generate_product_id()
            Product.objects.create(
                product_id=pid,
                name=item["name"],
                ip_name=item["ip_name"],
                character_name=item["character_name"],
                category=item["category"],
                reference_price=item["reference_price"],
                description=item["description"],
                status="active",
            )
            created += 1
            self.stdout.write(f"  [Product] {pid} - {item['name']}")

        self.stdout.write(self.style.SUCCESS(f"Created {created} products"))

    def _seed_assets(self):
        json_path = BASE_DIR / "seed_assets.json"
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f"找不到: {json_path}"))
            return

        with open(json_path, encoding="utf-8") as f:
            assets = json.load(f)

        products = list(Product.objects.all().order_by("created_at"))
        if not products:
            self.stdout.write(self.style.ERROR("No products found, skip assets"))
            return

        user = User.objects.filter(phone="13800000000").first()
        if not user:
            self.stdout.write(self.style.ERROR("Test user not found, skip assets"))
            return

        created = 0
        for item in assets:
            idx = item["product_index"]
            if idx >= len(products):
                self.stdout.write(f"  Skip: product_index {idx} out of range")
                continue

            product = products[idx]
            acquire_price = item["acquire_price"]
            current_value = product.reference_price if product.reference_price > 0 else acquire_price

            aid = generate_asset_id()
            UserAsset.objects.create(
                asset_id=aid,
                owner=user,
                product=product,
                quantity=item["quantity"],
                acquire_price=acquire_price,
                current_value=current_value,
                description=item.get("description", ""),
                status="holding",
            )
            created += 1
            self.stdout.write(f"  [Asset] {aid} - {product.name} x{item['quantity']}")

        self.stdout.write(self.style.SUCCESS(f"Created {created} assets"))

    def _seed_prices(self):
        """为每个商品生成30天的价格记录（基于参考价波动±15%）"""
        products = list(Product.objects.filter(reference_price__gt=0))
        if not products:
            self.stdout.write(self.style.ERROR("No products with reference_price, skip prices"))
            return

        now = timezone.now()
        created = 0

        for product in products:
            base = float(product.reference_price)
            # 生成30天的价格走势：从略低于参考价开始，波动上升到参考价附近
            for day in range(30, 0, -1):
                # 波动范围：参考价的 ±15%，最后一天接近参考价
                progress = (30 - day) / 30  # 0→1
                trend = base * (0.9 + 0.1 * progress)  # 从90%到100%
                noise = random.uniform(-base * 0.08, base * 0.08)
                price = round(max(trend + noise, base * 0.7), 2)

                recorded_at = now - timedelta(days=day, hours=random.randint(8, 20))
                PriceRecord.objects.create(
                    price_record_id=generate_price_record_id(),
                    product=product,
                    price=price,
                    source="manual",
                    recorded_at=recorded_at,
                )
                created += 1

            self.stdout.write(f"  [Price] {product.name} - 30 records")

        self.stdout.write(self.style.SUCCESS(f"Created {created} price records"))
