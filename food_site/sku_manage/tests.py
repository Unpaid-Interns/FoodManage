from django.test import TestCase, TransactionTestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from . import models, ex_data

class ForeignKeyTests(TransactionTestCase):

	def test_sku_correct(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		models.SKU(name='Can O Soup', case_upc='000000000026', unit_upc='000000000013', unit_size='32oz', units_per_case=12, product_line=pl, formula=fo, mfg_rate=1.0).save()

	def test_sku_missing_product_line(self):
		pl = models.ProductLine(name='Soups')
		fo = models.Formula(name='Soup Formula')
		fo.save()
		with self.assertRaisesMessage(ValueError, 'save() prohibited'):
			models.SKU(name='Can O Soup', case_upc='000000000026', unit_upc='000000000013', unit_size='32oz', units_per_case=12, product_line=pl, formula=fo, mfg_rate=1.0).save()

	def test_sku_missing_formula(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		with self.assertRaisesMessage(ValueError, 'save() prohibited'):
			models.SKU(name='Can O Soup', case_upc='000000000026', unit_upc='000000000013', unit_size='32oz', units_per_case=12, product_line=pl, formula=fo, mfg_rate=1.0).save()

	def test_ingredientqty_correct(self):
		i = models.Ingredient(name='Potato', package_size=50, package_size_units='lb.', cost=7.99)
		i.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		models.IngredientQty(formula=fo, ingredient=i, quantity=0.2).save()
		models.IngredientQty(formula=fo, ingredient=i, quantity=0.08).save()
		self.assertIs(models.IngredientQty.objects.count(), 2)


	def test_ingredientqty_missing_formula(self):
		i = models.Ingredient(name='Potato', package_size=50, package_size_units='lb.', cost=7.99)
		i.save()
		fo = models.Formula(name='Soup Formula')
		with self.assertRaisesMessage(ValueError, 'save() prohibited'):
			models.IngredientQty(formula=fo, ingredient=i, quantity=0.2).save()

	def test_ingredientqty_missing_ingredient(self):
		i = models.Ingredient(name='Potato', package_size=50, package_size_units='lb.', cost=7.99)
		fo = models.Formula(name='Soup Formula')
		fo.save()
		with self.assertRaisesMessage(ValueError, 'save() prohibited'):
			models.IngredientQty(formula=fo, ingredient=i, quantity=0.2).save()

	def test_skumfgline_correct(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		sku = models.SKU(name='Can O Soup', sku_num=0, case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0)
		sku.save()
		ml = models.ManufacturingLine(name='Soup Line', shortname='SL1')
		ml.save()
		models.SkuMfgLine(sku=sku, mfg_line=ml)


	def test_skumfgline_missing_sku(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		sku = models.SKU(name='Can O Soup', sku_num=0, case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0)
		ml = models.ManufacturingLine(name='Soup Line', shortname='SL1')
		ml.save()
		models.SkuMfgLine(sku=sku, mfg_line=ml)

	def test_skumfgline_missing_mfgline(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		sku = models.SKU(name='Can O Soup', sku_num=0, case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0)
		sku.save()
		ml = models.ManufacturingLine(name='Soup Line', shortname='SL1')
		models.SkuMfgLine(sku=sku, mfg_line=ml)


class UniquenessTests(TransactionTestCase):

	def test_unique_ingredients(self):
		models.Ingredient(name='Potato', number=0, package_size=50, package_size_units='lb.', cost=7.99).save()
		models.Ingredient(name='Tomato', number=1, package_size=10, package_size_units='lb.', cost=6.99).save()
		self.assertIs(models.Ingredient.objects.count(), 2)

	def test_unique_ingredient_number_generation(self):
		models.Ingredient(name='Potato', number=2, package_size=50, package_size_units='lb.', cost=7.99).save()
		models.Ingredient(name='Tomato', package_size=10, package_size_units='lb.', cost=6.99).save()
		models.Ingredient(name='Carrot', package_size=20, package_size_units='lb.', cost=13.99).save()
		models.Ingredient(name='Milk', package_size=100, package_size_units='gal.', cost=49.99).save()
		self.assertIs(models.Ingredient.objects.count(), 4)

	def test_identical_ingredient_names(self):
		models.Ingredient(name='Potato', number=0, package_size=50, package_size_units='lb.', cost=7.99).save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			models.Ingredient(name='Potato', number=1, package_size=70, package_size_units='lb.', cost=10.99).save()

	def test_identical_ingredient_numbers(self):
		models.Ingredient(name='Potato', number=0, package_size=50, package_size_units='lb.', cost=7.99).save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			models.Ingredient(name='Tomato', number=0, package_size=10, package_size_units='lb.', cost=6.99).save()

	def test_unique_product_line(self):
		models.ProductLine(name='Soups').save()
		models.ProductLine(name='Salads').save()
		self.assertIs(models.ProductLine.objects.count(), 2)

	def test_identical_product_line_names(self):
		models.ProductLine(name='Soups').save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			models.ProductLine(name='Soups').save()

	def test_unique_formula(self):
		models.Formula(name='Tomato Soup Formula', number=0).save()
		models.Formula(name='Potato Soup Formula', number=1).save()
		models.Formula(name='Potato Soup Formula', number=2).save()
		self.assertIs(models.Formula.objects.count(), 3)

	def test_unique_formula_number_generation(self):
		models.Formula(name='Tomato Soup Formula', number=2).save()
		models.Formula(name='Potato Soup Formula').save()
		models.Formula(name='Chicken Noodle Soup Formula').save()
		models.Formula(name='Broccoli Cheddar Soup Formula').save()
		self.assertIs(models.Formula.objects.count(), 4)

	def test_identical_formula_numbers(self):
		models.Formula(name='Tomato Soup Formula', number=2).save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			models.Formula(name='Potato Soup Formula', number=2).save()

	def test_unique_sku(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		models.SKU(name='Can O Soup', sku_num=0, case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0).save()
		models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0).save()
		self.assertIs(models.SKU.objects.count(), 2)

	def test_unique_sku_num_generation(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		models.SKU(name='Can O Soup', sku_num=2, case_upc='000000000000', unit_upc='000000000013', unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0).save()
		models.SKU(name='Can O Soup', case_upc='000000000026', unit_upc='000000000013', unit_size='32oz', units_per_case=12, product_line=pl, formula=fo, mfg_rate=1.0).save()
		models.SKU(name='Can O Soup', case_upc='000000000031', unit_upc='000000000013', unit_size='32oz', units_per_case=4, product_line=pl, formula=fo, mfg_rate=1.0).save()
		models.SKU(name='Can O Soup', case_upc='000000000048', unit_upc='000000000013', unit_size='32oz', units_per_case=64, product_line=pl, formula=fo, mfg_rate=1.0).save()
		self.assertIs(models.SKU.objects.count(), 4)

	def test_identical_sku_nums(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		models.SKU(name='Can O Soup', sku_num=0, case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0).save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			models.SKU(name='Can O Soup', sku_num=0, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0).save()

	def test_identical_case_upcs(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		fo = models.Formula(name='Soup Formula')
		fo.save()
		models.SKU(name='Can O Soup', sku_num=0, case_upc='000000000026', unit_upc='000000000013', unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0).save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			models.SKU(name='Can O Soup', sku_num=1, case_upc='000000000026', unit_upc='000000000013', unit_size='32oz', units_per_case=16, product_line=pl, formula=fo, mfg_rate=1.0).save()

	def test_unique_mfg_line(self):
		models.ManufacturingLine(name='Soup Line', shortname='SL1').save()
		models.ManufacturingLine(name='Soup Line', shortname='SL2').save()
		self.assertIs(models.ManufacturingLine.objects.count(), 2)

	def test_identical_mfg_line_shortname(self):
		models.ManufacturingLine(name='Soup Line', shortname='SL1').save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			models.ManufacturingLine(name='Soup Line', shortname='SL1').save()


class UPCValidationTests(TestCase):

	def test_all_zeros(self):
		models.validate_upc('000000000000')

	def test_correct_check_1(self):
		models.validate_upc('000400000006')

	def test_correct_check_2(self):
		models.validate_upc('004000000008')

	def test_correct_check_3(self):
		models.validate_upc('041104256290')

	def test_correct_check_4(self):
		models.validate_upc('019556793038')

	def test_correct_check_5(self):
		models.validate_upc('766171000439')

	def test_nonzero_first_digit_6(self):
		models.validate_upc('600000000002')

	def test_nonzero_first_digit_7(self):
		models.validate_upc('700000000009')

	def test_nonzero_first_digit_8(self):
		models.validate_upc('800000000006')

	def test_nonzero_first_digit_9(self):
		models.validate_upc('900000000003')

	def test_bad_check_1(self):
		with self.assertRaisesMessage(ValidationError, 'UPC check digit is not valid'):
			models.validate_upc('000000000001')

	def test_bad_check_2(self):
		with self.assertRaisesMessage(ValidationError, 'UPC check digit is not valid'):
			models.validate_upc('000000010000')

	def test_bad_first_digit_1(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc('100000000000')

	def test_bad_first_digit_2(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc('200000000000')

	def test_bad_first_digit_3(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc('300000000000')

	def test_bad_first_digit_4(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc('400000000000')

	def test_bad_first_digit_5(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc('500000000000')

	def test_bad_character(self):
		with self.assertRaisesMessage(ValidationError, 'UPC must only contain numbers'):
			models.validate_upc('+00000000000')

	def test_too_short(self):
		with self.assertRaisesMessage(ValidationError, 'UPC must be 12 digits long'):
			models.validate_upc('00000000000')

	def test_too_long(self):
		with self.assertRaisesMessage(ValidationError, 'UPC must be 12 digits long'):
			models.validate_upc('0000000000000')


class DataSaveTests(TestCase):

	def test_large_save(self):
		ex_data.load_data()

	def check_soup_ingredient_count(self):
		soup = models.Formula.filter(name__icontains='Soup')
		self.assertIs(models.IngredientQty.filter(formula__in=soup).count(), 22)

	def check_num_skus_with_salt(self):
		salt = models.Ingredient.filter(name='Salt')[0]
		self.assertIs(models.IngredientQty.filter(ingredient=salt).count(), 6)

	def check_soup_mfg_line_count(self):
		soup = models.SKU.filter(name__icontains='Soup')
		self.assertIs(models.ManufacturingLine.filter(skumfgline__sku__in=soup).count(), 2)


class ViewTests(TestCase):

	def load_data(self):
		ex_data.load_data()

	def test_ingr_filters(self):
		response = self.client.get("Ingredient")
		skus = models.SKU.objects.all()
		for item in skus:
			self.assertInHTML(item.__str__() + '</option>', response.content)

	def test_product_line_filters(self):
		response = self.client.get("ProductLine")
		skus = models.SKU.objects.all()
		for item in skus:
			self.assertInHTML(item.__str__() + '</option>', response.content)

	def test_sku_filters(self):
		response = self.client.get("SKU")
		ingredients = models.Ingredient.objects.all()
		for item in ingredients:
			self.assertInHTML(item.__str__() + '</option>', response.content)
		product_lines = models.ProductLine.objects.all()
		for item in product_lines:
			self.assertInHTML(item.__str__() + '</option>', response.content)

	def test_formula_filters(self):
		response = self.client.get("formula")
		ingredients = models.Ingredient.objects.all()
		for item in ingredients:
			self.assertInHTML(item.__str__() + '</option>', response.content)
		skus = models.SKU.objects.all()
		for item in skus:
			self.assertInHTML(item.__str__() + '</option>', response.content)

	def test_mfg_line_filters(self):
		response = self.client.get("ProductLine")
		skus = models.SKU.objects.all()
		for item in skus:
			self.assertInHTML(item.__str__() + '</option>', response.content)

