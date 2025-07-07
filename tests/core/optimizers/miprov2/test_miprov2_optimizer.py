import os
import unittest
from unittest.mock import Mock, patch, PropertyMock, MagicMock

import dspy  # type: ignore

from amzn_nova_prompt_optimizer.core.optimizers import MIPROv2OptimizationAdapter
from amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer import NovaMIPROv2OptimizationAdapter
from amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer import PredictorFactory
from amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_grounded_proposer import NovaGroundedProposer


class TestPredictorFactory(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create mock dataset adapter with proper property configuration
        self.mock_dataset_adapter = Mock()

        # Configure the input_columns property
        type(self.mock_dataset_adapter).input_columns = PropertyMock(
            return_value=["input1", "input2"]
        )

        # Configure the output_columns property
        type(self.mock_dataset_adapter).output_columns = PropertyMock(
            return_value=["output1"]
        )

    def _get_dspy_field_info(self, field):
        field_type = field.json_schema_extra.get("__dspy_field_type")
        if field_type is None:
            raise ValueError(f"Field {field} does not have a __dspy_field_type")
        return field_type

    def test_create_signature(self):
        # Test signature creation
        SignatureClass = PredictorFactory.create_signature(self.mock_dataset_adapter)
        input_fields = SignatureClass.input_fields.items()
        output_fields = SignatureClass.output_fields.items()
        self.assertEqual(len(input_fields), 2)
        self.assertEqual(len(output_fields), 1)
        for _, field_info in input_fields:
            # Verify field types
            self.assertEqual(self._get_dspy_field_info(field_info), "input")
        for _, field_info in output_fields:
            # Verify field types
            self.assertEqual(self._get_dspy_field_info(field_info), "output")

    def test_create_predictor(self):
        # Test predictor creation
        prompt = "Test prompt"
        temperature = 0.5

        predictor = PredictorFactory.create_predictor(
            self.mock_dataset_adapter,
            prompt,
            temperature
        )

        # Verify predictor properties
        self.assertIsInstance(predictor, dspy.Predict)
        self.assertEqual(predictor.temperature, temperature)
        self.assertEqual(predictor.signature.instructions, prompt)


class TestMIPROOptimizationAdapter(unittest.TestCase):
    def setUp(self):
        # Create mock adapters
        self.mock_dataset_adapter = Mock()
        self.mock_prompt_adapter = Mock()
        self.mock_metric_adapter = Mock()
        self.mock_inference_adapter = Mock()

        # Configure mock dataset adapter
        self.mock_dataset_adapter.input_columns = ["input1"]
        self.mock_dataset_adapter.output_columns = ["output1"]
        self.mock_dataset_adapter.fetch.return_value = [
            {
                "inputs": {"input1": "test input 1"},
                "outputs": {"output1": "test output 1"}
            },
            {
                "inputs": {"input1": "test input 2"},
                "outputs": {"output1": "test output 2"}
            }
        ]

        # Configure mock prompt adapter
        self.mock_prompt_adapter.fetch.return_value = {
            'user_prompt': {
                "template": "user prompt",
                'variables': ['var1', 'var2']  # Provide actual list instead of Mock
            },
            'system_prompt': {
                "template": "system prompt",
                'variables': ['var1', 'var2']  # Provide actual list instead of Mock
            }
        }
        self.mock_prompt_adapter.fetch_system_template.return_value = "Test System prompt template"
        self.mock_prompt_adapter.fetch_user_template.return_value = "Test User prompt template"
        self.mock_prompt_adapter.__class__ = Mock()
        self.mock_prompt_adapter.__class__.return_value = Mock()

        # Configure mock inference adapter
        self.mock_inference_adapter.region = 'us-west-2'

        # Create adapter instance
        self.adapter = MIPROv2OptimizationAdapter(
            dataset_adapter=self.mock_dataset_adapter,
            prompt_adapter=self.mock_prompt_adapter,
            metric_adapter=self.mock_metric_adapter,
            inference_adapter=self.mock_inference_adapter
        )

    def test_process_dataset_adapter(self):
        train_data, test_data = self.adapter._process_dataset_adapter(train_split=0.5)

        # Verify data splitting
        self.assertEqual(len(train_data), 1)
        self.assertEqual(len(test_data), 1)
        self.assertIsInstance(train_data[0], dspy.Example)
        self.assertIsInstance(test_data[0], dspy.Example)

    def test_dspy_metric(self):
        # Create mock examples
        gold = Mock()
        pred = Mock()
        setattr(gold, "output1", "true")
        setattr(pred, "output1", "pred")

        self.adapter._dspy_metric(gold, pred)

        # Verify metric calculation
        self.mock_metric_adapter.apply.assert_called_once_with("pred", "true")

    def test_construct_optimized_system_prompt(self):
        """Test _construct_optimized_system_prompt with valid user component"""
        # Mock prompt_adapter.fetch()
        self.mock_prompt_adapter.fetch.return_value = {
            "user_prompt": {
                "variables": ["input1"]
            }
        }
        miprov2_instructions = "Test Instructions"
        system_prompt = self.adapter._construct_optimized_system_prompt(miprov2_instructions)

        expected_prompt = (
            "Your input fields are:\n"
            "1. input1\n"
            "Your output fields are:\n"
            "1. output1\n"
            "\n"
            "All interactions will be structured in the following way, with the appropriate values filled in.\n"
            "[[ ## input1 ## ]]\ninput1\n"
            "[[ ## output1 ## ]]\noutput1\n"
            "\n"
            "[[ ## completed ## ]]\n"
            "\n"
            "In adhering to this structure, your objective is: \n        Test Instructions"
        )
        self.assertEqual(system_prompt, expected_prompt)

    def test_construct_optimized_user_prompt_with_variables(self):
        """Test _construct_optimized_user_prompt with valid user component"""
        # Mock prompt_adapter.fetch()
        self.mock_prompt_adapter.fetch.return_value = {
            "user_prompt": {
                "variables": ["var1", "var2"]
            }
        }

        user_prompt, variables = self.adapter._construct_optimized_user_prompt()

        expected_prompt = (
            "[[ ## var1 ## ]]\n"
            "{{ var1 }}\n"
            "[[ ## var2 ## ]]\n"
            "{{ var2 }}\n"
            "\n"
            "Respond with the corresponding output fields, starting with the field [[ ## output1 ## ]], "
            "and then ending with the marker for [[ ## completed ## ]]."
        )

        self.assertEqual(user_prompt, expected_prompt)
        self.assertEqual(variables, ["var1", "var2"])

    def test_construct_optimized_user_prompt_without_user_component(self):
        """Test _construct_optimized_user_prompt without user component"""
        # Mock prompt_adapter.fetch() to return empty dict
        self.mock_prompt_adapter.fetch.return_value = {}

        result, variable = self.adapter._construct_optimized_user_prompt()
        self.assertIsNone(result)
        self.assertIsNone(variable)

    def test_create_few_shot_samples(self):
        """Test _create_few_shot_samples with valid predictor"""
        # Create mock predictor with demos
        self.adapter.dataset_adapter = Mock()
        self.adapter.dataset_adapter.input_columns = ["input1", "input2"]
        self.adapter.dataset_adapter.output_columns = ["output1"]
        mock_predictor = Mock(spec=dspy.Predict)
        mock_predictor.demos = [
            {
                "input1": "test input 1",
                "input2": "test input 2",
                "output1": "test output 1"
            },
            {
                "input1": "test input 3",
                "input2": "test input 4",
                "output1": "test output 2"
            }
        ]

        samples, format_type = self.adapter._create_few_shot_samples(mock_predictor)
        # Verify the samples structure
        self.assertEqual(len(samples), 2)
        self.assertEqual(format_type, "converse")

        # Verify first sample
        expected_input_1 = (
            "[[ ## input1 ## ]]\ntest input 1\n"
            "[[ ## input2 ## ]]\ntest input 2\n"
        )
        self.assertEqual(samples[0]["input"], expected_input_1)
        self.assertEqual(samples[0]["output"], "[[ ## output1 ## ]]\ntest output 1\n")

        # Verify second sample
        expected_input_2 = (
            "[[ ## input1 ## ]]\ntest input 3\n"
            "[[ ## input2 ## ]]\ntest input 4\n"
        )
        self.assertEqual(samples[1]["input"], expected_input_2)
        self.assertEqual(samples[1]["output"], "[[ ## output1 ## ]]\ntest output 2\n")

    def test_create_optimized_prompt_adapter(self):
        """Test _create_optimized_prompt_adapter"""
        # Mock predictor with signature
        mock_predictor = Mock(spec=dspy.Predict)
        mock_predictor.signature = Mock()
        mock_predictor.signature.instructions = "Test instructions"

        mock_predictor.demos = [
            {
                "input1": "test input",
                "input2": "test input 2",
                "output1": "test output"
            }
        ]

        # Rest of the test remains the same
        mock_prompt_adapter_class = Mock()
        mock_new_adapter = Mock()
        mock_prompt_adapter_class.return_value = mock_new_adapter
        self.mock_prompt_adapter.__class__ = mock_prompt_adapter_class

        with patch.object(
                self.adapter,
                '_construct_optimized_user_prompt',
                return_value=("test prompt", ["var1"])
        ):
            result = self.adapter._create_optimized_prompt_adapter(mock_predictor)

        mock_new_adapter.set_system_prompt.assert_called_once_with(
            content="Your input fields are:\n"
                    "1. input1\n"
                    "Your output fields are:\n"
                    "1. output1\n"
                    "\n"
                    "All interactions will be structured in the following way, with the appropriate values filled in.\n"
                    "[[ ## input1 ## ]]\ninput1\n"
                    "[[ ## output1 ## ]]\noutput1\n"
                    "\n"
                    "[[ ## completed ## ]]\n"
                    "\n"
                    "In adhering to this structure, your objective is: \n        Test instructions"
        )
        mock_new_adapter.set_user_prompt.assert_called_once_with(
            content="test prompt",
            variables=["var1"]
        )
        mock_new_adapter.add_few_shot.assert_called_once()
        mock_new_adapter.adapt.assert_called_once()

        self.assertEqual(result, mock_new_adapter)

    @patch('amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer.dspy.LM')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer.MIPROv2')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer.dspy.configure')
    def test_optimize_without_nova_tips(self, mock_configure, mock_miprov2, mock_lm):
        # Setup mock objects
        mock_optimizer = MagicMock()
        mock_miprov2.return_value = mock_optimizer
        mock_optimized_predictor = MagicMock()
        mock_optimizer.compile.return_value = mock_optimized_predictor
        expected_instructions = "Test Instructions"
        mock_optimized_predictor.signature.instructions = expected_instructions

        # Create a mock for the original _propose_instructions method
        original_propose_instructions = MagicMock()
        mock_optimizer._propose_instructions = original_propose_instructions
        
        # Setup mock prompt adapter for return value
        mock_return_prompt_adapter = MagicMock()
        self.mock_prompt_adapter.__class__.return_value = mock_return_prompt_adapter
        
        # Call optimize with nova_tips=False (default)
        result = self.adapter.optimize(
            task_model_id="test-task-model",
            prompter_model_id="test-prompter-model",
            num_candidates=5,
            num_threads=1,
            num_trials=10,
            max_bootstrapped_demos=2,
            max_labeled_demos=2,
            minibatch_size=10,
            train_split=0.7
        )

        # Assert AWS REGION is default to us-west-2
        self.assertEqual(os.getenv('AWS_REGION_NAME'), 'us-west-2')

        # Verify that MIPROv2 was initialized correctly
        mock_miprov2.assert_called_once()

        # Verify _propose_instructions still the original one when nova_tips=False
        self.assertEqual(mock_optimizer._propose_instructions, original_propose_instructions)

        # Simulate calling the patched _propose_instructions method to verify NovaGroundedProposer is used
        # We need to call the method with the expected arguments to trigger the monkey patching
        args = [MagicMock(), MagicMock(), MagicMock(), 10, True, True, True, True]

        # Create a side effect for the patched method to verify NovaGroundedProposer is used
        def side_effect(*args, **kwargs):
            # This will be called when the patched method is called
            # We can verify that dspy.teleprompt.mipro_optimizer_v2.GroundedProposer was not replaced with NovaGroundedProposer
            import dspy.propose # type: ignore
            self.assertEqual(dspy.teleprompt.mipro_optimizer_v2.GroundedProposer, dspy.propose.GroundedProposer)
            return MagicMock()

        # Set up the side effect on the original method
        original_propose_instructions.side_effect = side_effect

        # Call the patched method - this should trigger the monkey patching
        mock_optimizer._propose_instructions(*args)
        
        # Verify the optimizer was compiled without monkey patching
        mock_optimizer.compile.assert_called_once()

        # Verify the result is a prompt adapter
        self.assertEqual(result, mock_return_prompt_adapter)


