from django.test import TestCase, TransactionTestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from . import models


class ForeignKeyTests(TransactionTestCase):

	def test_sku_correct_product_line(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku = models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku.save()

	def test_sku_missing_product_line(self):
		pl = models.ProductLine(name='Soups')
		sku = models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		with self.assertRaisesMessage(IntegrityError, 'FOREIGN KEY constraint failed'):
			sku.save()

	def test_recipe_correct_both(self):
		i = models.Ingredient(name='Potato', number=0, package_size='50lb bag', cost=7.99)
		i.save()
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku = models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku.save()
		iq1 = models.IngredientQty(sku=sku, ingredient=i, quantity=0.2)
		iq2 = models.IngredientQty(sku=sku, ingredient=i, quantity=0.08)
		iq1.save()
		iq2.save()
		self.assertIs(models.IngredientQty.objects.count(), 2)


	def test_recipe_missing_sku(self):
		i = models.Ingredient(name='Potato', number=0, package_size='50lb bag', cost=7.99)
		i.save()
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku = models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		iq = models.IngredientQty(sku=sku, ingredient=i, quantity=0.2)
		with self.assertRaisesMessage(ValueError, 'save() prohibited'):
			iq.save()

	def test_recipe_missing_ingredient(self):
		i = models.Ingredient(name='Potato', number=0, package_size='50lb bag', cost=7.99)
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku = models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku.save()
		iq = models.IngredientQty(sku=sku, ingredient=i, quantity=0.2)
		with self.assertRaisesMessage(ValueError, 'save() prohibited'):
			iq.save()


class IngredientUniqueTests(TransactionTestCase):

	def test_unique(self):
		i1 = models.Ingredient(name='Potato', number=0, package_size='50lb bag', cost=7.99)
		i2 = models.Ingredient(name='Tomato', number=1, package_size='10lb crate', cost=6.99)
		i1.save()
		i2.save()
		self.assertIs(models.Ingredient.objects.count(), 2)

	def test_unique_number_generation(self):
		i1 = models.Ingredient(name='Potato', package_size='50lb bag', cost=7.99)
		i2 = models.Ingredient(name='Tomato', package_size='10lb crate', cost=6.99)
		i1.save()
		i2.save()
		self.assertIs(models.Ingredient.objects.count(), 2)

	def test_identical_names(self):
		i1 = models.Ingredient(name='Potato', number=0, package_size='50lb bag', cost=7.99)
		i2 = models.Ingredient(name='Potato', number=1, package_size='70lb bag', cost=10.99)
		i1.save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			i2.save()

	def test_identical_numbers(self):
		i1 = models.Ingredient(name='Potato', number=0, package_size='50lb bag', cost=7.99)
		i2 = models.Ingredient(name='Tomato', number=0, package_size='10lb crate', cost=6.99)
		i1.save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			i2.save()


class ProductLineUniqueTests(TransactionTestCase):

	def test_unique(self):
		pl1 = models.ProductLine(name='Soups')
		pl2 = models.ProductLine(name='Salads')
		pl1.save()
		pl2.save()
		self.assertIs(models.ProductLine.objects.count(), 2)

	def test_identical_names(self):
		pl1 = models.ProductLine(name='Soups')
		pl2 = models.ProductLine(name='Soups')
		pl1.save()
		pl2.save()
		self.assertIs(models.ProductLine.objects.count(), 1)


class SKUUniqueTests(TransactionTestCase):

	def test_unique(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku1 = models.SKU(name='Can O Soup', sku_num=0, case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku2 = models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku1.save()
		sku2.save()
		self.assertIs(models.SKU.objects.count(), 2)

	def test_unique_number_generation(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku1 = models.SKU(name='Can O Soup', case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku2 = models.SKU(name='Can O Soup', case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku1.save()
		#sku2.save()
		#self.assertIs(models.SKU.objects.count(), 2)

	def test_identical_sku_nums(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku1 = models.SKU(name='Can O Soup', sku_num=0, case_upc=0, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku2 = models.SKU(name='Can O Soup', sku_num=0, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku1.save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			sku2.save()

	def test_identical_case_upcs(self):
		pl = models.ProductLine(name='Soups')
		pl.save()
		sku1 = models.SKU(name='Can O Soup', sku_num=0, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku2 = models.SKU(name='Can O Soup', sku_num=1, case_upc=26, unit_upc=13, unit_size='32oz', units_per_case=16, product_line=pl)
		sku1.save()
		with self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed'):
			sku2.save()


class UPCValidationTests(TestCase):

	def test_all_zeros(self):
		models.validate_upc(int('000000000000'))

	def test_correct_check_1(self):
		models.validate_upc(int('000400000006'))

	def test_correct_check_2(self):
		models.validate_upc(int('004000000008'))

	def test_correct_check_3(self):
		models.validate_upc(int('041104256290'))

	def test_correct_check_4(self):
		models.validate_upc(int('019556793038'))

	def test_correct_check_5(self):
		models.validate_upc(int('766171000439'))

	def test_nonzero_first_digit_6(self):
		models.validate_upc(int('600000000002'))

	def test_nonzero_first_digit_7(self):
		models.validate_upc(int('700000000009'))

	def test_nonzero_first_digit_8(self):
		models.validate_upc(int('800000000006'))

	def test_nonzero_first_digit_9(self):
		models.validate_upc(int('900000000003'))

	def test_bad_check_1(self):
		with self.assertRaisesMessage(ValidationError, 'UPC check digit is not valid'):
			models.validate_upc(int('000000000001'))

	def test_bad_check_2(self):
		with self.assertRaisesMessage(ValidationError, 'UPC check digit is not valid'):
			models.validate_upc(int('000000010000'))

	def test_bad_first_digit_1(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc(int('100000000000'))

	def test_bad_first_digit_2(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc(int('200000000000'))

	def test_bad_first_digit_3(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc(int('300000000000'))

	def test_bad_first_digit_4(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc(int('400000000000'))

	def test_bad_first_digit_5(self):
		with self.assertRaisesMessage(ValidationError, 'UPC first digit is not valid'):
			models.validate_upc(int('500000000000'))

	def test_bad_negative(self):
		with self.assertRaisesMessage(ValidationError, 'UPC cannot be negative'):
			models.validate_upc(int('-000000000019'))



class DataSaveTests(TestCase):

	def test_large_save(self):
		potato = models.Ingredient(name='Potato', package_size='Big Box', cost=100)
		tomato = models.Ingredient(name='Tomato', package_size='Big Box', cost=100)
		carrot = models.Ingredient(name='Carrot', package_size='Big Box', cost=100)
		pasta = models.Ingredient(name='Pasta', package_size='Big Box', cost=100)
		chicken = models.Ingredient(name='Chicken', package_size='Big Box', cost=100)
		turkey = models.Ingredient(name='Turkey', package_size='Big Box', cost=100)
		fish = models.Ingredient(name='Fish', package_size='Big Box', cost=100)
		onion = models.Ingredient(name='Onion', package_size='Big Box', cost=100)
		cheddar = models.Ingredient(name='Cheddar', package_size='Big Box', cost=100)
		mozzarella = models.Ingredient(name='Mozzarella', package_size='Big Box', cost=100)
		lettuce = models.Ingredient(name='Lettuce', package_size='Big Box', cost=100)
		egg = models.Ingredient(name='Egg', package_size='Big Box', cost=100)
		dead_animal = models.Ingredient(name='Dead Animal', package_size='Big Box', cost=100)
		cucumber = models.Ingredient(name='Cucumber', package_size='Big Box', cost=100)
		vinegar = models.Ingredient(name='Vinegar', package_size='Big Box', cost=100)
		salt = models.Ingredient(name='Salt', package_size='Big Box', cost=100)
		pepper = models.Ingredient(name='Pepper', package_size='Big Box', cost=100)
		water = models.Ingredient(name='Water', package_size='Big Box', cost=100)
		styrofoam = models.Ingredient(name='Styrofoam', package_size='Big Box', cost=100)
		potato.save()
		tomato.save()
		carrot.save()
		pasta.save()
		chicken.save()
		turkey.save()
		fish.save()
		onion.save()
		cheddar.save()
		mozzarella.save()
		lettuce.save()
		egg.save()
		dead_animal.save()
		cucumber.save()
		vinegar.save()
		salt.save()
		pepper.save()
		water.save()
		styrofoam.save()
		soups = models.ProductLine(name='Soups')
		salads = models.ProductLine(name='Salads')
		entrees = models.ProductLine(name='Entrees')
		macncheese = models.ProductLine(name='Mac-n-Cheese')
		easy_cheeses = models.ProductLine(name='Easy Cheeses')
		condiments = models.ProductLine(name='Condiments')
		frozen_meat = models.ProductLine(name='Frozen Meats')
		soups.save()
		salads.save()
		entrees.save()
		macncheese.save()
		easy_cheeses.save()
		condiments.save()
		frozen_meat.save()
		to_soup = models.SKU(name='Tomato Soup', sku_num=0, case_upc=0, product_line=soups, unit_upc=13, unit_size='Small Box', units_per_case=16)
		po_soup = models.SKU(name='Potato and Onion Soup', sku_num=1, case_upc=101, product_line=soups, unit_upc=13, unit_size='Small Box', units_per_case=16)
		cn_soup = models.SKU(name='Chicken Noodle Soup', sku_num=2, case_upc=10001, product_line=soups, unit_upc=13, unit_size='Small Box', units_per_case=16)
		tu_soup = models.SKU(name='Turkey Soup', sku_num=3, case_upc=1000009, product_line=soups, unit_upc=13, unit_size='Small Box', units_per_case=16)
		fi_soup = models.SKU(name='Fish Soup', sku_num=4, case_upc=100000009, product_line=soups, unit_upc=13, unit_size='Small Box', units_per_case=16)
		ptc_soup = models.SKU(name='Potato, Tomato, and Carrot Soup', sku_num=5, case_upc=10000000001, product_line=soups, unit_upc=13, unit_size='Small Box', units_per_case=16)
		p_salad = models.SKU(name='Potato Salad', sku_num=6, case_upc=208, product_line=salads, unit_upc=13, unit_size='Small Box', units_per_case=16)
		l_salad = models.SKU(name='Salad', sku_num=7, case_upc=20008, product_line=salads, unit_upc=13, unit_size='Small Box', units_per_case=16)
		e_salad = models.SKU(name='Egg Salad', sku_num=8, case_upc=2000008, product_line=salads, unit_upc=13, unit_size='Small Box', units_per_case=16)
		spaghetti = models.SKU(name='Spaghetti', sku_num=9, case_upc=307, product_line=entrees, unit_upc=13, unit_size='Small Box', units_per_case=16)
		ctikka = models.SKU(name='Chicken Tikka', sku_num=10, case_upc=30007, product_line=entrees, unit_upc=13, unit_size='Small Box', units_per_case=16)
		pizza = models.SKU(name='Pizza', sku_num=11, case_upc=3000003, product_line=entrees, unit_upc=13, unit_size='Small Box', units_per_case=16)
		fishnchips = models.SKU(name='Fish-n-Chips', sku_num=12, case_upc=300000007, product_line=entrees, unit_upc=13, unit_size='Small Box', units_per_case=16)
		lasagna = models.SKU(name='Lasagna', sku_num=13, case_upc=10108, product_line=entrees, unit_upc=13, unit_size='Small Box', units_per_case=16)
		burrito = models.SKU(name='Burrito', sku_num=14, case_upc=1000108, product_line=entrees, unit_upc=13, unit_size='Small Box', units_per_case=16)
		ezmac = models.SKU(name='Easy Mac', sku_num=15, case_upc=1010107, product_line=macncheese, unit_upc=13, unit_size='Small Box', units_per_case=16)
		threemac = models.SKU(name='3 Cheese Mac-n-Cheese', sku_num=16, case_upc=1010206, product_line=macncheese, unit_upc=13, unit_size='Small Box', units_per_case=16)
		american = models.SKU(name='American Cheese Whip', sku_num=17, case_upc=1020106, product_line=easy_cheeses, unit_upc=13, unit_size='Small Box', units_per_case=16)
		easycf = models.SKU(name='Cheese Food', sku_num=18, case_upc=2010106, product_line=easy_cheeses, unit_upc=13, unit_size='Small Box', units_per_case=16)
		ketchup = models.SKU(name='Ketchup', sku_num=19, case_upc=2030104, product_line=condiments, unit_upc=13, unit_size='Small Box', units_per_case=16)
		mayo = models.SKU(name='Mayonnaise', sku_num=20, case_upc=2020105, product_line=condiments, unit_upc=13, unit_size='Small Box', units_per_case=16)
		relish = models.SKU(name='Relish', sku_num=21, case_upc=2030203, product_line=condiments, unit_upc=13, unit_size='Small Box', units_per_case=16)
		hburger = models.SKU(name='Frozen Hamburger', sku_num=22, case_upc=2040202, product_line=frozen_meat, unit_upc=13, unit_size='Small Box', units_per_case=16)
		hdog = models.SKU(name='Frozen Hot Dog', sku_num=23, case_upc=3040201, product_line=frozen_meat, unit_upc=13, unit_size='Small Box', units_per_case=16)
		steak = models.SKU(name='Frozen Steak', sku_num=24, case_upc=3030202, product_line=frozen_meat, unit_upc=13, unit_size='Small Box', units_per_case=16)
		fturkey = models.SKU(name='Frozen Turkey', sku_num=25, case_upc=3010204, product_line=frozen_meat, unit_upc=13, unit_size='Small Box', units_per_case=16)
		to_soup.save()
		po_soup.save()
		cn_soup.save()
		tu_soup.save()
		fi_soup.save()
		ptc_soup.save()
		p_salad.save()
		l_salad.save()
		e_salad.save()
		spaghetti.save()
		ctikka.save()
		pizza.save()
		fishnchips.save()
		lasagna.save()
		burrito.save()
		ezmac.save()
		threemac.save()
		american.save()
		easycf.save()
		ketchup.save()
		mayo.save()
		relish.save()
		hburger.save()
		hdog.save()
		steak.save()
		fturkey.save()
		models.IngredientQty(sku=to_soup, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=to_soup, ingredient=water, quantity=0.05).save()
		models.IngredientQty(sku=po_soup, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(sku=po_soup, ingredient=onion, quantity=0.05).save()
		models.IngredientQty(sku=po_soup, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(sku=cn_soup, ingredient=chicken, quantity=0.05).save()
		models.IngredientQty(sku=cn_soup, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(sku=cn_soup, ingredient=water, quantity=0.05).save()
		models.IngredientQty(sku=cn_soup, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(sku=cn_soup, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(sku=tu_soup, ingredient=turkey, quantity=0.05).save()
		models.IngredientQty(sku=tu_soup, ingredient=water, quantity=0.05).save()
		models.IngredientQty(sku=tu_soup, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(sku=fi_soup, ingredient=fish, quantity=0.05).save()
		models.IngredientQty(sku=fi_soup, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=fi_soup, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(sku=fi_soup, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(sku=fi_soup, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(sku=fi_soup, ingredient=water, quantity=0.05).save()
		models.IngredientQty(sku=ptc_soup, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(sku=ptc_soup, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=ptc_soup, ingredient=carrot, quantity=0.05).save()
		models.IngredientQty(sku=p_salad, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(sku=p_salad, ingredient=egg, quantity=0.05).save()
		models.IngredientQty(sku=p_salad, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(sku=p_salad, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(sku=l_salad, ingredient=lettuce, quantity=0.05).save()
		models.IngredientQty(sku=e_salad, ingredient=egg, quantity=0.05).save()
		models.IngredientQty(sku=e_salad, ingredient=lettuce, quantity=0.05).save()
		models.IngredientQty(sku=e_salad, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(sku=spaghetti, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(sku=spaghetti, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=spaghetti, ingredient=salt, quantity=0.05).save()
		models.IngredientQty(sku=spaghetti, ingredient=pepper, quantity=0.05).save()
		models.IngredientQty(sku=ctikka, ingredient=chicken, quantity=0.05).save()
		models.IngredientQty(sku=ctikka, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=ctikka, ingredient=water, quantity=0.05).save()
		models.IngredientQty(sku=pizza, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=pizza, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(sku=pizza, ingredient=mozzarella, quantity=0.05).save()
		models.IngredientQty(sku=fishnchips, ingredient=fish, quantity=0.05).save()
		models.IngredientQty(sku=fishnchips, ingredient=potato, quantity=0.05).save()
		models.IngredientQty(sku=lasagna, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(sku=lasagna, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=lasagna, ingredient=mozzarella, quantity=0.05).save()
		models.IngredientQty(sku=ezmac, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(sku=ezmac, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(sku=threemac, ingredient=pasta, quantity=0.05).save()
		models.IngredientQty(sku=threemac, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(sku=threemac, ingredient=mozzarella, quantity=0.05).save()
		models.IngredientQty(sku=american, ingredient=cheddar, quantity=0.05).save()
		models.IngredientQty(sku=american, ingredient=water, quantity=0.05).save()
		models.IngredientQty(sku=american, ingredient=styrofoam, quantity=0.05).save()
		models.IngredientQty(sku=easycf, ingredient=water, quantity=0.05).save()
		models.IngredientQty(sku=easycf, ingredient=styrofoam, quantity=0.05).save()
		models.IngredientQty(sku=ketchup, ingredient=tomato, quantity=0.05).save()
		models.IngredientQty(sku=ketchup, ingredient=vinegar, quantity=0.05).save()
		models.IngredientQty(sku=mayo, ingredient=egg, quantity=0.05).save()
		models.IngredientQty(sku=relish, ingredient=cucumber, quantity=0.05).save()
		models.IngredientQty(sku=relish, ingredient=vinegar, quantity=0.05).save()
		models.IngredientQty(sku=hburger, ingredient=dead_animal, quantity=0.05).save()
		models.IngredientQty(sku=hdog, ingredient=dead_animal, quantity=0.05).save()
		models.IngredientQty(sku=hdog, ingredient=styrofoam, quantity=0.05).save()
		models.IngredientQty(sku=steak, ingredient=dead_animal, quantity=0.05).save()
		models.IngredientQty(sku=fturkey, ingredient=turkey, quantity=0.05).save()

	def check_tomato_soup_ingredient_count(self):
		soup = models.SKU.filter(name='Tomato Soup')[0]
		self.assertIs(models.IngredientQty.filter(sku=soup).count(), 2)

	def check_num_skus_with_salt(self):
		salt = models.Ingredient.filter(name='Salt')[0]
		self.assertIs(models.IngredientQty.filter(ingredient=salt).count(), 6)

