from django.urls import path

from .admin_views import (
    AdminGoodsApproveView,
    AdminGoodsEditView,
    AdminGoodsListView,
    AdminGoodsOfflineView,
    AdminGoodsRejectView,
)

urlpatterns = [
    path("", AdminGoodsListView.as_view(), name="admin-goods-list"),
    path("<str:product_id>/approve/", AdminGoodsApproveView.as_view(), name="admin-goods-approve"),
    path("<str:product_id>/reject/", AdminGoodsRejectView.as_view(), name="admin-goods-reject"),
    path("<str:product_id>/offline/", AdminGoodsOfflineView.as_view(), name="admin-goods-offline"),
    path("<str:product_id>/edit/", AdminGoodsEditView.as_view(), name="admin-goods-edit"),
]
