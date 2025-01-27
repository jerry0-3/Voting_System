import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox,
                               QInputDialog, QDialog, QLineEdit)
from PySide6.QtCore import Qt


class MeetingsScreen:
    def __init__(self, stack, db_controller):
        self.title_label = None
        self.add_meeting_button = None
        self.back_to_main_button = None
        self.meeting_list = None
        self.meeting_screen = None
        self.stack = stack
        self.db_controller = db_controller
        self.init_ui()

    def init_ui(self):
        self.create_meeting_screen()

    def create_meeting_screen(self):
        self.meeting_screen = QWidget()
        layout = QVBoxLayout()

        self.title_label = QLabel("<h1>Spotkania</h1>")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.meeting_list = QListWidget()
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
            self.meeting_list.addItem(f"{meeting[0]}: {meeting[1]}")

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
            # tutaj musisz jakos zrobic connecta z baza Mati :))))))
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)

        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)
        dialog.exec()
