import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, call
import sys
from io import StringIO

from main import MainProgram, main
from operations import Operations
from data import DataProgram

class TestDataProgram:
    def setup_method(self):
        DataProgram.reset()

    def test_initial_balance(self):
        balance = DataProgram.execute("READ")
        assert balance == Decimal("1000.00")

    def test_write_and_read_balance(self):
        DataProgram.execute("WRITE", Decimal("2500.50"))
        balance = DataProgram.execute("READ")
        assert balance == Decimal("2500.50")

    def test_write_negative_balance_raises_error(self):
        with pytest.raises(ValueError, match="Balance cannot be negative"):
            DataProgram.execute("WRITE", Decimal("-100.00"))

    def test_write_zero_balance(self):
        DataProgram.execute("WRITE", Decimal("0.00"))
        balance = DataProgram.execute("READ")
        assert balance == Decimal("0.00")

    def test_invalid_operation(self):
        with pytest.raises(ValueError, match="Invalid operation"):
            DataProgram.execute("INVALID")

    def test_write_without_balance(self):
        with pytest.raises(ValueError, match="Balance required for WRITE operation"):
            DataProgram.execute("WRITE")

    def test_reset_functionality(self):
        DataProgram.execute("WRITE", Decimal("5000.00"))
        DataProgram.reset()
        balance = DataProgram.execute("READ")
        assert balance == Decimal("1000.00")

class TestOperations:
    def setup_method(self):
        DataProgram.reset()

    def test_view_balance(self, capsys):
        Operations.execute("TOTAL")
        captured = capsys.readouterr()
        assert "Current balance: 1000.00" in captured.out

    @patch('operations.input', return_value='250.00')
    def test_credit_valid_amount(self, mock_input, capsys):
        Operations.execute("CREDIT")
        captured = capsys.readouterr()
        assert "Amount credited. New balance: 1250.00" in captured.out
        assert DataProgram.execute("READ") == Decimal("1250.00")

    @patch('operations.input', return_value='0.00')
    def test_credit_zero_amount(self, mock_input, capsys):
        Operations.execute("CREDIT")
        captured = capsys.readouterr()
        assert "Invalid amount. Please try again." in captured.out
        assert DataProgram.execute("READ") == Decimal("1000.00")

    @patch('operations.input', return_value='-100.00')
    def test_credit_negative_amount(self, mock_input, capsys):
        Operations.execute("CREDIT")
        captured = capsys.readouterr()
        assert "Invalid amount. Please try again." in captured.out
        assert DataProgram.execute("READ") == Decimal("1000.00")

    @patch('operations.input', return_value='300.00')
    def test_debit_valid_amount(self, mock_input, capsys):
        Operations.execute("DEBIT")
        captured = capsys.readouterr()
        assert "Amount debited. New balance: 700.00" in captured.out
        assert DataProgram.execute("READ") == Decimal("700.00")

    @patch('operations.input', return_value='1500.00')
    def test_debit_insufficient_funds(self, mock_input, capsys):
        Operations.execute("DEBIT")
        captured = capsys.readouterr()
        assert "Insufficient funds for this debit." in captured.out
        assert DataProgram.execute("READ") == Decimal("1000.00")

    @patch('operations.input', return_value='1000.00')
    def test_debit_exact_balance(self, mock_input, capsys):
        Operations.execute("DEBIT")
        captured = capsys.readouterr()
        assert "Amount debited. New balance: 0.00" in captured.out
        assert DataProgram.execute("READ") == Decimal("0.00")

    @patch('operations.input', return_value='abc')
    def test_invalid_amount_format(self, mock_input, capsys):
        Operations.execute("CREDIT")
        captured = capsys.readouterr()
        assert "Invalid amount format." in captured.out
        assert DataProgram.execute("READ") == Decimal("1000.00")

    def test_invalid_operation(self, capsys):
        Operations.execute("INVALID")
        captured = capsys.readouterr()
        assert "Invalid operation: INVALID" in captured.out

