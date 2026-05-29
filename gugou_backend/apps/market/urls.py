from django.urls import path

from .views import (
    ListingCancelView,
    ListingCreateView,
    ListingDetailView,
    ListingListView,
    MyListingListView,
)

urlpatterns = [
    path("", ListingListView.as_view(), name="market-listing-list"),
    path("create/", ListingCreateView.as_view(), name="market-listing-create"),
    path("my/", MyListingListView.as_view(), name="market-listing-my"),
    path("<str:listing_id>/", ListingDetailView.as_view(), name="market-listing-detail"),
    path("<str:listing_id>/cancel/", ListingCancelView.as_view(), name="market-listing-cancel"),
]
