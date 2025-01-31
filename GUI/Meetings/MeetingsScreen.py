import re

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem,
                               QMessageBox, QDialog, QLineEdit)
from PySide6.QtCore import Qt
from ..Voting.VotingScreen import VotingScreen


class MeetingsScreen:
    def __init__(self, stack, db_controller):
        self.title_label = None
        self.add_meeting_button = None
        self.delete_meeting_button = None
        self.edit_meeting_button = None
        self.back_to_main_button = None
        self.meeting_list = None
        self.meeting_screen = None
        self.voting_screen = VotingScreen(stack, db_controller)  # Instancja ekranu głosowań
        self.stack = stack
        self.db_controller = db_controller
        self.init_ui()

    def init_ui(self):
        self.create_meeting_screen()
        self.stack.addWidget(self.voting_screen.voting_screen)

    def create_meeting_screen(self):
        self.meeting_screen = QWidget()
        layout = QVBoxLayout()

        self.title_label = QLabel("<h1>Lista Spotkań</h1>")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.meeting_list = QListWidget()
        self.meeting_list.itemClicked.connect(self.open_votings_screen)
        layout.addWidget(self.meeting_list)

        buttons_layout = QHBoxLayout()

        self.add_meeting_button = QPushButton("Dodaj spotkanie")
        self.add_meeting_button.clicked.connect(self.add_meeting)
        buttons_layout.addWidget(self.add_meeting_button)

        self.delete_meeting_button = QPushButton("Usuń spotkanie")
        self.delete_meeting_button.clicked.connect(self.delete_meeting)
        buttons_layout.addWidget(self.delete_meeting_button)

        self.edit_meeting_button = QPushButton("Edytuj spotkanie")
        self.edit_meeting_button.clicked.connect(self.edit_meeting)
        buttons_layout.addWidget(self.edit_meeting_button)

        self.back_to_main_button = QPushButton("Powrót")
        self.back_to_main_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(0)))
        buttons_layout.addWidget(self.back_to_main_button)

        layout.addLayout(buttons_layout)

        self.meeting_screen.setLayout(layout)
        self.stack.addWidget(self.meeting_screen)
        self.load_meetings()

    def load_meetings(self):
        self.meeting_list.clear()
        meetings = self.db_controller.get_all_meetings()
        for meeting in meetings:
            item = QListWidgetItem(f"{meeting[0]}: {meeting[1]}")
            item.setData(Qt.UserRole, meeting[0])
            self.meeting_list.addItem(item)

    def add_meeting(self):
        dialog = QDialog(self.meeting_screen)
        dialog.setWindowTitle("Dodaj spotkanie")
        dialog_layout = QVBoxLayout()

        fields = {}
        fields_data = ["Termin (YYYY-MM-DD HH:MM:SS)", "Czas Trwania (HH:MM:SS)", "Czy Zakończone"]

        for field in fields_data:
            field_layout = QHBoxLayout()
            label = QLabel(field + ":")
            field_input = QLineEdit()
            fields[field.split(" ")[0].lower()] = field_input

            field_layout.addWidget(label)
            field_layout.addWidget(field_input)
            dialog_layout.addLayout(field_layout)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Dodaj")
        save_button.clicked.connect(lambda: self.save_new_meeting(dialog, fields))
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)

        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)
        dialog.exec()

    def delete_meeting(self):
        selected_items = self.meeting_list.selectedItems()
        print("deleting...")
        if selected_items:
            selected_item = selected_items[0]
            meeting_id = selected_item.data(Qt.UserRole)
            print(f"meeting id {meeting_id}")

            dialog = QDialog(self.meeting_screen)
            dialog.setWindowTitle("Usuń spotkanie")
            dialog_layout = QVBoxLayout()

            buttons_layout = QHBoxLayout()
            save_button = QPushButton("Potwierdź")
            save_button.clicked.connect(lambda: self.delete_meeting_dialog(dialog, meeting_id))
            buttons_layout.addWidget(save_button)

            cancel_button = QPushButton("Anuluj")
            cancel_button.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_button)

            dialog_layout.addLayout(buttons_layout)
            dialog.setLayout(dialog_layout)
            dialog.exec()

        else:
            dialog = QDialog(self.meeting_screen)
            dialog.setWindowTitle("Błąd")
            dialog_layout = QVBoxLayout()
            dialog.setLayout(dialog_layout)
            dialog_layout.addWidget(QLabel("Nie znaleziono spotkania do usunięcia"))

            buttons_layout = QHBoxLayout()
            ok_button = QPushButton("ok")
            ok_button.clicked.connect(dialog.accept)
            buttons_layout.addWidget(ok_button)
            dialog_layout.addLayout(buttons_layout)

            dialog.exec()

    def delete_meeting_dialog(self, dialog, meeting_id):
        self.db_controller.delete_meeting(meeting_id)

        self.load_meetings()

        dialog.accept()

    def edit_meeting(self):
        selected_items = self.meeting_list.selectedItems()
        print("editing...")
        if selected_items:
            selected_item = selected_items[0]
            meeting_id = selected_item.data(Qt.UserRole)
            print(f"meeting id {meeting_id}")

            dialog = QDialog(self.meeting_screen)
            dialog.setWindowTitle("Edytuj Spotkanie")
            dialog_layout = QVBoxLayout()

            fields = {}
            fields_data = ["Termin (YYYY-MM-DD HH:MM:SS)", "Czas Trwania (HH:MM:SS)", "Czy Zakończone"]

            for field in fields_data:
                field_layout = QHBoxLayout()
                label = QLabel(field + ":")
                field_input = QLineEdit()
                fields[field.split(" ")[0].lower()] = field_input

                field_layout.addWidget(label)
                field_layout.addWidget(field_input)
                dialog_layout.addLayout(field_layout)

            buttons_layout = QHBoxLayout()
            save_button = QPushButton("Potwierdź")
            save_button.clicked.connect(lambda: self.edit_meeting_dialog(dialog, meeting_id, fields))
            buttons_layout.addWidget(save_button)

            cancel_button = QPushButton("Anuluj")
            cancel_button.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_button)

            dialog_layout.addLayout(buttons_layout)
            dialog.setLayout(dialog_layout)
            dialog.exec()

        else:
            dialog = QDialog(self.meeting_screen)
            dialog.setWindowTitle("Błąd")
            dialog_layout = QVBoxLayout()
            dialog_layout.addWidget(QLabel("Nie znaleziono spotkania do edycji"))

            buttons_layout = QHBoxLayout()
            ok_button = QPushButton("ok")
            ok_button.clicked.connect(dialog.accept)
            buttons_layout.addWidget(ok_button)
            dialog_layout.addLayout(buttons_layout)

    def edit_meeting_dialog(self, dialog, meeting_id, fields):
        termin = fields["termin"].text()
        czas_trwania = fields["czas"].text()
        czy_zakonczone = fields["czy"].text().lower() in ("true", "1", "tak")

        datetime_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        time_pattern = r"\d{2}:\d{2}:\d{2}"

        if (
                re.fullmatch(datetime_pattern, termin)
                and re.fullmatch(time_pattern, czas_trwania)
        ):

            self.db_controller.update_meeting(meeting_id=meeting_id, termin=termin, czas_trwania=czas_trwania,
                                              czy_zakonczone=czy_zakonczone)
            self.load_meetings()
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "Błąd", "Niepoprawne dane!", QMessageBox.Ok)

    def save_new_meeting(self, dialog, fields):
        termin = fields["termin"].text()
        czas_trwania = fields["czas"].text()
        czy_zakonczone = fields["czy"].text().lower() in ("true", "1", "tak")

        datetime_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        time_pattern = r"\d{2}:\d{2}:\d{2}"

        if (
                re.fullmatch(datetime_pattern, termin)
                and re.fullmatch(time_pattern, czas_trwania)
        ):

            self.db_controller.insert_meeting(termin, czas_trwania, czy_zakonczone, 1)
            self.load_meetings()
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "Błąd", "Niepoprawne dane!", QMessageBox.Ok)

    def open_votings_screen(self, item):
        meeting_id = item.data(Qt.UserRole)
        self.voting_screen.set_current_meeting_id(meeting_id)
        self.voting_screen.load_votings()
        self.stack.setCurrentWidget(self.voting_screen.voting_screen)
