import unittest
import json
import io
import csv

from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter, CSVDatasetAdapter

from unittest.mock import mock_open, patch
from typing import List, Dict

class TestDatasetAdapter(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.input_columns = {"title", "content"}
        self.output_columns = {"sentiment"}
        self.expected_format = [
            {
                "inputs": {"title": "Test1", "content": "Content1"},
                "outputs": {"sentiment": "Positive"}
            },
            {
                "inputs": {"title": "Test2", "content": "Content2"},
                "outputs": {"sentiment": "Negative"}
            }
        ]
        self.test_data = [
            {"title": "Test1", "content": "Content1", "sentiment": "Positive"},
            {"title": "Test2", "content": "Content2", "sentiment": "Negative"}
        ]
        self.input_columns_extended_data = {"title", "content"}
        self.output_columns_extended_data = {"sentiment"}
        self.test_data_extended = [
            {"title": "Test1", "content": "Content1", "sentiment": "Positive"},
            {"title": "Test2", "content": "Content2", "sentiment": "Negative"},
            {"title": "Test1", "content": "Content1", "sentiment": "Positive"},
            {"title": "Test2", "content": "Content2", "sentiment": "Negative"},
            {"title": "Test1", "content": "Content1", "sentiment": "Positive"},
            {"title": "Test2", "content": "Content2", "sentiment": "Negative"},
            {"title": "Test1", "content": "Content1", "sentiment": "Positive"},
            {"title": "Test2", "content": "Content2", "sentiment": "Negative"}
        ]


    def create_mock_csv(self, data: List[Dict]) -> str:
        """Helper method to create mock CSV content"""
        output = io.StringIO()
        if not data:
            return ""

        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def test_dataset_adapter_initialization(self):
        """Test DatasetAdapter initialization"""
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        self.assertEqual(adapter.input_columns, self.input_columns)
        self.assertEqual(adapter.output_columns, self.output_columns)
        self.assertEqual(adapter.standardized_dataset, [])

    def test_show_empty_dataset(self):
        """Test show method with empty dataset"""
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        with patch('builtins.print') as mock_print:
            adapter.show()
            mock_print.assert_called_with("Dataset is empty. Call adapt() first.")

    def test_json_dataset_adapter_load(self):
        """Test JSONDatasetAdapter _load_dataset method"""
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        mock_json_data = '\n'.join(json.dumps(row) for row in self.test_data)

        with patch('builtins.open', mock_open(read_data=mock_json_data)):
            loaded_data = adapter._load_dataset('dummy_path.json')
            self.assertEqual(loaded_data, self.test_data)

    def test_json_dataset_adapter_adapt(self):
        """Test JSONDatasetAdapter adapt method"""
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        mock_json_data = '\n'.join(json.dumps(row) for row in self.test_data)

        with patch('builtins.open', mock_open(read_data=mock_json_data)):
            adapter.adapt('dummy_path.json')
            self.assertEqual(adapter.standardized_dataset, self.expected_format)

    def test_csv_dataset_adapter_load(self):
        """Test CSVDatasetAdapter _load_dataset method"""
        adapter = CSVDatasetAdapter(self.input_columns, self.output_columns)
        mock_csv_data = self.create_mock_csv(self.test_data)

        with patch('builtins.open', mock_open(read_data=mock_csv_data)):
            loaded_data = adapter._load_dataset('dummy_path.csv')
            self.assertEqual(loaded_data, self.test_data)

    def test_csv_dataset_adapter_adapt(self):
        """Test CSVDatasetAdapter adapt method"""
        adapter = CSVDatasetAdapter(self.input_columns, self.output_columns)
        mock_csv_data = self.create_mock_csv(self.test_data)

        with patch('builtins.open', mock_open(read_data=mock_csv_data)):
            adapter.adapt('dummy_path.csv')
            self.assertEqual(adapter.standardized_dataset, self.expected_format)

    def test_fetch_method(self):
        """Test fetch method"""
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        mock_json_data = '\n'.join(json.dumps(row) for row in self.test_data)

        with patch('builtins.open', mock_open(read_data=mock_json_data)):
            adapter.adapt('dummy_path.json')
            fetched_data = adapter.fetch()
            self.assertEqual(fetched_data, adapter.standardized_dataset)

    def test_show_method_with_data(self):
        """Test show method with data"""
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        mock_json_data = '\n'.join(json.dumps(row) for row in self.test_data)

        with patch('builtins.open', mock_open(read_data=mock_json_data)):
            adapter.adapt('dummy_path.json')
            with patch('builtins.print') as mock_print:
                adapter.show(1)
                mock_print.assert_any_call("\nShowing first 1 rows:")

    def test_missing_columns(self):
        """Test handling of missing columns"""
        adapter = JSONDatasetAdapter({"nonexistent"}, {"missing"})
        mock_json_data = json.dumps({"title": "Test1", "content": "Content1"})

        with patch('builtins.open', mock_open(read_data=mock_json_data)):
            adapter.adapt('dummy_path.json')
            self.assertEqual(
                adapter.standardized_dataset[0],
                {"inputs": {"nonexistent": ""}, "outputs": {"missing": ""}}
            )

    def test_json_adapter_from_variable(self):
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        adapter.adapt(self.test_data)
        self.assertEqual(adapter.standardized_dataset, self.expected_format)

    def test_csv_adapter_from_variable(self):
        adapter = CSVDatasetAdapter(self.input_columns, self.output_columns)
        adapter.adapt(self.test_data)
        self.assertEqual(adapter.standardized_dataset, self.expected_format)

    def _test_split_with_no_stratify(self, adapter):
        adapter.adapt(self.test_data_extended)
        train, test = adapter.split(split_percentage=0.7)
        self.assertEqual(len(train.fetch()), 5)
        self.assertEqual(len(test.fetch()), 3)

    def test_json_adapter_split(self):
        adapter = JSONDatasetAdapter(self.input_columns_extended_data, self.output_columns_extended_data)
        self._test_split_with_no_stratify(adapter)

    def test_csv_adapter_split(self):
        adapter = CSVDatasetAdapter(self.input_columns_extended_data, self.output_columns_extended_data)
        self._test_split_with_no_stratify(adapter)

    def _test_split_with_stratify(self, adapter):
        adapter.adapt(self.test_data_extended)
        train, test = adapter.split(split_percentage=0.7, stratify=True)
        self.assertEqual(len(train.fetch()), 4)
        self.assertEqual(len(test.fetch()), 4)

        # Check if stratification is maintained
        train_labels = [row["outputs"]["sentiment"] for row in train.fetch()]
        test_labels = [row["outputs"]["sentiment"] for row in test.fetch()]
        self.assertTrue(set(train_labels) == set(test_labels) == {"Positive", "Negative"})

    def test_json_adapter_stratified_split(self):
        adapter = JSONDatasetAdapter(self.input_columns_extended_data, self.output_columns_extended_data)
        self._test_split_with_stratify(adapter)

    def test_csv_adapter_stratified_split(self):
        adapter = CSVDatasetAdapter(self.input_columns_extended_data, self.output_columns_extended_data)
        self._test_split_with_stratify(adapter)

    def test_invalid_split_percentage(self):
        adapter = JSONDatasetAdapter(self.input_columns, self.output_columns)
        adapter.adapt(self.test_data_extended)
        with self.assertRaises(ValueError):
            adapter.split(split_percentage=1.5)
        with self.assertRaises(ValueError):
            adapter.split(split_percentage=-0.5)

    def test_extra_output_columns(self):
        with self.assertRaises(ValueError):
            extra_output_columns = {"abc", "xyz"}
            JSONDatasetAdapter(self.input_columns, extra_output_columns)