import re

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox,
                               QInputDialog, QDialog, QLineEdit)
from PySide6.QtCore import Qt


class VotingScreen:
    def __init__(self, stack, db_controller):
        self.current_choice_id = None
        self.current_voting_id = None
        self.back_button = None
        self.delete_button = None
        self.edit_button = None
        self.edit_choice_label = None
        self.choice_screen = None
        self.back_to_voting_button = None
        self.add_choice_button = None
        self.choices_list = None
        self.choices_label = None
        self.delete_voting_button = None
        self.edit_voting_button = None
        self.choices_screen = None
        self.voting_list = None
        self.voting_screen = None
        self.stack = stack
        self.db_controller = db_controller
        self.init_ui()

    def init_ui(self):
        """Tworzy potrzebne ekrany po naciśnięciu przycisku."""
        self.create_voting_screen()
        self.create_choices_screen()
        self.create_edit_choice_screen()

    def create_voting_screen(self):
        self.voting_screen = QWidget()
        layout = QVBoxLayout()

        voting_label = QLabel("Głosowania")
        layout.addWidget(voting_label)

        self.voting_list = QListWidget()
        self.voting_list.itemClicked.connect(self.open_choices_screen)
        layout.addWidget(self.voting_list)

        buttons_layout = QHBoxLayout()

        add_voting_button = QPushButton("Dodaj głosowanie")
        add_voting_button.clicked.connect(self.add_voting)
        buttons_layout.addWidget(add_voting_button)

        back_button = QPushButton("Powrót")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(0)))
        buttons_layout.addWidget(back_button)

        layout.addLayout(buttons_layout)

        self.voting_screen.setLayout(layout)
        self.stack.addWidget(self.voting_screen)
        self.load_votings()

    def create_choices_screen(self):
        self.choices_screen = QWidget()
        layout = QVBoxLayout()

        top_buttons_layout = QHBoxLayout()

        self.edit_voting_button = QPushButton("Edytuj głosowanie")
        self.edit_voting_button.clicked.connect(self.edit_voting)
        top_buttons_layout.addWidget(self.edit_voting_button)

        self.delete_voting_button = QPushButton("Usuń głosowanie")
        self.delete_voting_button.clicked.connect(self.delete_voting)
        top_buttons_layout.addWidget(self.delete_voting_button)

        layout.addLayout(top_buttons_layout)

        self.choices_label = QLabel("Wybory w głosowaniu")
        layout.addWidget(self.choices_label)

        self.choices_list = QListWidget()
        self.choices_list.clicked.connect(self.edit_choice_screen)
        layout.addWidget(self.choices_list)

        buttons_layout = QHBoxLayout()
        self.add_choice_button = QPushButton("Dodaj wybór")
        self.add_choice_button.clicked.connect(self.add_choice)
        buttons_layout.addWidget(self.add_choice_button)

        self.back_to_voting_button = QPushButton("Powrót do głosowań")
        self.back_to_voting_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.voting_screen))
        buttons_layout.addWidget(self.back_to_voting_button)

        layout.addLayout(buttons_layout)
        self.choices_screen.setLayout(layout)
        self.stack.addWidget(self.choices_screen)

    def create_edit_choice_screen(self):
        self.choice_screen = QWidget()
        layout = QVBoxLayout()

        self.edit_choice_label = QLabel(f"Edycja Wyboru")
        layout.addWidget(self.edit_choice_label, alignment=Qt.AlignCenter)

        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)

        self.edit_button = QPushButton("Edytuj treść")
        self.edit_button.clicked.connect(self.edit_choice)
        buttons_layout.addWidget(self.edit_button, alignment=Qt.AlignCenter)

        self.delete_button = QPushButton("Usuń wybór")
        self.delete_button.clicked.connect(self.delete_choice)
        buttons_layout.addWidget(self.delete_button, alignment=Qt.AlignCenter)

        self.back_button = QPushButton("Powrót")
        self.back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.choices_screen))
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        layout.addLayout(buttons_layout)
        self.choice_screen.setLayout(layout)
        self.stack.addWidget(self.choice_screen)

    def load_votings(self):
        self.voting_list.clear()
        votings = self.db_controller.get_all_glosowania()
        for voting in votings:
            self.voting_list.addItem(f"{voting[0]}: {voting[2]}")

    def open_choices_screen(self, item):
        self.current_voting_id = int(item.text().split(":")[0])
        self.choices_label.setText(f"Wybory w głosowaniu: {item.text().split(':')[1]}")
        self.load_choices()
        self.stack.setCurrentWidget(self.choices_screen)

    def load_choices(self):
        self.choices_list.clear()
        choices = self.db_controller.get_all_mozliwe_wybory_by_glosowanie_id(self.current_voting_id)
        if choices is not None:
            for choice in choices:
                self.choices_list.addItem(f"{choice[0]}: {choice[1]}")

    def edit_choice_screen(self, index):
        self.current_choice_id = int(self.choices_list.item(index.row()).text().split(":")[0])
        current_choice_text = self.choices_list.item(index.row()).text().split(":")[1]
        self.edit_choice_label.setText(f"Edycja Wyboru: {current_choice_text}")
        self.stack.setCurrentWidget(self.choice_screen)

    def add_voting(self):
        dialog = QDialog(self.voting_screen)
        dialog.setWindowTitle("Dodaj głosowanie")
        dialog_layout = QVBoxLayout()

        fields = {}
        fields_data = ["Minimalne Udziały", "Temat", "Termin (YYYY-MM-DD HH:MM:SS)", "Czas Trwania (HH:MM:SS)",
                       "Czy Zakończone"]

        for field in fields_data:
            field_layout = QHBoxLayout()
            label = QLabel(field + ":")
            field_input = QLineEdit()
            fields[field.lower()] = field_input

            field_layout.addWidget(label)
            field_layout.addWidget(field_input)
            dialog_layout.addLayout(field_layout)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Dodaj")
        save_button.clicked.connect(lambda: self.save_new_voting(dialog, fields))
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)

        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)
        dialog.exec()

    def save_new_voting(self, dialog, fields):
        minimalne_udzialy = fields["minimalne udziały"].text()
        temat = fields["temat"].text()
        termin = fields["termin (yyyy-mm-dd hh:mm:ss)"].text()
        czas_trwania = fields["czas trwania (hh:mm:ss)"].text()
        czy_zakonczone = fields["czy zakończone"].text().lower() in ("true", "1", "tak")

        datetime_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        time_pattern = r"\d{2}:\d{2}:\d{2}"

        if (
                minimalne_udzialy.isdigit()
                and temat
                and self.validate_datetime(termin, datetime_pattern)
                and self.validate_datetime(czas_trwania, time_pattern)
        ):
            self.db_controller.insert_glosowanie(
                int(minimalne_udzialy), temat, termin, czas_trwania, czy_zakonczone
            )
            self.load_votings()
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "Błąd", "Wszystkie pola muszą być wypełnione poprawnie!", QMessageBox.Ok)

    def edit_voting(self):
        dialog = QDialog(self.voting_screen)
        dialog.setWindowTitle("Edytuj głosowanie")
        dialog_layout = QVBoxLayout()

        fields = {}
        fields_data = ["Minimalne Udziały", "Temat", "Termin (YYYY-MM-DD HH:MM:SS)", "Czas Trwania (HH:MM:SS)",
                       "Czy Zakończone"]

        for field in fields_data:
            field_layout = QHBoxLayout()
            label = QLabel(field + ":")
            field_input = QLineEdit()
            fields[field.lower()] = field_input

            field_layout.addWidget(label)
            field_layout.addWidget(field_input)
            dialog_layout.addLayout(field_layout)

        # Wypełnianie aktualnymi danymi głosowania
        voting = self.db_controller.get_glosowanie_by_id(self.current_voting_id)
        if voting:
            fields["minimalne udziały"].setText(str(voting[1]))
            fields["temat"].setText(voting[2])
            fields["termin (yyyy-mm-dd hh:mm:ss)"].setText(voting[3])
            fields["czas trwania (hh:mm:ss)"].setText(voting[4])
            fields["czy zakończone"].setText("Tak" if voting[5] else "Nie")

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Zapisz")
        save_button.clicked.connect(lambda: self.save_edited_voting(dialog, fields))
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)

        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)
        dialog.exec()

    def save_edited_voting(self, dialog, fields):
        minimalne_udzialy = fields["minimalne udziały"].text()
        temat = fields["temat"].text()
        termin = fields["termin (yyyy-mm-dd hh:mm:ss)"].text()
        czas_trwania = fields["czas trwania (hh:mm:ss)"].text()
        czy_zakonczone = fields["czy zakończone"].text().lower() in ("true", "1", "tak")

        datetime_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        time_pattern = r"\d{2}:\d{2}:\d{2}"

        if (
                minimalne_udzialy.isdigit()
                and temat
                and self.validate_datetime(termin, datetime_pattern)
                and self.validate_datetime(czas_trwania, time_pattern)
        ):
            self.db_controller.update_glosowanie(
                self.current_voting_id,
                minimalne_udzialy=int(minimalne_udzialy),
                temat=temat,
                termin=termin,
                czas_trwania=czas_trwania,
                czy_zakonczone=czy_zakonczone
            )
            self.load_votings()
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "Błąd", "Wszystkie pola muszą być wypełnione poprawnie!", QMessageBox.Ok)

    def delete_voting(self):
        confirm = QMessageBox.question(self.choices_screen, "Usuń głosowanie",
                                       "Czy na pewno chcesz usunąć to głosowanie?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.db_controller.delete_glosowanie(self.current_voting_id)
            self.stack.setCurrentWidget(self.voting_screen)
            self.load_votings()

    def add_choice(self):
        text, ok = QInputDialog.getText(self.choices_screen, "Dodaj wybór", "Wpisz treść wyboru:")
        if ok and text:
            self.db_controller.insert_mozliwy_wybor(text, self.current_voting_id)
            self.load_choices()

    def edit_choice(self):
        new_text, ok = QInputDialog.getText(self.choice_screen, "Edytuj wybór", "Podaj nową treść:")
        if ok and new_text:
            print(self.current_choice_id, self.current_voting_id, new_text)
            self.db_controller.update_mozliwy_wybor(self.current_choice_id, self.current_voting_id, new_text)
            self.load_choices()

    def delete_choice(self):
        count_mozliwe_wybory = self.db_controller.get_count_mozliwe_wybory(self.current_voting_id)
        if count_mozliwe_wybory > 2:
            confirm = QMessageBox.question(self.choice_screen, "Usuń wybór", "Czy na pewno chcesz usunąć ten wybór?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.db_controller.delete_mozliwy_wybor(self.current_choice_id, self.current_voting_id)
                self.load_choices()
                self.stack.setCurrentWidget(self.choices_screen)
        else:
            QMessageBox.warning(self.choice_screen, "Błąd", "Nie można usunąć wyboru!", QMessageBox.Ok)

    @staticmethod
    def validate_datetime(value, pattern):
        """Sprawdza, czy wartość daty/czasu pasuje do wzorca."""
        return re.fullmatch(pattern, value) is not None
