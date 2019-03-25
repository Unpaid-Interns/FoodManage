# sku_manage/urls.py
from django.conf.urls import url
from sku_manage import views
from django.urls import path

urlpatterns = [
	path('', views.search, name='search'),
	path('ingredient/', views.IngredientView, name='Ingredient'),
	path('productline/', views.ProductLineView, name='ProductLine'),
	path('sku/', views.SKUView, name='SKU'),
	path('formula/', views.FormulaView, name='formula'),
	path('manufacturingline/', views.ManufacturingLineView, name='ManufacturingLine'),
	path('ingredient/<int:pk>/', views.IngredientDetailView.as_view(), name='ingredient_detail'),
	path('productline/<int:pk>/', views.ProductLineDetailView.as_view(), name='product_line_detail'),
	path('sku/<int:pk>/', views.SKUDetailView.as_view(), name='sku_detail'),
	path('formula/<int:pk>/', views.FormulaDetailView.as_view(), name='formula_detail'),
	path('manufacturingline/<int:pk>/', views.ManufacturingLineDetailView.as_view(), name='mfg_line_detail'),
]
