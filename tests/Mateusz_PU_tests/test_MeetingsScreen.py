import pytest
from PySide6.QtWidgets import QApplication, QStackedWidget, QDialog, QLineEdit, QPushButton, QListWidgetItem
from PySide6.QtCore import Qt
from unittest.mock import MagicMock

from GUI.Meetings.MeetingsScreen import MeetingsScreen


@pytest.fixture
def app(qtbot):
    """Ensure QApplication is created once per test session."""
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def stack():
    """Fixture to create a QStackedWidget."""
    return QStackedWidget()


@pytest.fixture
def db_controller():
    """Mocked database controller."""
    mock_db = MagicMock()
    mock_db.get_all_meetings.return_value = [(6, '2025-01-30 15:00:00')]
    return mock_db


@pytest.fixture
def meetings_screen(stack, db_controller, qtbot):
    """Fixture to create MeetingsScreen instance."""
    screen = MeetingsScreen(stack, db_controller)
    qtbot.addWidget(screen.meeting_screen)
    return screen


def test_init_ui(app, meetings_screen):
    """Test UI initialization."""

    # Check if the meeting screen is created
    assert meetings_screen.meeting_screen is not None, "Meeting screen was not initialized."

    # Verify that the title label has the correct text
    assert meetings_screen.title_label.text() == "<h1>Lista Spotkań</h1>", "Title label text is incorrect."

    # Ensure that the meeting list is populated with data from the mock database
    assert meetings_screen.meeting_list.count() == 1, "Meeting list does not contain the expected number of items."


def test_load_meetings(app, meetings_screen):
    """Test loading meetings from the database."""
    meetings_screen.load_meetings()
    assert meetings_screen.meeting_list.count() == 1
    assert meetings_screen.meeting_list.item(0).text() == '6: 2025-01-30 15:00:00'


def test_add_meeting(app, meetings_screen, qtbot):
    """Test adding a new meeting."""
    meetings_screen.db_controller.insert_meeting = MagicMock()
    qtbot.mouseClick(meetings_screen.add_meeting_button, Qt.MouseButton.LeftButton)

    dialog = None
    for widget in app.allWidgets():
        if isinstance(widget, QDialog) and widget.windowTitle() == "Dodaj spotkanie":
            dialog = widget
            break

    assert dialog is not None, "Dialog for adding a meeting did not appear!"

    termin_input = dialog.findChild(QLineEdit, None)
    czas_trwania_input = dialog.findChildren(QLineEdit, None)[1]
    czy_zakonczone_input = dialog.findChildren(QLineEdit, None)[2]

    assert termin_input and czas_trwania_input and czy_zakonczone_input

    qtbot.keyClicks(termin_input, "2025-01-30 12:00:00")
    qtbot.keyClicks(czas_trwania_input, "01:30:00")
    qtbot.keyClicks(czy_zakonczone_input, "tak")

    add_button = dialog.findChild(QPushButton, None)
    assert add_button is not None, "Failed to find 'Dodaj' button!"
    qtbot.mouseClick(add_button, Qt.LeftButton)

    meetings_screen.db_controller.insert_meeting.assert_called_once_with(
        "2025-01-30 12:00:00", "01:30:00", True, 1
    )


def test_delete_meeting(app, meetings_screen, qtbot):
    """Test deleting a meeting."""

    meetings_screen.db_controller.delete_meeting = MagicMock()

    test_meeting = QListWidgetItem("1: 2025-01-30 15:00:00")
    test_meeting.setData(Qt.UserRole, 1)  # Meeting ID = 1
    meetings_screen.meeting_list.addItem(test_meeting)
    meetings_screen.meeting_list.setCurrentItem(test_meeting)
    qtbot.mouseClick(meetings_screen.delete_meeting_button, Qt.MouseButton.LeftButton)

    dialog = None
    for widget in app.allWidgets():
        if isinstance(widget, QDialog) and widget.windowTitle() == "Usuń spotkanie":
            dialog = widget
            break

    assert dialog is not None, "Delete confirmation dialog did not appear!"

    confirm_button = None
    for button in dialog.findChildren(QPushButton):
        if button.text() == "Potwierdź":
            confirm_button = button
            break

    assert confirm_button is not None, "Failed to find 'Potwierdź' button!"
    qtbot.mouseClick(confirm_button, Qt.MouseButton.LeftButton)

    meetings_screen.db_controller.delete_meeting.assert_called_once_with(1)


def test_edit_meeting(app, meetings_screen, qtbot):
    """Test editing a meeting."""
    meetings_screen.db_controller.update_meeting = MagicMock()

    # Add a test meeting item to the list
    test_meeting = QListWidgetItem("1: 2025-01-30 15:00:00")
    test_meeting.setData(Qt.UserRole, 1)  # Meeting ID = 1
    meetings_screen.meeting_list.addItem(test_meeting)
    meetings_screen.meeting_list.setCurrentItem(test_meeting)

    qtbot.mouseClick(meetings_screen.edit_meeting_button, Qt.MouseButton.LeftButton)

    dialog = None
    for widget in app.allWidgets():
        if isinstance(widget, QDialog) and widget.windowTitle() == "Edytuj Spotkanie":
            dialog = widget
            break

    assert dialog is not None, "Edit meeting dialog did not appear!"

    termin_input = dialog.findChild(QLineEdit, None)
    czas_trwania_input = dialog.findChildren(QLineEdit, None)[1]  # Second QLineEdit
    czy_zakonczone_input = dialog.findChildren(QLineEdit, None)[2]

    assert termin_input and czas_trwania_input and czy_zakonczone_input

    qtbot.keyClicks(termin_input, "2024-06-30 14:00:00")
    qtbot.keyClicks(czas_trwania_input, "02:30:00")
    qtbot.keyClicks(czy_zakonczone_input, "tak")

    confirm_button = None
    for button in dialog.findChildren(QPushButton):
        if button.text() == "Potwierdź":
            confirm_button = button
            break

    assert confirm_button is not None, "Failed to find 'Potwierdź' button!"
    qtbot.mouseClick(confirm_button, Qt.MouseButton.LeftButton)

    meetings_screen.db_controller.update_meeting.assert_called_once_with(
        meeting_id=1,
        termin="2024-06-30 14:00:00",
        czas_trwania="02:30:00",
        czy_zakonczone=True
    )
