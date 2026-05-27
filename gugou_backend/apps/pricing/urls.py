from django.urls import path

from .views import PriceQueryView, PriceHotView

urlpatterns = [
    path("query/", PriceQueryView.as_view()),
    path("hot/", PriceHotView.as_view()),
]
