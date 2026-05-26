from django.urls import path

from .views import AssetListView, AssetDetailView, AssetOperateView

urlpatterns = [
    path("", AssetListView.as_view(), name="assets-list"),
    path("<str:asset_id>/", AssetDetailView.as_view(), name="assets-detail"),
    path("<str:asset_id>/operate/", AssetOperateView.as_view(), name="assets-operate"),
]
