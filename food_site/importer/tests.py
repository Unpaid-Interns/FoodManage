from django.test import TestCase
from django.test import Client
from sku_manage import models
from importer import CSVImport

path_prefix = "importer/import_test_suite/"


class HTMLTests(TestCase):

    def test_html(self):
        pass
        # c = Client()
        # with open('file.csv') as fp:
        #     response = c.post('simple_upload', {'name': 'myfile', 'attachment': fp})
        # self.assertIs()


class NoErrorsUpload(TestCase):
    ingredients_file = 'ingredients_single_correct_upload.csv'
    product_lines_file = 'product_lines_single_correct_upload.csv'
    formulas_file = 'formulas_single_correct_upload.csv'
    skus_file = 'skus_single_correct_upload.csv'

    def test_single_correct_ingredients_upload(self):
        importer = CSVImport.CSVImport()
        filename = path_prefix + self.ingredients_file
        importer.add_filename(filename)
        success, conflicts_exist, result_message = importer.import_csv()
        self.assertIs(success, True, result_message)
        self.assertIs(conflicts_exist, False, result_message)
        self.assertContains(result_message, "Import completed successfully", result_message)

    def test_single_correct_product_lines_upload(self):
        importer = CSVImport.CSVImport()
        filename = path_prefix + self.product_lines_file
        importer.add_filename(filename)
        success, conflicts_exist, result_message = importer.import_csv()
        self.assertIs(success, True, result_message)
        self.assertIs(conflicts_exist, False, result_message)
        self.assertContains(result_message, "Import completed successfully", result_message)

    def test_single_correct_formulas_upload(self):
        importer = CSVImport.CSVImport()
        filename = path_prefix + self.formulas_file
        importer.add_filename(filename)
        success, conflicts_exist, result_message = importer.import_csv()
        self.assertIs(success, True, result_message)
        self.assertIs(conflicts_exist, False, result_message)
        self.assertContains(result_message, "Import completed successfully", result_message)

    def test_single_correct_sku_upload(self):
        importer = CSVImport.CSVImport()
        filename = path_prefix + self.skus_file
        importer.add_filename(filename)
        success, conflicts_exist, result_message = importer.import_csv()
        self.assertIs(success, True, result_message)
        self.assertIs(conflicts_exist, False, result_message)
        self.assertContains(result_message, "Import completed successfully", result_message)



