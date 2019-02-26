
weight_factors = {
	'Ounce': 32000.0,
	'Pound': 2000.0,
	'Ton': 1.0,
	'Gram': 907185.0,
	'Kilogram': 907.185,
}

volume_factors = {
	'Fluid Ounce': 128.0,
	'Pint': 8.0,
	'Quart': 4.0,
	'Gallon': 1.0,
	'Milliliter': 3785.41,
	'Liter': 3.78541,
}

count_factors = {
	'Count': 1.0,
}

def convert(value, unit_in, unit_out):
	if unit_in in weight_factors and unit_out in weight_factors:
		return value*weight_factors[unit_out]/weight_factors[unit_in]
	if unit_in in volume_factors and unit_out in volume_factors:
		return value*volume_factors[unit_out]/volume_factors[unit_in]
	if unit_in in count_factors and unit_out in count_factors:
		return value*count_factors[unit_out]/count_factors[unit_in]
	raise Exception('Units are not of same type')
