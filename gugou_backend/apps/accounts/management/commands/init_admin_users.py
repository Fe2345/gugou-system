from django.core.management.base import BaseCommand

from apps.accounts.models import User, UserProfile
from apps.common.id_generator import generate_user_id


class Command(BaseCommand):
    help = "初始化管理员测试账号"

    ADMIN_USERS = [
        {"phone": "13900000001", "password": "admin123", "nickname": "系统管理员"},
        {"phone": "13900000002", "password": "admin123", "nickname": "商品审核员"},
        {"phone": "13900000003", "password": "admin123", "nickname": "订单管理员"},
    ]

    def handle(self, *args, **options):
        created = 0
        for u in self.ADMIN_USERS:
            if User.objects.filter(phone=u["phone"]).exists():
                self.stdout.write(self.style.WARNING(f"跳过已存在: {u['phone']}"))
                continue
            user = User(
                user_id=generate_user_id(),
                phone=u["phone"],
                nickname=u["nickname"],
                role=User.Role.ADMIN,
                status=User.Status.NORMAL,
            )
            user.set_password(u["password"])
            user.save()
            UserProfile.objects.create(user=user)
            created += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"已创建管理员: {u['phone']} / {u['password']} "
                    f"(id={user.user_id}, nickname={u['nickname']})"
                )
            )

        if created == 0:
            self.stdout.write("没有需要新建的账号")
        else:
            self.stdout.write(self.style.SUCCESS(f"\n共创建 {created} 个管理员账号"))
