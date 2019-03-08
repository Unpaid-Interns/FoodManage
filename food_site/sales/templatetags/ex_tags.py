from django import template

register = template.Library()

@register.filter
def mult(value, arg):
	return value * arg

@register.filter
def year(value):
	return value.isocalendar()[0]

@register.filter
def week(value):
	return value.isocalendar()[1]
