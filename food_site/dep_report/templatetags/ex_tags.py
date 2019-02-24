from django import template

register = template.Library()

@register.filter
def mult(value, arg):
	return round(value * arg, 12)

@register.filter
def hours(value):
	return value.seconds//3600

