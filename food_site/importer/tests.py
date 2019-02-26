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


class LowercaseHeaderNoErrorsUpload(TestCase):
    pass


class NoErrorsUpload(TestCase):
    ingredients_file = 'ingredients_correct.csv'
    product_lines_file = 'product_lines_correct.csv'
    formulas_file = 'formulas_correct.csv'
    skus_file = 'skus_correct.csv'
    # models.ManufacturingLine(name='Line1', shortname='line1', comment='').save()

    def test_ingredients_correct(self):
        importer = CSVImport.CSVImport()
        importer.add_filename(path_prefix + self.ingredients_file)
        success, conflicts_exist, result_message = importer.import_csv()
        self.assertIs(success, True, result_message)
        self.assertIs(conflicts_exist, False, result_message)
        self.assertIn("Import completed successfully", result_message, result_message)
        # importer.clear_filenames()
        # importer.add_filename(path_prefix + self.product_lines_file)
        # success, conflicts_exist, result_message = importer.import_csv()
        # self.assertIs(success, True, result_message)
        # self.assertIs(conflicts_exist, False, result_message)
        # self.assertIn("Import completed successfully", result_message, result_message)
        # importer.clear_filenames()
        # importer.add_filename(path_prefix + self.formulas_file)
        # success, conflicts_exist, result_message = importer.import_csv()
        # self.assertIs(success, True, result_message)
        # self.assertIs(conflicts_exist, False, result_message)
        # self.assertIn("Import completed successfully", result_message, result_message)
        # importer.clear_filenames()
        # importer.add_filename(path_prefix + self.skus_file)
        # success, conflicts_exist, result_message = importer.import_csv()
        # self.assertIs(success, True, result_message)
        # self.assertIs(conflicts_exist, False, result_message)
        # self.assertIn("Import completed successfully", result_message, result_message)

    # def test_correct_product_lines_upload(self):
    #     importer = CSVImport.CSVImport()
    #     filename = path_prefix + self.product_lines_file
    #     importer.add_filename(filename)
    #     success, conflicts_exist, result_message = importer.import_csv()
    #     self.assertIs(success, True, result_message)
    #     self.assertIs(conflicts_exist, False, result_message)
    #     self.assertIn("Import completed successfully", result_message, result_message)
    #
    # def test_correct_formulas_upload(self):
    #     importer = CSVImport.CSVImport()
    #     filename = path_prefix + self.formulas_file
    #     importer.add_filename(filename)
    #     success, conflicts_exist, result_message = importer.import_csv()
    #     self.assertIs(success, True, result_message)
    #     self.assertIs(conflicts_exist, False, result_message)
    #     self.assertIn("Import completed successfully", result_message, result_message)
    #
    # def test_correct_sku_upload(self):
    #     importer = CSVImport.CSVImport()
    #     filename = path_prefix + self.skus_file
    #     importer.add_filename(filename)
    #     success, conflicts_exist, result_message = importer.import_csv()
    #     self.assertIs(success, True, result_message)
    #     self.assertIs(conflicts_exist, False, result_message)
    #     self.assertIn("Import completed successfully", result_message, result_message)


def test_correct(test, filename):
    importer = CSVImport.CSVImport()
    filename = path_prefix + filename
    importer.add_filename(filename)
    success, conflicts_exist, result_message = importer.import_csv()
    test.assertIs(success, True, result_message)
    test.assertIs(conflicts_exist, False, result_message)
    test.assertIn("Import completed successfully", result_message, result_message)


