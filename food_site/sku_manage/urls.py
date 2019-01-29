# sku_manage/urls.py
from django.conf.urls import url
from sku_manage import views
from django.urls import path

urlpatterns = [
	path('search/ingredient/', views.IngredientView, name='Ingredient'),
	path('search/productline/', views.ProductLineView.as_view(), name='ProductLine'),
	path('search/sku/', views.SKUView.as_view(), name='SKU'),
	path('search/ingredientqty/', views.IngredientQtyView.as_view(), name='IngredientQty'),
	path('search/', views.search, name='search'),
	path('authout/', views.authout, name='authout'),
]
