from django.test import TestCase
from . import models

class SkuUpcTests(TestCase):

	def test_all_zeros(self):
		sku = models.SKU(case_upc = int('000000000000'))
		self.assertIs(sku.check_case_upc(), True)

	def test_correct_check_1(self):
		sku = models.SKU(case_upc = int('000400000006'))
		self.assertIs(sku.check_case_upc(), True)

	def test_correct_check_2(self):
		sku = models.SKU(case_upc = int('004000000008'))
		self.assertIs(sku.check_case_upc(), True)

	def test_correct_check_3(self):
		sku = models.SKU(case_upc = int('041104256290'))
		self.assertIs(sku.check_case_upc(), True)

	def test_correct_check_4(self):
		sku = models.SKU(case_upc = int('019556793038'))
		self.assertIs(sku.check_case_upc(), True)

	def test_correct_check_5(self):
		sku = models.SKU(case_upc = int('766171000439'))
		self.assertIs(sku.check_case_upc(), True)

	def test_nonzero_first_digit_6(self):
		sku = models.SKU(case_upc = int('600000000002'))
		self.assertIs(sku.check_case_upc(), True)

	def test_nonzero_first_digit_7(self):
		sku = models.SKU(case_upc = int('700000000009'))
		self.assertIs(sku.check_case_upc(), True)

	def test_nonzero_first_digit_8(self):
		sku = models.SKU(case_upc = int('800000000006'))
		self.assertIs(sku.check_case_upc(), True)

	def test_nonzero_first_digit_9(self):
		sku = models.SKU(case_upc = int('900000000003'))
		self.assertIs(sku.check_case_upc(), True)

	def test_bad_check_1(self):
		sku = models.SKU(case_upc = int('000000000001'))
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_check_2(self):
		sku = models.SKU(case_upc = int('000000010000'))
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_1(self):
		sku = models.SKU(case_upc = int('100000000000'))
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_2(self):
		sku = models.SKU(case_upc = int('200000000000'))
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_3(self):
		sku = models.SKU(case_upc = int('300000000000'))
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_4(self):
		sku = models.SKU(case_upc = int('400000000000'))
		self.assertIs(sku.check_case_upc(), False)

	def test_bad_first_digit_5(self):
		sku = models.SKU(case_upc = int('500000000000'))
		self.assertIs(sku.check_case_upc(), False)

