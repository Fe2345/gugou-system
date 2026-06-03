from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls_auth")),
    path("api/user/", include("apps.accounts.urls_user")),
    path("api/admin/goods/", include("apps.products.admin_urls")),
    path("api/admin/users/", include("apps.accounts.admin_urls")),
    path("api/admin/prices/", include("apps.pricing.admin_urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/assets/", include("apps.assets.urls")),
    path("api/market/", include("apps.market.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/exchanges/", include("apps.exchanges.urls")),
    path("api/teams/", include("apps.teams.urls")),
    path("api/pricing/", include("apps.pricing.urls")),
    path("api/credits/", include("apps.credits.urls")),
    path("api/operations/", include("apps.operations.urls")),
    path("api/", include("apps.addresses.urls")),
]

# 开发环境提供media文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
