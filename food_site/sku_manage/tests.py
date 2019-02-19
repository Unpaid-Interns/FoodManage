from django.test import TestCase, TransactionTestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from . import models


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
		potato = models.Ingredient(name='Potato', package_size=10, package_size_units='lb.', cost=100)
		potato.save()
		tomato = models.Ingredient(name='Tomato', package_size=10, package_size_units='lb.', cost=100)
		tomato.save()
		carrot = models.Ingredient(name='Carrot', package_size=10, package_size_units='lb.', cost=100)
		carrot.save()
		pasta = models.Ingredient(name='Pasta', package_size=10, package_size_units='lb.', cost=100)
		pasta.save()
		chicken = models.Ingredient(name='Chicken', package_size=10, package_size_units='lb.', cost=100)
		chicken.save()
		turkey = models.Ingredient(name='Turkey', package_size=10, package_size_units='lb.', cost=100)
		turkey.save()
		fish = models.Ingredient(name='Fish', package_size=10, package_size_units='lb.', cost=100)
		fish.save()
		onion = models.Ingredient(name='Onion', package_size=10, package_size_units='lb.', cost=100)
		onion.save()
		cheddar = models.Ingredient(name='Cheddar', package_size=10, package_size_units='lb.', cost=100)
		cheddar.save()
		mozzarella = models.Ingredient(name='Mozzarella', package_size=10, package_size_units='lb.', cost=100)
		mozzarella.save()
		lettuce = models.Ingredient(name='Lettuce', package_size=10, package_size_units='lb.', cost=100)
		lettuce.save()
		egg = models.Ingredient(name='Egg', package_size=10, package_size_units='lb.', cost=100)
		egg.save()
		dead_animal = models.Ingredient(name='Dead Animal', package_size=10, package_size_units='lb.', cost=100)
		dead_animal.save()
		cucumber = models.Ingredient(name='Cucumber', package_size=10, package_size_units='lb.', cost=100)
		cucumber.save()
		vinegar = models.Ingredient(name='Vinegar', package_size=10, package_size_units='lb.', cost=100)
		vinegar.save()
		salt = models.Ingredient(name='Salt', package_size=10, package_size_units='lb.', cost=100)
		salt.save()
		pepper = models.Ingredient(name='Pepper', package_size=10, package_size_units='lb.', cost=100)
		pepper.save()
		water = models.Ingredient(name='Water', package_size=10, package_size_units='lb.', cost=100)
		water.save()
		styrofoam = models.Ingredient(name='Styrofoam', package_size=10, package_size_units='lb.', cost=100)
		styrofoam.save()
		soups = models.ProductLine(name='Soups')
		soups.save()
		salads = models.ProductLine(name='Salads')
		salads.save()
		entrees = models.ProductLine(name='Entrees')
		entrees.save()
		macncheese = models.ProductLine(name='Mac-n-Cheese')
		macncheese.save()
		easy_cheeses = models.ProductLine(name='Easy Cheeses')
		easy_cheeses.save()
		condiments = models.ProductLine(name='Condiments')
		condiments.save()
		frozen_meat = models.ProductLine(name='Frozen Meats')
		frozen_meat.save()
		to_soup_formula = models.Formula(name='Tomato Soup Formula')
		to_soup_formula.save()
		po_soup_formula = models.Formula(name='Potato and Onion Soup Formula')
		po_soup_formula.save()
		cn_soup_formula = models.Formula(name='Chicken Noodle Soup Formula')
		cn_soup_formula.save()
		tu_soup_formula = models.Formula(name='Turkey Soup Formula')
		tu_soup_formula.save()
		fi_soup_formula = models.Formula(name='Fish Soup Formula')
		fi_soup_formula.save()
		ptc_soup_formula = models.Formula(name='Potato, Tomato, Carrot Soup Formula')
		ptc_soup_formula.save()
		p_salad_formula = models.Formula(name='Potato Salad Formula')
		p_salad_formula.save()
		l_salad_formula = models.Formula(name='Salad Formula')
		l_salad_formula.save()
		e_salad_formula = models.Formula(name='Egg Salad Formula')
		e_salad_formula.save()
		spaghetti_formula = models.Formula(name='Spaghetti Formula')
		spaghetti_formula.save()
		ctikka_formula = models.Formula(name='Chicken Tikka Formula')
		ctikka_formula.save()
		pizza_formula = models.Formula(name='Pizza Formula')
		pizza_formula.save()
		fishnchips_formula = models.Formula(name='Fish-n-Chips Formula')
		fishnchips_formula.save()
		lasagna_formula = models.Formula(name='Lasagna Formula')
		lasagna_formula.save()
		burrito_formula = models.Formula(name='Burrito Formula')
		burrito_formula.save()
		ezmac_formula = models.Formula(name='Easy Mac Formula')
		ezmac_formula.save()
		threemac_formula = models.Formula(name='3 Cheese Mac-n-Cheese Formula')
		threemac_formula.save()
		american_formula = models.Formula(name='American Cheese Formula')
		american_formula.save()
		easycf_formula = models.Formula(name='Cheese Food Formula')
		easycf_formula.save()
		ketchup_formula = models.Formula(name='Ketchup Formula')
		ketchup_formula.save()
		mayo_formula = models.Formula(name='Mayonnaise Formula')
		mayo_formula.save()
		relish_formula = models.Formula(name='Relish Formula')
		relish_formula.save()
		hburger_formula = models.Formula(name='Hamburger Formula')
		hburger_formula.save()
		hdog_formula = models.Formula(name='Hot Dog Formula')
		hdog_formula.save()
		steak_formula = models.Formula(name='Steak Formula')
		steak_formula.save()
		fturkey_formula = models.Formula(name='Turkey Formula')
		fturkey_formula.save()
		to_soup = models.SKU(name='Tomato Soup', case_upc='000000000000', product_line=soups, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=to_soup_formula, mfg_rate=1.0)
		to_soup.save()
		po_soup = models.SKU(name='Potato and Onion Soup', case_upc='000000000017', product_line=soups, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=po_soup_formula, mfg_rate=2.0)
		po_soup.save()
		cn_soup = models.SKU(name='Chicken Noodle Soup', case_upc='000000000109', product_line=soups, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=cn_soup_formula, mfg_rate=1.0)
		cn_soup.save()
		tu_soup = models.SKU(name='Turkey Soup', case_upc='000000001007', product_line=soups, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=tu_soup_formula, mfg_rate=0.7)
		tu_soup.save()
		fi_soup = models.SKU(name='Fish Soup', case_upc='000000010009', product_line=soups, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=fi_soup_formula, mfg_rate=1.0)
		fi_soup.save()
		ptc_soup = models.SKU(name='Potato, Tomato, and Carrot Soup', case_upc='000000000116', product_line=soups, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=ptc_soup_formula, mfg_rate=1.0)
		ptc_soup.save()
		p_salad = models.SKU(name='Potato Salad', case_upc='000000000215', product_line=salads, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=p_salad_formula, mfg_rate=1.0)
		p_salad.save()
		l_salad = models.SKU(name='Salad', case_upc='000000000314', product_line=salads, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=l_salad_formula, mfg_rate=1.0)
		l_salad.save()
		e_salad = models.SKU(name='Egg Salad', case_upc='000000000413', product_line=salads, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=e_salad_formula, mfg_rate=17.0)
		e_salad.save()
		spaghetti = models.SKU(name='Spaghetti', case_upc='000000000512', product_line=entrees, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=spaghetti_formula, mfg_rate=1.0)
		spaghetti.save()
		ctikka = models.SKU(name='Chicken Tikka', case_upc='000000000611', product_line=entrees, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=ctikka_formula, mfg_rate=71.089)
		ctikka.save()
		pizza = models.SKU(name='Pizza', case_upc='000000000710', product_line=entrees, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=pizza_formula, mfg_rate=100.26)
		pizza.save()
		fishnchips = models.SKU(name='Fish-n-Chips', case_upc='000000000208', product_line=entrees, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=fishnchips_formula, mfg_rate=1.0)
		fishnchips.save()
		lasagna = models.SKU(name='Lasagna', case_upc='000000000307', product_line=entrees, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=lasagna_formula, mfg_rate=118.0)
		lasagna.save()
		burrito = models.SKU(name='Burrito', case_upc='000000000406', product_line=entrees, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=burrito_formula, mfg_rate=91.0)
		burrito.save()
		ezmac = models.SKU(name='Easy Mac', case_upc='000000000505', product_line=macncheese, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=ezmac_formula, mfg_rate=1.0)
		ezmac.save()
		threemac = models.SKU(name='3 Cheese Mac-n-Cheese', case_upc='000000000604', product_line=macncheese, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=threemac_formula, mfg_rate=1.0)
		threemac.save()
		american = models.SKU(name='American Cheese Whip', case_upc='000000000703', product_line=easy_cheeses, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=american_formula, mfg_rate=1.0)
		american.save()
		easycf = models.SKU(name='Cheese Food', case_upc='000000000802', product_line=easy_cheeses, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=easycf_formula, mfg_rate=21.0)
		easycf.save()
		ketchup = models.SKU(name='Ketchup', case_upc='000000000901', product_line=condiments, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=ketchup_formula, mfg_rate=1.20)
		ketchup.save()
		mayo = models.SKU(name='Mayonnaise', case_upc='000000000123', product_line=condiments, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=mayo_formula, mfg_rate=12.0)
		mayo.save()
		relish = models.SKU(name='Relish', case_upc='000000000222', product_line=condiments, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=relish_formula, mfg_rate=10.0)
		relish.save()
		hburger = models.SKU(name='Frozen Hamburger', case_upc='000000000321', product_line=frozen_meat, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=hburger_formula, mfg_rate=1.0)
		hburger.save()
		hdog = models.SKU(name='Frozen Hot Dog', case_upc='000000000420', product_line=frozen_meat, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=hdog_formula, mfg_rate=1.0)
		hdog.save()
		steak = models.SKU(name='Frozen Steak', case_upc='000000001113', product_line=frozen_meat, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=steak_formula, mfg_rate=166.0)
		steak.save()
		fturkey = models.SKU(name='Frozen Turkey', case_upc='000000001212', product_line=frozen_meat, unit_upc='000000000013', unit_size='Small Box', units_per_case=16, formula=fturkey_formula, mfg_rate=10.09)
		fturkey.save()
		soup_line_1 = models.ManufacturingLine(name='Soup Line', shortname='SL1')
		soup_line_1.save()
		soup_line_2 = models.ManufacturingLine(name='Soup Line', shortname='SL2')
		soup_line_2.save()
		entree_line_1 = models.ManufacturingLine(name='Entree Line', shortname='EL1')
		entree_line_1.save()
		entree_line_2 = models.ManufacturingLine(name='Entree Line', shortname='EL2')
		entree_line_2.save()
		entree_line_3 = models.ManufacturingLine(name='Entree Line', shortname='EL3')
		entree_line_3.save()
		cond_line = models.ManufacturingLine(name='Condiment Line', shortname='COL1')
		cond_line.save()
		cheese_line_1 = models.ManufacturingLine(name='Cheese Line', shortname='CHL1')
		cheese_line_1.save()
		cheese_line_2 = models.ManufacturingLine(name='Cheese Line', shortname='CHL2')
		cheese_line_2.save()
		meat_line = models.ManufacturingLine(name='Meat Processing Line', shortname='ML1')
		meat_line.save()
		models.IngredientQty(formula=to_soup_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=to_soup_formula, ingredient=water, quantity=0.05).save()
		models.IngredientQty(formula=po_soup_formula, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(formula=po_soup_formula, ingredient=onion, quantity=0.05).save()
		models.IngredientQty(formula=po_soup_formula, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(formula=cn_soup_formula, ingredient=chicken, quantity=0.05).save()
		models.IngredientQty(formula=cn_soup_formula, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(formula=cn_soup_formula, ingredient=water, quantity=0.05).save()
		models.IngredientQty(formula=cn_soup_formula, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(formula=cn_soup_formula, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(formula=tu_soup_formula, ingredient=turkey, quantity=0.05).save()
		models.IngredientQty(formula=tu_soup_formula, ingredient=water, quantity=0.05).save()
		models.IngredientQty(formula=tu_soup_formula, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(formula=fi_soup_formula, ingredient=fish, quantity=0.05).save()
		models.IngredientQty(formula=fi_soup_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=fi_soup_formula, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(formula=fi_soup_formula, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(formula=fi_soup_formula, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(formula=fi_soup_formula, ingredient=water, quantity=0.05).save()
		models.IngredientQty(formula=ptc_soup_formula, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(formula=ptc_soup_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=ptc_soup_formula, ingredient=carrot, quantity=0.05).save()
		models.IngredientQty(formula=p_salad_formula, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(formula=p_salad_formula, ingredient=egg, quantity=0.05).save()
		models.IngredientQty(formula=p_salad_formula, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(formula=p_salad_formula, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(formula=l_salad_formula, ingredient=lettuce, quantity=0.05).save()
		models.IngredientQty(formula=e_salad_formula, ingredient=egg, quantity=0.05).save()
		models.IngredientQty(formula=e_salad_formula, ingredient=lettuce, quantity=0.05).save()
		models.IngredientQty(formula=e_salad_formula, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(formula=spaghetti_formula, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(formula=spaghetti_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=spaghetti_formula, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(formula=spaghetti_formula, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(formula=ctikka_formula, ingredient=chicken, quantity=0.05).save()
		models.IngredientQty(formula=ctikka_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=ctikka_formula, ingredient=water, quantity=0.05).save()
		models.IngredientQty(formula=pizza_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=pizza_formula, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(formula=pizza_formula, ingredient=mozzarella, quantity=0.05).save()
		models.IngredientQty(formula=fishnchips_formula, ingredient=fish, quantity=0.05).save()
		models.IngredientQty(formula=fishnchips_formula, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(formula=lasagna_formula, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(formula=lasagna_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=lasagna_formula, ingredient=mozzarella, quantity=0.05).save()
		models.IngredientQty(formula=ezmac_formula, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(formula=ezmac_formula, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(formula=threemac_formula, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(formula=threemac_formula, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(formula=threemac_formula, ingredient=mozzarella, quantity=0.05).save()
		models.IngredientQty(formula=american_formula, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(formula=american_formula, ingredient=water, quantity=0.05).save()
		models.IngredientQty(formula=american_formula, ingredient=styrofoam, quantity=0.05).save()
		models.IngredientQty(formula=easycf_formula, ingredient=water, quantity=0.05).save()
		models.IngredientQty(formula=easycf_formula, ingredient=styrofoam, quantity=0.05).save()
		models.IngredientQty(formula=ketchup_formula, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(formula=ketchup_formula, ingredient=vinegar, quantity=0.05).save()
		models.IngredientQty(formula=mayo_formula, ingredient=egg, quantity=0.05).save()
		models.IngredientQty(formula=relish_formula, ingredient=cucumber, quantity=0.05).save()
		models.IngredientQty(formula=relish_formula, ingredient=vinegar, quantity=0.05).save()
		models.IngredientQty(formula=hburger_formula, ingredient=dead_animal, quantity=0.05).save()
		models.IngredientQty(formula=hdog_formula, ingredient=dead_animal, quantity=0.05).save()
		models.IngredientQty(formula=hdog_formula, ingredient=styrofoam, quantity=0.05).save()
		models.IngredientQty(formula=steak_formula, ingredient=dead_animal, quantity=0.05).save()
		models.IngredientQty(formula=fturkey_formula, ingredient=turkey, quantity=0.05).save()
		models.SkuMfgLine(sku=to_soup, mfg_line=soup_line_1).save()
		models.SkuMfgLine(sku=to_soup, mfg_line=soup_line_2).save()
		models.SkuMfgLine(sku=po_soup, mfg_line=soup_line_1).save()
		models.SkuMfgLine(sku=po_soup, mfg_line=soup_line_2).save()
		models.SkuMfgLine(sku=cn_soup, mfg_line=soup_line_1).save()
		models.SkuMfgLine(sku=cn_soup, mfg_line=soup_line_2).save()
		models.SkuMfgLine(sku=fi_soup, mfg_line=soup_line_1).save()
		models.SkuMfgLine(sku=fi_soup, mfg_line=soup_line_2).save()
		models.SkuMfgLine(sku=ptc_soup, mfg_line=soup_line_1).save()
		models.SkuMfgLine(sku=ptc_soup, mfg_line=soup_line_2).save()
		models.SkuMfgLine(sku=ctikka, mfg_line=entree_line_1).save()
		models.SkuMfgLine(sku=ctikka, mfg_line=entree_line_2).save()
		models.SkuMfgLine(sku=ctikka, mfg_line=entree_line_3).save()
		models.SkuMfgLine(sku=pizza, mfg_line=entree_line_2).save()
		models.SkuMfgLine(sku=pizza, mfg_line=entree_line_3).save()
		models.SkuMfgLine(sku=fishnchips, mfg_line=entree_line_1).save()
		models.SkuMfgLine(sku=fishnchips, mfg_line=entree_line_2).save()
		models.SkuMfgLine(sku=fishnchips, mfg_line=entree_line_3).save()
		models.SkuMfgLine(sku=lasagna, mfg_line=entree_line_1).save()
		models.SkuMfgLine(sku=lasagna, mfg_line=entree_line_2).save()
		models.SkuMfgLine(sku=burrito, mfg_line=entree_line_2).save()
		models.SkuMfgLine(sku=ezmac, mfg_line=entree_line_1).save()
		models.SkuMfgLine(sku=ezmac, mfg_line=entree_line_2).save()
		models.SkuMfgLine(sku=ezmac, mfg_line=entree_line_3).save()
		models.SkuMfgLine(sku=threemac, mfg_line=entree_line_1).save()
		models.SkuMfgLine(sku=threemac, mfg_line=entree_line_2).save()
		models.SkuMfgLine(sku=threemac, mfg_line=entree_line_3).save()
		models.SkuMfgLine(sku=american, mfg_line=cheese_line_1).save()
		models.SkuMfgLine(sku=american, mfg_line=cheese_line_2).save()
		models.SkuMfgLine(sku=easycf, mfg_line=cheese_line_1).save()
		models.SkuMfgLine(sku=easycf, mfg_line=cheese_line_2).save()
		models.SkuMfgLine(sku=ketchup, mfg_line=cond_line).save()
		models.SkuMfgLine(sku=mayo, mfg_line=cond_line).save()
		models.SkuMfgLine(sku=relish, mfg_line=cond_line).save()
		models.SkuMfgLine(sku=hburger, mfg_line=meat_line).save()
		models.SkuMfgLine(sku=hdog, mfg_line=meat_line).save()
		models.SkuMfgLine(sku=steak, mfg_line=meat_line).save()
		models.SkuMfgLine(sku=fturkey, mfg_line=meat_line).save()

	def check_soup_ingredient_count(self):
		soup = models.Formula.filter(name__icontains='Soup')
		self.assertIs(models.IngredientQty.filter(formula__in=soup).count(), 22)

	def check_num_skus_with_salt(self):
		salt = models.Ingredient.filter(name='Salt')[0]
		self.assertIs(models.IngredientQty.filter(ingredient=salt).count(), 6)

	def check_soup_mfg_line_count(self):
		soup = models.SKU.filter(name__icontains='Soup')
		self.assertIs(models.ManufacturingLine.filter(skumfgline__sku__in=soup).count(), 2)