class TestNovaMIPROv2OptimizationAdapter(unittest.TestCase):
    def setUp(self):
        # Create mock adapters
        self.mock_dataset_adapter = Mock()
        self.mock_prompt_adapter = Mock()
        self.mock_metric_adapter = Mock()
        self.mock_inference_adapter = Mock()

        # Configure mock dataset adapter
        self.mock_dataset_adapter.input_columns = ["input1"]
        self.mock_dataset_adapter.output_columns = ["output1"]
        self.mock_dataset_adapter.fetch.return_value = [
            {
                "inputs": {"input1": "test input 1"},
                "outputs": {"output1": "test output 1"}
            },
            {
                "inputs": {"input1": "test input 2"},
                "outputs": {"output1": "test output 2"}
            }
        ]

        # Configure mock prompt adapter
        self.mock_prompt_adapter.fetch.return_value = {
            'user_prompt': {
                "template": "user prompt",
                'variables': ['var1', 'var2']  # Provide actual list instead of Mock
            },
            'system_prompt': {
                "template": "system prompt",
                'variables': ['var1', 'var2']  # Provide actual list instead of Mock
            }
        }
        self.mock_prompt_adapter.fetch_system_template.return_value = "Test System prompt template"
        self.mock_prompt_adapter.fetch_user_template.return_value = "Test User prompt template"
        self.mock_prompt_adapter.__class__ = Mock()
        self.mock_prompt_adapter.__class__.return_value = Mock()

        # Configure mock inference adapter
        self.mock_inference_adapter.region = 'us-east-1'

        # Create adapter instance
        self.adapter = NovaMIPROv2OptimizationAdapter(
            dataset_adapter=self.mock_dataset_adapter,
            prompt_adapter=self.mock_prompt_adapter,
            metric_adapter=self.mock_metric_adapter,
            inference_adapter=self.mock_inference_adapter
        )

    def test_process_dataset_adapter(self):
        train_data, test_data = self.adapter._process_dataset_adapter(train_split=0.5)

        # Verify data splitting
        self.assertEqual(len(train_data), 1)
        self.assertEqual(len(test_data), 1)
        self.assertIsInstance(train_data[0], dspy.Example)
        self.assertIsInstance(test_data[0], dspy.Example)

    def test_dspy_metric(self):
        # Create mock examples
        gold = Mock()
        pred = Mock()
        setattr(gold, "output1", "true")
        setattr(pred, "output1", "pred")

        self.adapter._dspy_metric(gold, pred)

        # Verify metric calculation
        self.mock_metric_adapter.apply.assert_called_once_with("pred", "true")

    def test_construct_optimized_user_prompt_without_user_component(self):
        """Test _construct_optimized_user_prompt without user component"""
        # Mock prompt_adapter.fetch() to return empty dict
        self.mock_prompt_adapter.fetch.return_value = {}

        result, variable = self.adapter._construct_optimized_user_prompt()
        self.assertIsNone(result)
        self.assertIsNone(variable)

    def test_create_few_shot_samples_with_user_prompt_template(self):
        """Test _create_few_shot_samples with valid predictor"""
        # Create mock predictor with demos
        self.adapter.dataset_adapter = Mock()
        user_prompt = "This is {{ var1 }} and {{var2}}"
        user_variables = ['var1', 'var2']
        self.adapter.dataset_adapter.input_columns = ["var1", "var2"]
        self.adapter.dataset_adapter.output_columns = ["output"]
        mock_predictor = Mock(spec=dspy.Predict)
        mock_predictor.demos = [
            {
                "var1": "test input 1",
                "var2": "test input 2",
                "output": "test output 1"
            },
            {
                "var1": "test input 3",
                "var2": "test input 4",
                "output": "test output 2"
            }
        ]

        samples, format_type = self.adapter._create_few_shot_samples_with_prompt(mock_predictor,
                                                                                 user_prompt, user_variables)
        # Verify the samples structure
        self.assertEqual(len(samples), 2)
        self.assertEqual(format_type, "converse")

        # Verify first sample
        expected_input_1 = (
            "This is test input 1 and test input 2"
        )
        self.assertEqual(samples[0]["input"], expected_input_1)
        self.assertEqual(samples[0]["output"], "test output 1")

        # Verify second sample
        expected_input_2 = (
            "This is test input 3 and test input 4"
        )
        self.assertEqual(samples[1]["input"], expected_input_2)
        self.assertEqual(samples[1]["output"], "test output 2")

    def test_create_optimized_prompt_adapter(self):
        """Test _create_optimized_prompt_adapter"""
        # Mock predictor with signature
        mock_predictor = Mock(spec=dspy.Predict)
        mock_predictor.signature = Mock()
        mock_predictor.signature.instructions = "Test instructions"

        mock_predictor.demos = [
            {
                "input1": "test input",
                "input2": "test input 2",
                "output1": "test output"
            }
        ]

        # Rest of the test remains the same
        mock_prompt_adapter_class = Mock()
        mock_new_adapter = Mock()
        mock_prompt_adapter_class.return_value = mock_new_adapter
        self.mock_prompt_adapter.__class__ = mock_prompt_adapter_class

        with patch.object(
                self.adapter,
                '_create_few_shot_samples_with_prompt',
                return_value=([{"input": "input_message", "output": "output_message"}], "converse")
        ):
            result = self.adapter._create_optimized_prompt_adapter(mock_predictor)

        mock_new_adapter.set_system_prompt.assert_called_once_with(
            content="Test instructions"
        )
        mock_new_adapter.set_user_prompt.assert_called_once_with(
            content="Test User prompt template",
            variables=["var1", "var2"]
        )
        mock_new_adapter.add_few_shot.assert_called_once()
        mock_new_adapter.adapt.assert_called_once()

        self.assertEqual(result, mock_new_adapter)

    @patch('amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer.dspy.LM')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer.MIPROv2')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer.dspy.configure')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_grounded_proposer.NovaGroundedProposer')
    @patch('dspy.propose.GroundedProposer')
    def test_optimize_with_nova_tips(self, mock_grounded_proposer, mock_nova_grounded_proposer, mock_configure, mock_miprov2, mock_lm):
        # Setup mock objects
        mock_optimizer = MagicMock()
        mock_miprov2.return_value = mock_optimizer
        mock_optimized_predictor = MagicMock()
        mock_optimizer.compile.return_value = mock_optimized_predictor

        expected_instructions = "Test Instructions"
        mock_optimized_predictor.signature.instructions = expected_instructions

        # Create a mock for the original _propose_instructions method
        original_propose_instructions = MagicMock()
        mock_optimizer._propose_instructions = original_propose_instructions

        # Setup mock prompt adapter for return value
        mock_return_prompt_adapter = MagicMock()
        self.mock_prompt_adapter.__class__.return_value = mock_return_prompt_adapter
        with patch.object(
                self.adapter,
                '_create_few_shot_samples_with_prompt',
                return_value=([{"input": "input_message", "output": "output_message"}], "converse")
        ):
            # Call optimize with nova_tips=True
            result = self.adapter.optimize(
                task_model_id="test-task-model",
                prompter_model_id="test-prompter-model",
                num_candidates=5,
                num_threads=1,
                num_trials=10,
                max_bootstrapped_demos=2,
                max_labeled_demos=2,
                minibatch_size=10,
                train_split=0.7
            )

        # Assert AWS REGION has been set
        self.assertEqual(os.getenv('AWS_REGION_NAME'), 'us-east-1')

        # Verify that MIPROv2 was initialized correctly
        mock_miprov2.assert_called_once()

        # Verify that the monkey patching was applied by checking if the _propose_instructions
        # method was replaced with a new function that uses NovaGroundedProposer
        self.assertNotEqual(mock_optimizer._propose_instructions, original_propose_instructions)

        # Simulate calling the patched _propose_instructions method to verify NovaGroundedProposer is used
        # We need to call the method with the expected arguments to trigger the monkey patching
        args = [MagicMock(), MagicMock(), MagicMock(), 10, True, True, True, True]

        # Create a side effect for the patched method to verify NovaGroundedProposer is used
        def side_effect(*args, **kwargs):
            # This will be called when the patched method is called
            # We can verify that dspy.teleprompt.mipro_optimizer_v2.GroundedProposer was temporarily replaced with NovaGroundedProposer
            self.assertEqual(dspy.teleprompt.mipro_optimizer_v2.GroundedProposer, NovaGroundedProposer)
            return MagicMock()

        # Set up the side effect on the original method
        original_propose_instructions.side_effect = side_effect

        # Call the patched method - this should trigger the monkey patching
        mock_optimizer._propose_instructions(*args)

        # Verify the optimizer was compiled
        mock_optimizer.compile.assert_called_once()


        # Verify the result is a prompt adapter
        self.assertEqual(result, mock_return_prompt_adapter)