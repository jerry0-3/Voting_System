import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from GUI.Shareholders.ShareholderScreen import ShareholderScreen


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
    db_controller.get_all_udzialowcy = Mock(return_value=[
        (1, "login1", "pass1", "Jan", "Kowalski", 10),
        (2, "login2", "pass2", "Anna", "Nowak", 20),
    ])
    db_controller.get_udzialowiec_by_id = Mock(return_value=(1, "login1", "pass1", "Jan", "Kowalski", 10))
    db_controller.get_waga_glosu_by_id = Mock(return_value=(10, 15))
    db_controller.insert_udzialowiec = Mock()
    db_controller.update_udzialowiec = Mock()
    db_controller.delete_udzialowiec = Mock()
    return db_controller


def test_init_ui(app, mock_stack, mock_db_controller):
    # Tworzenie obiektu ShareholderScreen
    screen = ShareholderScreen(mock_stack, mock_db_controller)

    # Testy inicjalizacji
    assert screen.shareholders_screen is not None, "Ekran 'shareholders_screen' nie został poprawnie zainicjalizowany."
    assert screen.shareholder_screen is not None, "Ekran 'shareholder_screen' nie został poprawnie zainicjalizowany."

    # Sprawdzanie, czy ekrany zostały dodane do stosu
    mock_stack.addWidget.assert_any_call(screen.shareholders_screen)
    mock_stack.addWidget.assert_any_call(screen.shareholder_screen)


def test_load_shareholders(app, mock_stack, mock_db_controller):
    # Tworzenie obiektu ShareholderScreen
    screen = ShareholderScreen(mock_stack, mock_db_controller)

    # Wywołanie metody
    screen.load_shareholders()

    # Sprawdzanie, czy lista udziałowców została wypełniona poprawnymi danymi
    assert screen.shareholders_list.count() == 2, "Lista udziałowców ma niepoprawną liczbę elementów."
    assert screen.shareholders_list.item(0).text() == "1: Jan Kowalski", "Pierwszy udziałowiec ma niepoprawne dane."
    assert screen.shareholders_list.item(1).text() == "2: Anna Nowak", "Drugi udziałowiec ma niepoprawne dane."


def test_add_shareholder(app, mock_stack, mock_db_controller):
    # Tworzenie obiektu ShareholderScreen
    screen = ShareholderScreen(mock_stack, mock_db_controller)

    # Symulowanie dodawania nowego udziałowca
    dialog_mock = Mock()
    dialog_mock.exec = Mock()
    fields_mock = {
        "login": Mock(text=Mock(return_value="new_login")),
        "hasło": Mock(text=Mock(return_value="new_password")),
        "imię": Mock(text=Mock(return_value="Piotr")),
        "nazwisko": Mock(text=Mock(return_value="Nowak")),
        "udziały": Mock(text=Mock(return_value="50"))
    }

    # Wywołanie metody zapisu nowego udziałowca
    screen.save_new_shareholder(dialog_mock, fields_mock)

    # Sprawdzanie, czy metoda w kontrolerze bazy danych została wywołana z poprawnymi argumentami
    mock_db_controller.insert_udzialowiec.assert_called_once_with(
        "new_login", "new_password", "Piotr", "Nowak", 50
    )


def test_delete_shareholder(app, mock_stack, mock_db_controller):
    # Tworzenie obiektu ShareholderScreen
    screen = ShareholderScreen(mock_stack, mock_db_controller)

    # Symulacja wybrania udziałowca
    screen.current_shareholder_id = 1  # Przypisanie ID udziałowca do usunięcia

    # Mockowanie QMessageBox z odpowiedzią 'Yes'
    QMessageBox.question = Mock(return_value=QMessageBox.Yes)

    # Wywołanie metody delete_shareholder
    screen.delete_shareholder()

    # Sprawdzenie, czy metoda kontrolera bazy danych została wywołana z poprawnym ID
    mock_db_controller.delete_udzialowiec.assert_called_once_with(1)

    # Sprawdzenie, czy metoda ładowania listy udziałowców została wywołana
    assert mock_db_controller.get_all_udzialowcy.called, "Metoda ładowania udziałowców nie została wywołana."

    # Sprawdzenie, czy nastąpiło przejście na ekran listy udziałowców
    mock_stack.setCurrentWidget.assert_called_once_with(screen.shareholders_screen)

