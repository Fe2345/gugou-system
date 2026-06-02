"""填充测试数据。用法: python manage.py seed_data"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from django.utils import timezone

from django.core.management.base import BaseCommand

from apps.common.id_generator import generate_user_id
from apps.accounts.models import User
from apps.products.models import Product, ProductImage
from apps.assets.models import UserAsset
from apps.pricing.models import PriceRecord


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
SEQ_FILE = BASE_DIR / ".seq_cache"


class LocalSequence:
    """Seed data generates many IDs, so avoid waiting on Redis per row."""

    def __init__(self):
        self.data = {}
        if SEQ_FILE.exists():
            with open(SEQ_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" not in line:
                        continue
                    key, value = line.strip().split("=", 1)
                    try:
                        self.data[key] = int(value)
                    except ValueError:
                        pass

    def next(self, key):
        value = self.data.get(key, 0) + 1
        self.data[key] = value
        return value

    def save(self):
        with open(SEQ_FILE, "w", encoding="utf-8") as f:
            for key, value in self.data.items():
                f.write(f"{key}={value}\n")


def _today():
    return datetime.now().strftime("%Y%m%d")


def _now():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _seq(num):
    return str(num).zfill(4)


class Command(BaseCommand):
    help = "填充商品、资产、价格测试数据"

    def handle(self, *args, **options):
        self.local_sequence = LocalSequence()
        self._seed_user()
        self._seed_products()
        self._seed_assets()
        self._seed_prices()
        self.local_sequence.save()

    def _generate_product_id(self):
        return f"G{_today()}{_seq(self.local_sequence.next(f'pid:{_today()}'))}"

    def _generate_asset_id(self):
        now = _now()
        return f"AS{now}{_seq(self.local_sequence.next(f'asset:{now}'))}"

    def _generate_price_record_id(self):
        now = _now()
        return f"PR{now}{_seq(self.local_sequence.next(f'price:{now}'))}"

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
        updated = 0
        for item in products:
            lookup = {
                "name": item["name"],
                "ip_name": item["ip_name"],
                "character_name": item["character_name"],
                "category": item["category"],
            }
            main_image = item.get("main_image") or item.get("mainImage", "")
            product = Product.objects.filter(**lookup).first()
            if product is None:
                product = Product(product_id=self._generate_product_id(), **lookup)
                created += 1
                action = "Created"
            else:
                updated += 1
                action = "Updated"

            product.reference_price = item["reference_price"]
            product.main_image = main_image
            product.description = item["description"]
            product.status = "active"
            product.save()

            images = item.get("images", [])
            if images:
                ProductImage.objects.filter(product=product).delete()
                ProductImage.objects.bulk_create(
                    [
                        ProductImage(
                            product=product,
                            image_url=image["url"] if isinstance(image, dict) else image,
                            sort_order=index,
                        )
                        for index, image in enumerate(images)
                    ]
                )

            self.stdout.write(f"  [Product] {action} {product.product_id} - {item['name']}")

        self.stdout.write(self.style.SUCCESS(f"Created {created} products, updated {updated} products"))

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

            description = item.get("description", "")
            asset = UserAsset.objects.filter(owner=user, product=product, description=description).first()
            if asset:
                asset.quantity = item["quantity"]
                asset.acquire_price = acquire_price
                asset.current_value = current_value
                asset.status = "holding"
                asset.save(update_fields=["quantity", "acquire_price", "current_value", "status", "updated_at"])
                self.stdout.write(f"  [Asset] Updated {asset.asset_id} - {product.name} x{item['quantity']}")
                continue

            aid = self._generate_asset_id()
            UserAsset.objects.create(
                asset_id=aid,
                owner=user,
                product=product,
                quantity=item["quantity"],
                acquire_price=acquire_price,
                current_value=current_value,
                description=description,
                status="holding",
            )
            created += 1
            self.stdout.write(f"  [Asset] Created {aid} - {product.name} x{item['quantity']}")

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
            if PriceRecord.objects.filter(product=product, source="manual").exists():
                self.stdout.write(f"  [Price] {product.name} already has manual records, skip")
                continue

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
                    price_record_id=self._generate_price_record_id(),
                    product=product,
                    price=price,
                    source="manual",
                    recorded_at=recorded_at,
                )
                created += 1

            self.stdout.write(f"  [Price] {product.name} - 30 records")

        self.stdout.write(self.style.SUCCESS(f"Created {created} price records"))
