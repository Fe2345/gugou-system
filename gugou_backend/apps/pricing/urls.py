from django.urls import path

from .views import PriceQueryView, PriceHotView, MyAssetPricesView

urlpatterns = [
    path("query/", PriceQueryView.as_view()),
    path("hot/", PriceHotView.as_view()),
    path("my-assets/", MyAssetPricesView.as_view()),
]
