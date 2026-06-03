from django.urls import path

from .views import (
    AdminExchangeCancelView,
    AdminExchangeCompleteView,
    AdminExchangeDetailView,
    AdminExchangeExpireView,
    AdminExchangeHandleAbnormalView,
    AdminExchangeListView,
    ExchangeCancelView,
    ExchangeCompleteView,
    ExchangeMatchAcceptView,
    ExchangeMatchCreateView,
    ExchangeMatchRejectView,
    ExchangeRequestCreateView,
    ExchangeRequestDetailView,
    ExchangeRequestListView,
    MyExchangeRequestListView,
)

urlpatterns = [
    # 用户端接口
    path("", ExchangeRequestListView.as_view(), name="exchange-list"),
    path("create/", ExchangeRequestCreateView.as_view(), name="exchange-create"),
    path("my/", MyExchangeRequestListView.as_view(), name="exchange-my"),
    path("<str:exchange_id>/", ExchangeRequestDetailView.as_view(), name="exchange-detail"),
    path("<str:exchange_id>/cancel/", ExchangeCancelView.as_view(), name="exchange-cancel"),
    path("<str:exchange_id>/complete/", ExchangeCompleteView.as_view(), name="exchange-complete"),
    path("<str:exchange_id>/match/", ExchangeMatchCreateView.as_view(), name="exchange-match-create"),
    path("<str:exchange_id>/match/<str:match_id>/accept/", ExchangeMatchAcceptView.as_view(), name="exchange-match-accept"),
    path("<str:exchange_id>/match/<str:match_id>/reject/", ExchangeMatchRejectView.as_view(), name="exchange-match-reject"),
    # 管理员端接口
    path("admin/list/", AdminExchangeListView.as_view(), name="admin-exchange-list"),
    path("admin/<str:exchange_id>/", AdminExchangeDetailView.as_view(), name="admin-exchange-detail"),
    path("admin/<str:exchange_id>/expire/", AdminExchangeExpireView.as_view(), name="admin-exchange-expire"),
    path("admin/<str:exchange_id>/cancel/", AdminExchangeCancelView.as_view(), name="admin-exchange-cancel"),
    path("admin/<str:exchange_id>/complete/", AdminExchangeCompleteView.as_view(), name="admin-exchange-complete"),
    path("admin/<str:exchange_id>/handle-abnormal/", AdminExchangeHandleAbnormalView.as_view(), name="admin-exchange-handle-abnormal"),
]
