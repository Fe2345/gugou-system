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
from apps.market.models import Listing
from apps.orders.models import Order, PaymentRecord, OrderStatusLog
from apps.exchanges.models import ExchangeRequest, ExchangeMatch
from apps.teams.models import TeamProject, TeamParticipant
from apps.credits.models import CreditRecord


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
    help = "填充用户、商品、资产、价格、挂单、订单、换物、拼团、信用测试数据"

    def handle(self, *args, **options):
        self.local_sequence = LocalSequence()
        self._seed_user()
        self._seed_products()
        self._seed_assets()
        self._seed_prices()
        self._seed_listings()
        self._seed_orders()
        self._seed_exchanges()
        self._seed_teams()
        self._seed_credits()
        self.local_sequence.save()

    def _generate_product_id(self):
        return f"G{_today()}{_seq(self.local_sequence.next(f'pid:{_today()}'))}"

    def _generate_asset_id(self):
        now = _now()
        return f"AS{now}{_seq(self.local_sequence.next(f'asset:{now}'))}"

    def _generate_price_record_id(self):
        now = _now()
        return f"PR{now}{_seq(self.local_sequence.next(f'price:{now}'))}"

    def _generate_listing_id(self):
        now = _now()
        return f"L{now}{_seq(self.local_sequence.next(f'listing:{now}'))}"

    def _generate_order_id(self):
        now = _now()
        return f"O{now}{_seq(self.local_sequence.next(f'order:{now}'))}"

    def _generate_payment_id(self):
        now = _now()
        return f"P{now}{_seq(self.local_sequence.next(f'payment:{now}'))}"

    def _generate_order_log_id(self):
        now = _now()
        return f"OL{now}{_seq(self.local_sequence.next(f'order_log:{now}'))}"

    def _generate_exchange_id(self):
        return f"E{_today()}{_seq(self.local_sequence.next(f'exchange:{_today()}'))}"

    def _generate_match_id(self):
        now = _now()
        return f"M{now}{_seq(self.local_sequence.next(f'match:{now}'))}"

    def _generate_team_id(self):
        return f"T{_today()}{_seq(self.local_sequence.next(f'team:{_today()}'))}"

    def _generate_participant_id(self):
        now = _now()
        return f"TP{now}{_seq(self.local_sequence.next(f'participant:{now}'))}"

    def _generate_credit_record_id(self):
        return f"CR{_today()}{_seq(self.local_sequence.next(f'credit:{_today()}'))}"

    def _seed_user(self):
        # 创建默认测试用户
        if not User.objects.filter(phone="13800000000").exists():
            uid = generate_user_id()
            user = User(user_id=uid, phone="13800000000", nickname="测试用户", role="user")
            user.set_password("123456")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {uid} (13800000000 / 123456)"))

        # 从 JSON 文件批量加载用户
        json_path = BASE_DIR / "seed_users.json"
        if not json_path.exists():
            self.stdout.write("  seed_users.json not found, skip batch users")
            return

        with open(json_path, encoding="utf-8") as f:
            users = json.load(f)

        created = 0
        for item in users:
            if User.objects.filter(phone=item["phone"]).exists():
                self.stdout.write(f"  User {item['phone']} already exists, skip")
                continue
            uid = generate_user_id()
            user = User(
                user_id=uid,
                phone=item["phone"],
                nickname=item["nickname"],
                role=item.get("role", "user"),
                credit_score=item.get("credit_score", 100),
            )
            user.set_password(item["password"])
            user.save()
            created += 1
            self.stdout.write(f"  [User] {uid} - {item['nickname']} ({item['phone']})")

        self.stdout.write(self.style.SUCCESS(f"Created {created} users from JSON"))

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

    def _seed_listings(self):
        """围绕演示流程创建市场挂单 - 增加数据量"""
        if Listing.objects.exists():
            self.stdout.write("  Listings already exist, skip")
            return

        # 获取所有用户
        users = list(User.objects.all().order_by("user_id"))
        if len(users) < 10:
            self.stdout.write(self.style.ERROR("Need at least 10 users"))
            return

        products = list(Product.objects.filter(reference_price__gt=0))
        if len(products) < 20:
            self.stdout.write(self.style.ERROR("Need at least 20 products"))
            return

        # 为10个用户分配资产并发布挂单
        listing_users = users[:10]  # 前10个用户作为卖家
        created = 0
        all_new_assets = []

        for i, user in enumerate(listing_users):
            # 每个用户创建1-2个资产和挂单
            num_listings = 2 if i < 5 else 1  # 前5个用户各2个挂单，后5个各1个

            for j in range(num_listings):
                product_idx = (i * 2 + j) % len(products)
                product = products[product_idx]

                # 创建资产
                asset_id = self._generate_asset_id()
                acquire_price = float(product.reference_price) * random.uniform(0.7, 0.9)
                asset = UserAsset.objects.create(
                    asset_id=asset_id,
                    owner=user,
                    product=product,
                    quantity=1,
                    acquire_price=round(acquire_price, 2),
                    current_value=product.reference_price,
                    status="holding",
                    source="演示数据",
                )
                all_new_assets.append(asset)

                # 创建挂单
                price = float(product.reference_price) * random.uniform(0.85, 1.15)
                listing_id = self._generate_listing_id()
                Listing.objects.create(
                    listing_id=listing_id,
                    seller=user,
                    asset=asset,
                    product=product,
                    price=round(price, 2),
                    quantity=1,
                    description=f"【演示】{user.nickname}出售 {product.name}",
                    status="active",
                )
                asset.status = "selling"
                asset.save(update_fields=["status", "updated_at"])
                created += 1
                self.stdout.write(f"  [Listing] {user.nickname} -> {listing_id} - {product.name}")

        self.stdout.write(self.style.SUCCESS(f"Created {created} listings"))
        return all_new_assets

    def _seed_orders(self):
        """围绕演示流程创建订单 - 增加数据量"""
        if Order.objects.exists():
            self.stdout.write("  Orders already exist, skip")
            return

        # 获取所有用户和活跃挂单
        users = list(User.objects.all().order_by("user_id"))
        active_listings = list(Listing.objects.filter(status="active").select_related("seller", "product", "asset"))

        if len(users) < 5 or len(active_listings) < 5:
            self.stdout.write(self.style.ERROR("Not enough users/listings"))
            return

        now = timezone.now()
        created = 0

        # === 已完成订单（6个）===
        completed_listings = active_listings[:6]
        for i, listing in enumerate(completed_listings):
            buyer = users[(i + 5) % len(users)]  # 买家从第5个用户开始轮换
            if buyer.user_id == listing.seller.user_id:
                buyer = users[(i + 6) % len(users)]

            order_id = self._generate_order_id()
            order = Order.objects.create(
                order_id=order_id,
                buyer=buyer,
                seller=listing.seller,
                listing=listing,
                product=listing.product,
                quantity=1,
                amount=listing.price,
                status="completed",
                paid_at=now - timedelta(days=random.randint(3, 10)),
                completed_at=now - timedelta(days=random.randint(1, 3)),
            )
            PaymentRecord.objects.create(
                payment_id=self._generate_payment_id(),
                order=order, payer=buyer, amount=order.amount,
                pay_method="simulated", status="success",
            )
            for from_s, to_s, note in [("", "created", "订单创建"), ("created", "paid", "支付完成"), ("paid", "completed", "交易完成")]:
                OrderStatusLog.objects.create(
                    log_id=self._generate_order_log_id(), order=order,
                    from_status=from_s, to_status=to_s,
                    operator=buyer if to_s != "completed" else listing.seller, note=note,
                )
            listing.status = "sold"
            listing.save(update_fields=["status", "updated_at"])
            listing.asset.status = "sold"
            listing.asset.save(update_fields=["status", "updated_at"])
            created += 1
            self.stdout.write(f"  [Order] {buyer.nickname}购买{listing.seller.nickname}的{listing.product.name} -> 已完成")

        # === 已支付订单（3个）===
        paid_listings = active_listings[6:9]
        for i, listing in enumerate(paid_listings):
            buyer = users[(i + 10) % len(users)]
            if buyer.user_id == listing.seller.user_id:
                buyer = users[(i + 11) % len(users)]

            order_id = self._generate_order_id()
            order = Order.objects.create(
                order_id=order_id,
                buyer=buyer,
                seller=listing.seller,
                listing=listing,
                product=listing.product,
                quantity=1,
                amount=listing.price,
                status="paid",
                paid_at=now - timedelta(days=random.randint(1, 3)),
            )
            PaymentRecord.objects.create(
                payment_id=self._generate_payment_id(),
                order=order, payer=buyer, amount=order.amount,
                pay_method="simulated", status="success",
            )
            for from_s, to_s, note in [("", "created", "订单创建"), ("created", "paid", "支付完成")]:
                OrderStatusLog.objects.create(
                    log_id=self._generate_order_log_id(), order=order,
                    from_status=from_s, to_status=to_s, operator=buyer, note=note,
                )
            listing.status = "locked"
            listing.save(update_fields=["status", "updated_at"])
            created += 1
            self.stdout.write(f"  [Order] {buyer.nickname}购买{listing.seller.nickname}的{listing.product.name} -> 已支付")

        # === 待支付订单（3个）===
        created_listings = active_listings[9:12] if len(active_listings) > 11 else active_listings[9:]
        for i, listing in enumerate(created_listings):
            buyer = users[(i + 15) % len(users)]
            if buyer.user_id == listing.seller.user_id:
                buyer = users[(i + 16) % len(users)]

            order_id = self._generate_order_id()
            Order.objects.create(
                order_id=order_id,
                buyer=buyer,
                seller=listing.seller,
                listing=listing,
                product=listing.product,
                quantity=1,
                amount=listing.price,
                status="created",
            )
            OrderStatusLog.objects.create(
                log_id=self._generate_order_log_id(), order=Order.objects.get(order_id=order_id),
                from_status="", to_status="created", operator=buyer, note="订单创建，等待支付",
            )
            created += 1
            self.stdout.write(f"  [Order] {buyer.nickname}购买{listing.seller.nickname}的{listing.product.name} -> 待支付")

        # === 已取消订单（3个）===
        cancelled_listings = active_listings[12:15] if len(active_listings) > 14 else active_listings[12:]
        for i, listing in enumerate(cancelled_listings):
            buyer = users[(i + 18) % len(users)]
            if buyer.user_id == listing.seller.user_id:
                buyer = users[(i + 19) % len(users)]

            order_id = self._generate_order_id()
            order = Order.objects.create(
                order_id=order_id,
                buyer=buyer,
                seller=listing.seller,
                listing=listing,
                product=listing.product,
                quantity=1,
                amount=listing.price,
                status="cancelled",
            )
            reasons = ["买家取消订单", "卖家取消订单", "超时未支付自动取消"]
            for from_s, to_s, note in [("", "created", "订单创建"), ("created", "cancelled", reasons[i % 3])]:
                OrderStatusLog.objects.create(
                    log_id=self._generate_order_log_id(), order=order,
                    from_status=from_s, to_status=to_s, operator=buyer, note=note,
                )
            created += 1
            self.stdout.write(f"  [Order] {buyer.nickname}取消{listing.seller.nickname}的订单 -> 已取消")

        self.stdout.write(self.style.SUCCESS(f"Created {created} orders"))

    def _seed_exchanges(self):
        """围绕演示流程创建换物请求 - 增加数据量"""
        if ExchangeRequest.objects.exists():
            self.stdout.write("  Exchange requests already exist, skip")
            return

        # 获取所有用户
        users = list(User.objects.all().order_by("user_id"))
        products = list(Product.objects.filter(reference_price__gt=0))

        if len(users) < 10 or len(products) < 10:
            self.stdout.write(self.style.ERROR("Not enough users/products"))
            return

        now = timezone.now()
        created_requests = 0
        created_matches = 0

        # 为换物创建资产
        exchange_assets = []
        for i in range(12):
            user = users[i + 5]  # 从第5个用户开始
            product = products[i + 10] if i + 10 < len(products) else products[i]
            asset_id = self._generate_asset_id()
            asset = UserAsset.objects.create(
                asset_id=asset_id, owner=user, product=product,
                quantity=1, acquire_price=float(product.reference_price) * 0.8,
                current_value=product.reference_price,
                status="holding", source="演示数据-换物",
            )
            exchange_assets.append((user, asset))

        # === 已完成换物（3个）===
        for i in range(3):
            user1, asset1 = exchange_assets[i * 2]
            user2, asset2 = exchange_assets[i * 2 + 1]

            exchange_id = self._generate_exchange_id()
            req = ExchangeRequest.objects.create(
                exchange_id=exchange_id,
                owner=user1,
                offered_asset=asset1,
                target_condition=f"希望换 {asset2.product.name} 或同IP商品",
                price_difference_note="可接受小幅度补差",
                status="completed",
            )
            match_id = self._generate_match_id()
            ExchangeMatch.objects.create(
                match_id=match_id, request=req,
                applicant=user2, applicant_asset=asset2,
                status="accepted",
            )
            # 交换资产归属
            asset1.owner, asset2.owner = asset2.owner, asset1.owner
            asset1.save(update_fields=["owner", "updated_at"])
            asset2.save(update_fields=["owner", "updated_at"])
            created_requests += 1
            created_matches += 1
            self.stdout.write(f"  [Exchange] {user1.nickname} <-> {user2.nickname} -> 已完成")

        # === 匹配中换物（3个）===
        for i in range(3):
            user1, asset1 = exchange_assets[i * 2 + 6]
            user2, asset2 = exchange_assets[i * 2 + 7]

            exchange_id = self._generate_exchange_id()
            req = ExchangeRequest.objects.create(
                exchange_id=exchange_id,
                owner=user1,
                offered_asset=asset1,
                target_condition=f"希望换 {asset2.product.name} 或类似手办",
                price_difference_note="可协商补差",
                status="matched",
            )
            asset1.status = "exchanging"
            asset1.save(update_fields=["status", "updated_at"])
            match_id = self._generate_match_id()
            ExchangeMatch.objects.create(
                match_id=match_id, request=req,
                applicant=user2, applicant_asset=asset2,
                status="pending",
            )
            created_requests += 1
            created_matches += 1
            self.stdout.write(f"  [Exchange] {user1.nickname} <-> {user2.nickname} -> 匹配中")

        # === 挂单中换物（4个）===
        for i in range(4):
            user, asset = exchange_assets[i]
            product = products[i + 20] if i + 20 < len(products) else products[i]

            exchange_id = self._generate_exchange_id()
            ExchangeRequest.objects.create(
                exchange_id=exchange_id,
                owner=user,
                offered_asset=asset,
                target_condition=f"希望换 {product.name} 或同系列商品",
                price_difference_note="面议",
                status="active",
            )
            created_requests += 1
            self.stdout.write(f"  [Exchange] {user.nickname}发布换物请求 -> 挂单中")

        # === 已取消换物（2个）===
        for i in range(2):
            user, asset = exchange_assets[i + 4]

            exchange_id = self._generate_exchange_id()
            ExchangeRequest.objects.create(
                exchange_id=exchange_id,
                owner=user,
                offered_asset=asset,
                target_condition="希望换限定款",
                price_difference_note="不限",
                status="cancelled",
            )
            created_requests += 1
            self.stdout.write(f"  [Exchange] {user.nickname}发布换物请求 -> 已取消")

        self.stdout.write(self.style.SUCCESS(f"Created {created_requests} exchanges, {created_matches} matches"))

    def _seed_teams(self):
        """围绕演示流程创建拼团 - 增加数据量"""
        if TeamProject.objects.exists():
            self.stdout.write("  Team projects already exist, skip")
            return

        # 获取所有用户
        users = list(User.objects.all().order_by("user_id"))
        products = list(Product.objects.filter(reference_price__gt=0, status="active"))

        if len(users) < 10 or len(products) < 10:
            self.stdout.write(self.style.ERROR("Not enough users/products"))
            return

        now = timezone.now()
        created_teams = 0
        created_participants = 0

        # === 成功拼团（4个）===
        for i in range(4):
            creator = users[i + 4]  # 从第4个用户开始
            product = products[i]
            target_count = random.choice([3, 4, 5])
            team_price = round(float(product.reference_price) * random.uniform(0.70, 0.85), 2)

            team_id = self._generate_team_id()
            team = TeamProject.objects.create(
                team_id=team_id, product=product, creator=creator,
                target_count=target_count, current_count=target_count,
                team_price=team_price,
                deadline=now - timedelta(days=random.randint(1, 3)),
                status="success",
            )
            # 添加参与者
            participants = [u for u in users if u.user_id != creator.user_id][:target_count - 1]
            for participant in participants:
                TeamParticipant.objects.create(
                    participant_id=self._generate_participant_id(),
                    team=team, user=participant, status="joined",
                )
                created_participants += 1
            created_teams += 1
            self.stdout.write(f"  [Team] {creator.nickname}发起拼团 -> 成功 ({target_count}人)")

        # === 招募中拼团（4个）===
        for i in range(4):
            creator = users[i + 8]
            product = products[i + 4]
            target_count = random.choice([4, 5, 6, 8])
            current_count = random.randint(1, target_count - 1)
            team_price = round(float(product.reference_price) * random.uniform(0.70, 0.85), 2)

            team_id = self._generate_team_id()
            team = TeamProject.objects.create(
                team_id=team_id, product=product, creator=creator,
                target_count=target_count, current_count=current_count,
                team_price=team_price,
                deadline=now + timedelta(days=random.randint(3, 14)),
                status="recruiting",
            )
            # 添加已有参与者
            participants = [u for u in users if u.user_id != creator.user_id][:current_count - 1]
            for participant in participants:
                TeamParticipant.objects.create(
                    participant_id=self._generate_participant_id(),
                    team=team, user=participant, status="joined",
                )
                created_participants += 1
            created_teams += 1
            self.stdout.write(f"  [Team] {creator.nickname}发起拼团 -> 招募中 ({current_count}/{target_count})")

        # === 失败拼团（3个）===
        for i in range(3):
            creator = users[i + 12]
            product = products[i + 8]
            target_count = random.choice([5, 6, 8])
            current_count = random.randint(2, target_count - 2)
            team_price = round(float(product.reference_price) * random.uniform(0.70, 0.80), 2)

            team_id = self._generate_team_id()
            team = TeamProject.objects.create(
                team_id=team_id, product=product, creator=creator,
                target_count=target_count, current_count=current_count,
                team_price=team_price,
                deadline=now - timedelta(days=random.randint(1, 5)),
                status="failed",
            )
            participants = [u for u in users if u.user_id != creator.user_id][:current_count - 1]
            for participant in participants:
                TeamParticipant.objects.create(
                    participant_id=self._generate_participant_id(),
                    team=team, user=participant, status="joined",
                )
                created_participants += 1
            created_teams += 1
            self.stdout.write(f"  [Team] {creator.nickname}发起拼团 -> 失败 ({current_count}/{target_count})")

        # === 已取消拼团（3个）===
        for i in range(3):
            creator = users[i + 15]
            product = products[i + 11] if i + 11 < len(products) else products[i]
            target_count = random.choice([3, 4, 5])
            team_price = round(float(product.reference_price) * random.uniform(0.72, 0.82), 2)

            team_id = self._generate_team_id()
            TeamProject.objects.create(
                team_id=team_id, product=product, creator=creator,
                target_count=target_count, current_count=1,
                team_price=team_price,
                deadline=now + timedelta(days=random.randint(3, 10)),
                status="cancelled",
            )
            created_teams += 1
            self.stdout.write(f"  [Team] {creator.nickname}发起拼团 -> 已取消")

        self.stdout.write(self.style.SUCCESS(f"Created {created_teams} teams, {created_participants} participants"))

    def _seed_credits(self):
        """围绕演示流程创建信用变动记录 - 为所有用户创建"""
        if CreditRecord.objects.exists():
            self.stdout.write("  Credit records already exist, skip")
            return

        # 获取所有用户
        users = list(User.objects.all().order_by("user_id"))
        if not users:
            self.stdout.write(self.style.ERROR("No users found"))
            return

        now = timezone.now()
        created = 0

        # 获取已完成订单用于关联
        completed_orders = list(Order.objects.filter(status="completed"))
        cancelled_orders = list(Order.objects.filter(status="cancelled"))

        # 信用变动模板
        positive_templates = [
            (+5, "完成交易，信用+5"),
            (+3, "获得买家好评，信用+3"),
            (+2, "及时发货，信用+2"),
            (+2, "及时确认收货，信用+2"),
            (+3, "积极参与社区活动，信用+3"),
            (+5, "连续交易良好记录，信用+5"),
            (+3, "完成换物交易，信用+3"),
            (+5, "成功组织拼团，信用+5"),
            (+3, "参与拼团成功，信用+3"),
        ]

        negative_templates = [
            (-5, "取消订单，信用-5"),
            (-3, "未按时发货，信用-3"),
            (-10, "交易纠纷，信用-10"),
            (-8, "恶意评价，信用-8"),
            (-15, "虚假描述，信用-15"),
        ]

        # 为每个用户创建信用记录
        for i, user in enumerate(users):
            # 根据用户角色确定信用记录数量和类型
            if i == 0:
                # 测试用户：良好卖家
                records = [
                    (+5, "完成交易，信用+5", completed_orders[0] if completed_orders else None),
                    (+3, "获得买家好评，信用+3", None),
                    (+2, "及时发货，信用+2", None),
                    (+5, "连续交易良好记录，信用+5", None),
                    (-5, "取消订单，信用-5", cancelled_orders[0] if cancelled_orders else None),
                ]
            elif i == 19:
                # 小透明：信用较低用户
                records = [
                    (-10, "交易纠纷，信用-10", None),
                    (-8, "恶意评价，信用-8", None),
                    (-15, "虚假描述，信用-15", None),
                    (-5, "未按时发货，信用-5", None),
                ]
            elif i < 5:
                # 前5个用户：活跃用户，3-4条正向记录
                num_records = random.randint(3, 4)
                records = [(random.choice(positive_templates)[0], random.choice(positive_templates)[1], None) for _ in range(num_records)]
            elif i < 10:
                # 6-10用户：普通用户，2-3条记录（偶尔有负向）
                num_records = random.randint(2, 3)
                records = []
                for _ in range(num_records):
                    if random.random() < 0.8:
                        template = random.choice(positive_templates)
                    else:
                        template = random.choice(negative_templates)
                    records.append((template[0], template[1], None))
            else:
                # 其他用户：1-2条记录
                num_records = random.randint(1, 2)
                records = [(random.choice(positive_templates)[0], random.choice(positive_templates)[1], None) for _ in range(num_records)]

            # 创建信用记录
            for change, reason, order in records:
                CreditRecord.objects.create(
                    credit_record_id=self._generate_credit_record_id(),
                    user=user, change_value=change, reason=reason,
                    related_order=order,
                    created_at=now - timedelta(days=random.randint(1, 60)),
                )
                created += 1

            self.stdout.write(f"  [Credit] {user.nickname} - {len(records)} records")

        self.stdout.write(self.style.SUCCESS(f"Created {created} credit records"))
