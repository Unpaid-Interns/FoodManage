# sku_manage/urls.py
from django.conf.urls import url
from sku_manage import views
from django.urls import path

urlpatterns = [
	path('search/', views.search, name='search'),
	path('search/ingredient/', views.IngredientView, name='Ingredient'),
	path('search/productline/', views.ProductLineView, name='ProductLine'),
	path('search/sku/', views.SKUView, name='SKU'),
	path('search/formula/', views.FormulaView, name='formula'),
	path('search/manufacturingline/', views.ManufacturingLineView, name='ManufacturingLine'),
	path('search/ingredient/<int:pk>/', views.IngredientDetailView.as_view(), name='ingredient_detail'),
	path('search/productline/<int:pk>/', views.ProductLineDetailView.as_view(), name='product_line_detail'),
	path('search/sku/<int:pk>/', views.SKUDetailView.as_view(), name='sku_detail'),
	path('search/formula/<int:pk>/', views.FormulaDetailView.as_view(), name='formula_detail'),
	path('search/manufacturingline/<int:pk>/', views.ManufacturingLineDetailView.as_view(), name='mfg_line_detail'),
	path('authout/', views.authout, name='authout'),
	path('populate/', views.populate, name='populate')
]
