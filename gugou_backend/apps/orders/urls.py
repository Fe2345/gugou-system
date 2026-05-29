from django.urls import path

from .views import (
    OrderCancelView,
    OrderCompleteView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    PaymentCreateView,
    PaymentSuccessView,
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),
    path("create/", OrderCreateView.as_view(), name="order-create"),
    path("<str:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("<str:order_id>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("<str:order_id>/complete/", OrderCompleteView.as_view(), name="order-complete"),
    path("<str:order_id>/payment/", PaymentCreateView.as_view(), name="order-payment-create"),
    path("<str:order_id>/payment/<str:payment_id>/success/", PaymentSuccessView.as_view(), name="order-payment-success"),
]
