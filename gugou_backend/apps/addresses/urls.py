from django.urls import path

from .views import AddressDetailView, AddressListView, DivisionListView

urlpatterns = [
    # 行政区划（公开）
    path("divisions/", DivisionListView.as_view(), name="division-list"),
    # 用户地址
    path("user/addresses/", AddressListView.as_view(), name="address-list"),
    path("user/addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
]
