import pytest
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox, QInputDialog
from GUI.Voting.VotingScreen import VotingScreen


# Fixture do inicjalizacji QApplication
@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication(sys.argv)
    yield app
    app.quit()


# Fixture do mockowania obiektu QStackedWidget
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
    db_controller.get_all_glosowania = Mock(return_value=[
        (1, "Głosowanie 1", "2025-02-01 10:00:00", "01:00:00", True),
        (2, "Głosowanie 2", "2025-02-02 10:00:00", "02:00:00", False),
    ])
    db_controller.get_glosowanie_by_id = Mock(return_value=(1, "Głosowanie 1", "2025-02-01 10:00:00", "01:00:00", True))
    db_controller.get_all_mozliwe_wybory_by_glosowanie_id = MagicMock(return_value=[
        (1, "Pierwszy wybór"),
        (2, "Drugi wybór")
    ])
    db_controller.insert_mozliwy_wybor = MagicMock()
    db_controller.update_mozliwy_wybor = MagicMock()
    db_controller.delete_mozliwy_wybor = MagicMock()
    return db_controller


def test_init_ui(app, mock_stack, mock_db_controller):
    # Tworzenie obiektu VotingScreen
    screen = VotingScreen(mock_stack, mock_db_controller)

    # Testy inicjalizacji
    assert screen.choices_screen is not None, "Ekran 'choices_screen' nie został poprawnie zainicjalizowany."
    assert screen.choice_screen is not None, "Ekran 'choice_screen' nie został poprawnie zainicjalizowany."

    # Sprawdzanie, czy ekrany zostały dodane do stosu
    mock_stack.addWidget.assert_any_call(screen.choices_screen)
    mock_stack.addWidget.assert_any_call(screen.choice_screen)


# Test dla metody load_choices
def test_load_choices(app, mock_stack, mock_db_controller):
    # Przygotowanie testowanego ekranu
    screen = VotingScreen(mock_stack, mock_db_controller)

    # Przykład danych zwracanych przez mocka
    mock_db_controller.get_all_mozliwe_wybory_by_glosowanie_id.return_value = [
        (1, "Wybór 1"),
        (2, "Wybór 2"),
        (3, "Wybór 3")
    ]

    # Ustawienie przykładowego ID głosowania
    screen.current_voting_id = 123

    # Wywołanie metody load_choices
    screen.load_choices()

    # Sprawdzanie, czy lista choices_list została prawidłowo załadowana
    assert screen.choices_list.count() == 3, "Liczba wyborów nie zgadza się z oczekiwaną."

    # Sprawdzanie, czy odpowiednie elementy zostały dodane do listy
    assert screen.choices_list.item(0).text() == "1: Wybór 1", "Pierwszy wybór nie został poprawnie dodany."
    assert screen.choices_list.item(1).text() == "2: Wybór 2", "Drugi wybór nie został poprawnie dodany."
    assert screen.choices_list.item(2).text() == "3: Wybór 3", "Trzeci wybór nie został poprawnie dodany."

    # Sprawdzanie, czy metoda get_all_mozliwe_wybory_by_glosowanie_id została wywołana z odpowiednim ID
    mock_db_controller.get_all_mozliwe_wybory_by_glosowanie_id.assert_called_with(123)


def test_add_choice(app, mock_stack, mock_db_controller):
    screen = VotingScreen(mock_stack, mock_db_controller)

    # Zmiana zachowania QInputDialog
    QInputDialog.getText = MagicMock(return_value=("Nowy wybór", True))

    # Ustawienie przykładowego ID głosowania
    screen.current_voting_id = 123

    # Wywołanie metody add_choice
    screen.add_choice()

    # Sprawdzenie, czy insert_mozliwy_wybor został wywołany z odpowiednimi danymi
    mock_db_controller.insert_mozliwy_wybor.assert_called_with("Nowy wybór", 123)


def test_edit_choice(app, mock_stack, mock_db_controller):
    screen = VotingScreen(mock_stack, mock_db_controller)

    # Zmiana zachowania QInputDialog
    QInputDialog.getText = MagicMock(return_value=("Zmieniony wybór", True))

    # Ustawienie przykładowych danych
    screen.current_choice_id = 1
    screen.current_voting_id = 123

    # Wywołanie metody edit_choice
    screen.edit_choice()

    # Sprawdzenie, czy update_mozliwy_wybor został wywołany z odpowiednimi danymi
    mock_db_controller.update_mozliwy_wybor.assert_called_with(1, 123, "Zmieniony wybór")

    # Sprawdzenie, czy lista wyborów została załadowana po edytowaniu
    screen.load_choices()
    assert screen.choices_list.count() == 2  # Po edytowaniu mamy 2 wybory


def test_delete_choice(app, mock_stack, mock_db_controller):
    screen = VotingScreen(mock_stack, mock_db_controller)

    # Przygotowanie danych do testu
    mock_db_controller.get_count_mozliwe_wybory = MagicMock(return_value=3)

    # Zmiana zachowania QMessageBox
    QMessageBox.question = MagicMock(return_value=QMessageBox.Yes)

    # Ustawienie przykładowych danych
    screen.current_choice_id = 1
    screen.current_voting_id = 123

    # Wywołanie metody delete_choice
    screen.delete_choice()

    # Sprawdzenie, czy delete_mozliwy_wybor został wywołany z odpowiednimi danymi
    mock_db_controller.delete_mozliwy_wybor.assert_called_with(1, 123)

    # Sprawdzenie, czy lista wyborów została załadowana po usunięciu wyboru
    screen.load_choices()
    assert screen.choices_list.count() == 2  # Po usunięciu mamy 2 wybory

    # Test dla sytuacji, gdy liczba wyborów jest mniejsza lub równa 2
    mock_db_controller.get_count_mozliwe_wybory = MagicMock(return_value=2)
    QMessageBox.warning = MagicMock()

    screen.delete_choice()

    # Sprawdzenie, czy pokazano komunikat ostrzegawczy
    QMessageBox.warning.assert_called_once()
