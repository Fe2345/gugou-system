from django.core.management.base import BaseCommand

from apps.credits.services import monthly_credit_recovery


class Command(BaseCommand):
    help = "执行月度信用分恢复：信用分 < 80 的用户自动 +2 分（上限80分）"

    def handle(self, *args, **options):
        count = monthly_credit_recovery()
        self.stdout.write(self.style.SUCCESS(f"月度信用恢复完成，影响 {count} 名用户"))
