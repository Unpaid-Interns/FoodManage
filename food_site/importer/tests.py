from django.test import TestCase
from django.test import Client
from sku_manage import models
from importer import CSVImport


# Create your tests here.


class HTMLTests(TestCase):

    def test_html(self):
        pass
        # c = Client()
        # with open('file.csv') as fp:
        #     response = c.post('simple_upload', {'name': 'myfile', 'attachment': fp})
        # self.assertIs()


class NoErrorsUpload(TestCase):

    def test_single_correct_sku_upload(self):
        importer = CSVImport.CSVImport()
        filename = 'importer/import_test_suite/skus_single_correct_upload.csv'
        importer.add_filename(filename)
        success, conflicts_exist, result_message = importer.import_csv()
        self.assertIs(success, True, result_message)
        self.assertIs(conflicts_exist, False, result_message)
        self.assertContains(result_message, "Import completed successfully", result_message)

