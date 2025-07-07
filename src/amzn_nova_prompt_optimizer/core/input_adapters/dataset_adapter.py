# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import csv
import random

from abc import ABC, abstractmethod
from typing import List, Dict, Set, Tuple, Union, Any

OUTPUTS_FIELD = "outputs"
INPUTS_FIELD = "inputs"


class DatasetAdapter(ABC):
    def __init__(self, input_columns: Set[str], output_columns: Set[str]):
        """
        Initialize the adapter with input and output column specifications.

        :param input_columns: Set of column names to be included in inputs
        :param output_columns: Set of column names to be included in outputs
        """
        self.input_columns: Set[str] = input_columns
        self.output_columns: Set[str] = output_columns
        if len(output_columns) > 1:
            raise ValueError("output_columns must be a singleton set (contain exactly one element)")
        self.standardized_dataset: List[Dict] = []

    @abstractmethod
    def adapt(self, file_path: str) -> 'DatasetAdapter':
        """
        Load and transform the dataset into the standardized format.

        Standardized Format =

        :param file_path: Path to the input file
        :return: Self for method chaining
        """
        pass

    @abstractmethod
    def _load_dataset(self, file_path: str) -> List[Dict]:
        """
        Protected method to load data from a file.

        :param file_path: Path to the input file
        :return: List of data rows
        """
        pass

    def show(self, n: int = 10) -> None:
        """
        Display the first n rows of the standardized dataset.

        :param n: Number of rows to display (default: 10)
        """
        if not self.standardized_dataset:
            print("Dataset is empty. Call adapt() first.")
            return

        print(f"\nShowing first {min(n, len(self.standardized_dataset))} rows:")
        for i, row in enumerate(self.standardized_dataset[:n]):
            print(f"\nRow {i + 1}:")
            print("Inputs:", row[INPUTS_FIELD])
            print("Outputs:", row[OUTPUTS_FIELD])

    def fetch(self) -> List:
        """
        Returns the standardized dataset.
        """
        return self.standardized_dataset

    def split(self, split_percentage: float, stratify: bool = False) -> Tuple['DatasetAdapter', 'DatasetAdapter']:
        """
        Split the dataset into train and test sets.

        Args:
            split_percentage (float): Percentage of data to use for training (between 0 and 1)
            stratify (bool): Whether to perform stratified split using the first output column

        Returns:
            Tuple of (train_adapter, test_adapter)
        """
        if not 0 < split_percentage < 1:
            raise ValueError("split_percentage must be between 0 and 1")

        train_size = int(len(self.standardized_dataset) * split_percentage)

        if stratify:
            # Group data by stratify column values
            stratified_data: Dict[str, Any] = {}
            for row in self.standardized_dataset:
                key = row[OUTPUTS_FIELD][list(self.output_columns)[0]]
                if key not in stratified_data:
                    stratified_data[key] = []
                stratified_data[key].append(row)

            train_data, test_data = [], []
            for key, group in stratified_data.items():
                group_train_size = int(len(group) * split_percentage)
                train_data.extend(group[:group_train_size])
                test_data.extend(group[group_train_size:])

            # Shuffle the split data
            random.shuffle(train_data)
            random.shuffle(test_data)
        else:
            # Simple random split
            shuffled_data = random.sample(self.standardized_dataset, len(self.standardized_dataset))
            train_data = shuffled_data[:train_size]
            test_data = shuffled_data[train_size:]

        train_adapter = self.__class__(self.input_columns, self.output_columns)
        test_adapter = self.__class__(self.input_columns, self.output_columns)

        train_adapter.standardized_dataset = train_data
        test_adapter.standardized_dataset = test_data

        return train_adapter, test_adapter


class JSONDatasetAdapter(DatasetAdapter):
    def _load_dataset(self, data_source: Union[str, List[Dict]]) -> List[Dict]:
        if isinstance(data_source, str):
            rows = []
            with open(data_source, 'r') as file:
                for line in file:
                    rows.append(json.loads(line.strip()))
            return rows
        elif isinstance(data_source, list):
            return data_source
        else:
            raise ValueError("Invalid data_source type. Expected str or List[Dict]")

    def adapt(self, data_source: Union[str, List[Dict]]) -> DatasetAdapter:
        dataset = self._load_dataset(data_source)

        self.standardized_dataset = []
        for row in dataset:
            standardized_row = {
                INPUTS_FIELD: {
                    col: row.get(col, "") for col in self.input_columns
                },
                OUTPUTS_FIELD: {
                    col: row.get(col, "") for col in self.output_columns
                }
            }
            self.standardized_dataset.append(standardized_row)

        return self

class CSVDatasetAdapter(DatasetAdapter):
    def _load_dataset(self, data_source: Union[str, List[Dict]]) -> List[Dict]:
        if isinstance(data_source, str):
            rows = []
            with open(data_source, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    rows.append(row)
            return rows
        elif isinstance(data_source, list):
            return data_source
        else:
            raise ValueError("Invalid data_source type. Expected str or List[Dict]")

    def adapt(self, data_source: Union[str, List[Dict]]) -> DatasetAdapter:
        dataset = self._load_dataset(data_source)

        self.standardized_dataset = []
        for row in dataset:
            standardized_row = {
                INPUTS_FIELD: {
                    col: row.get(col, "") for col in self.input_columns
                },
                OUTPUTS_FIELD: {
                    col: row.get(col, "") for col in self.output_columns
                }
            }
            self.standardized_dataset.append(standardized_row)

        return self

