from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls_auth")),
    path("api/user/", include("apps.accounts.urls_user")),
    path("api/products/", include("apps.products.urls")),
    path("api/assets/", include("apps.assets.urls")),
    path("api/market/", include("apps.market.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/exchanges/", include("apps.exchanges.urls")),
    path("api/teams/", include("apps.teams.urls")),
    path("api/pricing/", include("apps.pricing.urls")),
    path("api/credits/", include("apps.credits.urls")),
    path("api/operations/", include("apps.operations.urls")),
]
