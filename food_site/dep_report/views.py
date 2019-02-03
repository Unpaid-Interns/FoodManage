import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse
from sku_manage.models import Ingredient
from django_tables2 import RequestConfig, paginators
from .tables import IngredientTable
from .filters import IngredientFilter


def ingr_dep_menu(request):
	queryset = Ingredient.objects.all()
	f = IngredientFilter(request.GET, queryset=queryset)
	table = IngredientTable(f.qs)

	context = {
		'table': table, 
		'filter': f, 
		'paginated': True,
	}
	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25
	}
	if request.method == 'GET' and 'remove_pagination' in request.GET:
		print(request.GET)
		paginate = False
		context['paginated'] = False


	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'dep_report/data.html', context)


def ingr_dep_generate(request):
	if request.method == 'POST' and 'choice' in request.POST:
		request.session['choices'] = request.POST.getlist('choice')
		return redirect('ingr_dep_report')
	else:
		return redirect('ingr_dep')


def ingr_dep_report(request):
	choices = request.session.get('choices')
	ingredients = Ingredient.objects.filter(id__in=choices)

	if request.method == 'POST':
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="report.csv"'
		writer = csv.writer(response)
		writer.writerow(['Ingredient', 'SKUs'])
		for ingredient in ingredients.all():
			row = [str(ingredient)]
			for choice in ingredient.ingredientqty_set.all():
				row.append(str(choice.sku))
			writer.writerow(row)
		return response

	context = {'ingredients': ingredients}
	return render(request, 'dep_report/detail.html', context)