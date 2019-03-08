from django.shortcuts import render
from sku_manage.models import SKU

def sku_drilldown(request, pk):
	context = dict()
	context['sku'] = SKU.objects.get(pk=pk)
	return render(request, 'sales/sku_drilldown.html', context)