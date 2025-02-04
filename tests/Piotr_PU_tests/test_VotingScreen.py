import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox, QDialog, QLabel, QPushButton, QListWidget
from GUI.Voting.VotingScreen import VotingScreen


@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication(sys.argv)
    yield app
    app.quit()


@pytest.fixture
def mock_stack():
    stack = Mock(spec=QStackedWidget)
    stack.addWidget = Mock()
    stack.setCurrentWidget = Mock()
    return stack


# Fixture do mockowania kontrolera bazy danych
@pytest.fixture
def mock_db_controller():
    db_controller = Mock()
    db_controller.get_all_glosowania = Mock(return_value=[])
    db_controller.insert_glosowanie = Mock()
    db_controller.approve_glosowanie = Mock()
    db_controller.update_glosowanie = Mock()
    return db_controller


def test_init_ui(app, mock_stack, mock_db_controller):
    """Test inicjalizacji interfejsu użytkownika."""
    screen = VotingScreen(mock_stack, mock_db_controller)
    assert screen.voting_screen is not None, "Ekran głosowań nie został poprawnie zainicjalizowany."
    mock_stack.addWidget.assert_called()


def test_user_can_create_voting(app, mock_stack, mock_db_controller):
    """Test sprawdzający, czy użytkownik może utworzyć nowe głosowanie."""
    screen = VotingScreen(mock_stack, mock_db_controller)
    dialog_mock = Mock()
    fields_mock = {
        "minimalne udziały": Mock(text=Mock(return_value="10")),
        "temat": Mock(text=Mock(return_value="Nowe głosowanie")),
        "termin (yyyy-mm-dd hh:mm:ss)": Mock(text=Mock(return_value="2025-01-01 12:00:00")),
        "czas trwania (hh:mm:ss)": Mock(text=Mock(return_value="01:00:00")),
        "czy zakończone": Mock(text=Mock(return_value="Nie"))
    }
    screen.save_new_voting(dialog_mock, fields_mock)
    mock_db_controller.insert_glosowanie.assert_called_once()


def test_user_can_approve_voting(app, mock_stack, mock_db_controller):
    """Test sprawdzający, czy użytkownik może zatwierdzić głosowanie."""
    screen = VotingScreen(mock_stack, mock_db_controller)
    screen.current_voting_id = 1
    QMessageBox.question = Mock(return_value=QMessageBox.Yes)
    screen.approve_voting_button = QPushButton()
    screen.approve_voting_button.click()


def test_user_can_edit_voting(app, mock_stack, mock_db_controller):
    """Test sprawdzający, czy użytkownik może edytować istniejące głosowanie."""
    screen = VotingScreen(mock_stack, mock_db_controller)
    screen.current_voting_id = 1
    dialog_mock = Mock()
    fields_mock = {
        "minimalne udziały": Mock(text=Mock(return_value="15")),
        "temat": Mock(text=Mock(return_value="Zmienione głosowanie")),
        "termin (yyyy-mm-dd hh:mm:ss)": Mock(text=Mock(return_value="2025-02-01 15:00:00")),
        "czas trwania (hh:mm:ss)": Mock(text=Mock(return_value="02:00:00")),
        "czy zakończone": Mock(text=Mock(return_value="Nie"))
    }
    screen.save_edited_voting(dialog_mock, fields_mock)
    mock_db_controller.update_glosowanie.assert_called_once_with(1, minimalne_udzialy=15, temat="Zmienione głosowanie",
                                                                 termin="2025-02-01 15:00:00", czas_trwania="02:00:00",
                                                                 czy_zakonczone=False)
