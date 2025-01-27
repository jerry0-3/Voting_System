from typing import re

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem,
                               QMessageBox, QInputDialog, QDialog, QLineEdit)
from PySide6.QtCore import Qt
from ..Jeremiasz_PU.VotingScreen import VotingScreen



class MeetingsScreen:
    def __init__(self, stack, db_controller):
        self.title_label = None
        self.add_meeting_button = None
        self.back_to_main_button = None
        self.meeting_list = None
        self.meeting_screen = None
        self.voting_screen = VotingScreen(stack, db_controller)  # Instancja ekranu głosowań
        self.stack = stack
        self.db_controller = db_controller
        self.init_ui()

    def init_ui(self):
        self.create_meeting_screen()
        self.stack.addWidget(self.voting_screen.voting_screen)  # Dodanie ekranu głosowań do stosu

    def create_meeting_screen(self):
        self.meeting_screen = QWidget()
        layout = QVBoxLayout()

        self.title_label = QLabel("<h1>Spotkania</h1>")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.meeting_list = QListWidget()
        self.meeting_list.itemClicked.connect(self.open_votings_screen)
        layout.addWidget(self.meeting_list)

        buttons_layout = QHBoxLayout()

        self.add_meeting_button = QPushButton("Dodaj spotkanie")
        self.add_meeting_button.clicked.connect(self.add_meeting)
        buttons_layout.addWidget(self.add_meeting_button)

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
            self.db_controller.insert_meeting(termin, czas_trwania, czy_zakonczone)
            self.load_meetings()
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "Błąd", "Niepoprawne dane!", QMessageBox.Ok)

    def open_votings_screen(self, item):
        meeting_id = item.data(Qt.UserRole)
        self.voting_screen.set_current_meeting_id(meeting_id)
        self.voting_screen.load_votings()
        self.stack.setCurrentWidget(self.voting_screen.voting_screen)
