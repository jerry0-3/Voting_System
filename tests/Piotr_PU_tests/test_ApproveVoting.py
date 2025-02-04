import unittest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QMessageBox
from GUI.Voting.ApproveVoting import ApproveVoting


class TestApproveVoting(unittest.TestCase):
    """
    Zestaw testów dla klasy ApproveVoting.
    """

    def setUp(self):
        """Inicjalizuje zależności mockowane przed każdym testem."""
        self.db_mock = Mock()
        self.stack_mock = Mock()
        self.choices_screen_mock = Mock()
        self.voting_screen_mock = Mock()
        self.load_votings_callback = Mock()
        self.approve_voting = ApproveVoting(self.db_mock, self.stack_mock)

    def test_check_voting_conditions_pass(self):
        """Test sprawdzający, czy metoda check_voting_conditions zwraca True, gdy jest wystarczająca liczba wyborów."""
        self.db_mock.get_count_mozliwe_wybory.return_value = 3
        result = self.approve_voting.check_voting_conditions(1)
        self.assertTrue(result)

    def test_check_voting_conditions_fail(self):
        """Test sprawdzający, czy metoda check_voting_conditions zwraca False, gdy liczba wyborów jest niewystarczająca."""
        self.db_mock.get_count_mozliwe_wybory.return_value = 1
        result = self.approve_voting.check_voting_conditions(1)
        self.assertFalse(result)

    @patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes)
    @patch.object(QMessageBox, 'information')
    def test_approve_voting_success(self, mock_information, mock_question):
        """Test sprawdzający poprawne zatwierdzenie głosowania, gdy spełnione są warunki."""
        self.db_mock.get_count_mozliwe_wybory.return_value = 3
        self.approve_voting.approve_voting(1, self.choices_screen_mock, self.voting_screen_mock,
                                           self.load_votings_callback)

        self.db_mock.approve_glosowanie.assert_called_once_with(1)
        self.load_votings_callback.assert_called_once()
        mock_information.assert_called_once()

    @patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes)
    @patch.object(QMessageBox, 'warning')
    def test_approve_voting_failure(self, mock_warning, mock_question):
        """Test sprawdzający niepowodzenie zatwierdzenia głosowania, gdy warunki nie są spełnione."""
        self.db_mock.get_count_mozliwe_wybory.return_value = 1
        self.approve_voting.approve_voting(1, self.choices_screen_mock, self.voting_screen_mock,
                                           self.load_votings_callback)

        self.db_mock.approve_glosowanie.assert_not_called()
        self.load_votings_callback.assert_not_called()
        mock_warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
