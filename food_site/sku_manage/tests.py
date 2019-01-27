from django.test import TestCase
import models

class SkuUpcTests(TestCase):

	def test_all_zeros(self):
		sku = models.SKU(case_upc = 000000000000)
		self.assertIs(sku.check_case_upc(), True)

	def test_correct_check(self):
		sku = models.SKU(case_upc = 000040000006)
		self.assertIs(sku.check_case_upc(), True)

	def test_nonzero_first_digit_6(self):
		sku = models.SKU(case_upc = 600000000004)
		self.assertIs(sku.check_case_upc(), True)

	def test_bad_check_1(self):
		sku = models.SKU(case_upc = 000000000001)
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_check_2(self):
		sku = models.SKU(case_upc = 000000010000)
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_1(self):
		sku = models.SKU(case_upc = 100000000000)
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_2(self):
		sku = models.SKU(case_upc = 200000000000)
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_3(self):
		sku = models.SKU(case_upc = 300000000000)
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_4(self):
		sku = models.SKU(case_upc = 400000000000)
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_5(self):
		sku = models.SKU(case_upc = 500000000000)
		self.assertIs(sku.check_case_upc(), False)