class TestMainProgram:
    def setup_method(self):
        DataProgram.reset()

    @patch('main.input')
    @patch('operations.Operations.execute')
    def test_view_balance_menu_flow(self, mock_ops, mock_input):
        mock_input.side_effect = ['1', '4']
        program = MainProgram()
        program.run()
        mock_ops.assert_called_once_with("TOTAL")

    @patch('main.input')
    @patch('operations.Operations.execute')
    def test_credit_menu_flow(self, mock_ops, mock_input):
        mock_input.side_effect = ['2', '4']
        program = MainProgram()
        program.run()
        mock_ops.assert_called_once_with("CREDIT")

    @patch('main.input')
    @patch('operations.Operations.execute')
    def test_debit_menu_flow(self, mock_ops, mock_input):
        mock_input.side_effect = ['3', '4']
        program = MainProgram()
        program.run()
        mock_ops.assert_called_once_with("DEBIT")

    @patch('main.input', return_value='4')
    def test_exit_flow(self, mock_input, capsys):
        program = MainProgram()
        program.run()
        captured = capsys.readouterr()
        assert "Exiting the program. Goodbye!" in captured.out

    @patch('main.input')
    def test_invalid_menu_choice(self, mock_input, capsys):
        mock_input.side_effect = ['5', '0', 'abc', '4']
        program = MainProgram()
        program.run()
        captured = capsys.readouterr()
        assert "Invalid choice. Please enter a number between 1 and 4." in captured.out
        assert "Invalid input. Please enter a valid number." in captured.out

    def test_menu_display(self, capsys):
        program = MainProgram()
        program._display_menu()
        captured = capsys.readouterr()
        assert "Account Management System" in captured.out
        assert "1. View Balance" in captured.out
        assert "2. Credit Account" in captured.out
        assert "3. Debit Account" in captured.out
        assert "4. Exit" in captured.out

    @patch('main.input')
    def test_keyboard_interrupt_handling(self, mock_input, capsys):
        mock_input.side_effect = KeyboardInterrupt()
        program = MainProgram()
        with pytest.raises(SystemExit) as exc_info:
            program.run()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Program interrupted. Goodbye!" in captured.out

class TestIntegration:
    def setup_method(self):
        DataProgram.reset()

    @patch('main.input')
    @patch('operations.input')
    def test_complete_transaction_flow(self, mock_ops_input, mock_main_input, capsys):
        mock_main_input.side_effect = ['1', '2', '3', '1', '4']
        mock_ops_input.side_effect = ['500.00', '300.00']
        program = MainProgram()
        program.run()
        captured = capsys.readouterr()
        output = captured.out
        assert "Current balance: 1000.00" in output
        assert "Amount credited. New balance: 1500.00" in output
        assert "Amount debited. New balance: 1200.00" in output
        assert "Current balance: 1200.00" in output
        assert "Exiting the program. Goodbye!" in output

    @patch('main.input')
    @patch('operations.input')
    def test_insufficient_funds_integration(self, mock_ops_input, mock_main_input, capsys):
        mock_main_input.side_effect = ['3', '1', '4']
        mock_ops_input.return_value = '1500.00'
        program = MainProgram()
        program.run()
        captured = capsys.readouterr()
        assert "Insufficient funds for this debit." in captured.out
        assert "Current balance: 1000.00" in captured.out

    @patch('main.input')
    @patch('operations.input')
    def test_decimal_precision_integration(self, mock_ops_input, mock_main_input):
        mock_main_input.side_effect = ['2', '2', '3', '1', '4']
        mock_ops_input.side_effect = ['0.01', '0.02', '0.01']
        program = MainProgram()
        program.run()
        assert DataProgram.execute("READ") == Decimal("1000.02")

    def test_direct_module_interaction(self):
        initial = DataProgram.execute("READ")
        assert initial == Decimal("1000.00")
        DataProgram.execute("WRITE", initial + Decimal("500.00"))
        balance = DataProgram.execute("READ")
        DataProgram.execute("WRITE", balance - Decimal("300.00"))
        final = DataProgram.execute("READ")
        assert final == Decimal("1200.00")

    @patch('main.input')
    @patch('operations.input')
    def test_multiple_users_simulation(self, mock_ops_input, mock_main_input):
        mock_main_input.side_effect = ['2', '4']
        mock_ops_input.return_value = '500.00'
        program1 = MainProgram()
        program1.run()
        assert DataProgram.execute("READ") == Decimal("1500.00")
        DataProgram.reset()
        mock_main_input.side_effect = ['1', '4']
        program2 = MainProgram()
        program2.run()
        assert DataProgram.execute("READ") == Decimal("1000.00")

class TestCOBOLCompatibility:
    def setup_method(self):
        DataProgram.reset()

    def test_cobol_call_pattern_operations(self, capsys):
        Operations.execute("TOTAL")
        captured = capsys.readouterr()
        assert "Current balance: 1000.00" in captured.out

    def test_cobol_call_pattern_data(self):
        balance = DataProgram.execute("READ")
        assert balance == Decimal("1000.00")
        DataProgram.execute("WRITE", Decimal("2000.00"))
        new_balance = DataProgram.execute("READ")
        assert new_balance == Decimal("2000.00")

    def test_initial_balance_matches_cobol(self):
        assert DataProgram.execute("READ") == Decimal("1000.00")

    def test_case_insensitive_operations(self):
        assert DataProgram.execute("read") == Decimal("1000.00")
        assert DataProgram.execute("READ") == Decimal("1000.00")
        assert DataProgram.execute("Read") == Decimal("1000.00")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])