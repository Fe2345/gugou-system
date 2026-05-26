from django.urls import path

from .views import ProductListView, ProductDetailView, ProductCategoriesView

urlpatterns = [
    path("", ProductListView.as_view(), name="products-list"),
    path("categories/", ProductCategoriesView.as_view(), name="products-categories"),
    path("<str:product_id>/", ProductDetailView.as_view(), name="products-detail"),
]
