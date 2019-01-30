# sku_manage/urls.py
from django.conf.urls import url
from sku_manage import views
from django.urls import path

urlpatterns = [
	path('search/ingredient/', views.IngredientView, name='Ingredient'),
	path('search/productline/', views.ProductLineView, name='ProductLine'),
	path('search/sku/', views.SKUView, name='SKU'),
	path('search/ingredientqty/', views.IngredientQtyView, name='IngredientQty'),
	path('search/', views.search, name='search'),
	path('authout/', views.authout, name='authout'),
	path('search/ingredient/<name>/', views.IngredientDetailView.as_view(), name='ingredient_detail')
	path('search/sku/<int:sku_num>/', views.SKUDetailView.as_view(), name='sku_detail')
]
