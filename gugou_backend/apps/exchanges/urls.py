from django.urls import path

from .views import (
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
    path("", ExchangeRequestListView.as_view(), name="exchange-list"),
    path("create/", ExchangeRequestCreateView.as_view(), name="exchange-create"),
    path("my/", MyExchangeRequestListView.as_view(), name="exchange-my"),
    path("<str:exchange_id>/", ExchangeRequestDetailView.as_view(), name="exchange-detail"),
    path("<str:exchange_id>/cancel/", ExchangeCancelView.as_view(), name="exchange-cancel"),
    path("<str:exchange_id>/complete/", ExchangeCompleteView.as_view(), name="exchange-complete"),
    path("<str:exchange_id>/match/", ExchangeMatchCreateView.as_view(), name="exchange-match-create"),
    path("<str:exchange_id>/match/<str:match_id>/accept/", ExchangeMatchAcceptView.as_view(), name="exchange-match-accept"),
    path("<str:exchange_id>/match/<str:match_id>/reject/", ExchangeMatchRejectView.as_view(), name="exchange-match-reject"),
]
