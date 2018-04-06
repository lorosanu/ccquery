import os
import filecmp
import unittest
from ccquery.data import csv_controller
from ccquery.utils import io_utils

class TestCsvController(unittest.TestCase):
    """Test the csv controller methods"""

    def setUp(self):
        """Set up local variables"""

        self.csv_file = os.path.join(os.path.dirname(__file__), 'sample.csv')
        self.jsonl_file = io_utils.change_extension(self.csv_file, 'jsonl')

        io_utils.check_file_readable(self.csv_file)
        io_utils.check_file_readable(self.jsonl_file)

        self.copy_csv = io_utils.change_extension(self.csv_file, 'copy.csv')
        self.copy_jsonl = io_utils.change_extension(self.csv_file, 'copy.jsonl')

    def test_load_csv(self):
        """Load csv data"""

        columns = [
            'baths', 'beds', 'city', 'latitude', 'longitude',
            'price', 'sale_date', 'sq__ft', 'state', 'type', 'zip']

        first_entry = [
            'SACRAMENTO', 95838, 'CA', 2, 1, 836, 'Residential',
            'Wed May 21 00:00:00 EDT 2008', 59222, 38.631913,
            -121.43487900000001]

        data = csv_controller.load(self.csv_file, header=0)

        self.assertEqual(columns, sorted(list(data.columns)))
        self.assertEqual(10, len(data))
        self.assertEqual(first_entry, list(data.iloc(0)[0]))

    def test_filter_csv(self):
        """Filter csv data"""

        zips = [95838, 95823, 95815, 95815, 95824, 95841, 95842, 95820]
        data = csv_controller.load(self.csv_file, header=0)
        data = csv_controller.filter_data(data, {'city': 'SACRAMENTO'})
        self.assertEqual(zips, list(data.zip))

    def test_load_chunk(self):
        """Load partial data"""
        data = csv_controller.load_chunk(self.csv_file, 5, header=0)
        self.assertEqual(5, len(data))

    def test_stream_csv(self):
        """Load one entry at a time"""
        for row in csv_controller.stream(self.csv_file, header=0):
            self.assertEqual(len(list(row)), len(row.columns))

    def test_stream_field_csv(self):
        """Load one field from one entry at a time"""
        cities = ['SACRAMENTO'] * 8 + ['RANCHO CORDOVA', 'RIO LINDA']
        fields = list(csv_controller.stream_field(
            self.csv_file, 'city', header=0))
        self.assertEqual(cities, fields)

    def test_store_csv(self):
        """Store content to csv file"""

        data = csv_controller.load(self.csv_file, header=0)
        csv_controller.store_csv(data.round(6), self.copy_csv, quoting=0)

        self.assertTrue(
            filecmp.cmp(self.copy_csv, self.csv_file, shallow=False),
            'Output file different from input file')

    def test_store_jsonl(self):
        """Store content to jsonl file"""

        data = csv_controller.load(self.csv_file, header=0)
        csv_controller.store_jsonlines(data.round(6), self.copy_jsonl)

        self.assertTrue(
            filecmp.cmp(self.copy_jsonl, self.jsonl_file, shallow=False),
            'Output file different from input file')

    def tearDown(self):
        """Remove temporary files"""
        if os.path.exists(self.copy_csv):
            os.remove(self.copy_csv)
        if os.path.exists(self.copy_jsonl):
            os.remove(self.copy_jsonl)
