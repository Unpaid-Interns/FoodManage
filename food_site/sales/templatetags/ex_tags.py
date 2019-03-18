from django import template

register = template.Library()

@register.filter
def mult(value, arg):
	return value * arg

@register.filter
def hours(value):
	return value.seconds//3600

@register.filter
def year(value):
	return value.isocalendar()[0]

@register.filter
def week(value):
	return value.isocalendar()[1]

@register.filter
def lookup(value, arg):
	return value[arg]

@register.filter
def rows(value):
	return value.rows

