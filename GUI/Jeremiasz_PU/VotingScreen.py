from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox,
                               QInputDialog)
from PySide6.QtCore import Qt


class VotingScreen:
    def __init__(self, stack, db_controller):
        self.stack = stack
        self.db_controller = db_controller
        self.init_ui()

    def init_ui(self):
        """Tworzy potrzebne ekrany po naciśnięciu przycisku."""
        self.create_voting_screen()
        self.create_choices_screen()
        self.create_edit_choice_screen()
        self.create_shareholders_screen()

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

    def create_shareholders_screen(self):
        self.shareholders_screen = QWidget()
        layout = QVBoxLayout()

        shareholders_label = QLabel("Udziałowcy")
        layout.addWidget(shareholders_label)

        self.shareholders_list = QListWidget()
        layout.addWidget(self.shareholders_list)

        back_button = QPushButton("Powrót")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_screen))
        layout.addWidget(back_button)

        self.shareholders_screen.setLayout(layout)
        self.stack.addWidget(self.shareholders_screen)

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
        self.current_choice_text = self.choices_list.item(index.row()).text().split(":")[1]
        self.edit_choice_label.setText(f"Edycja Wyboru: {self.current_choice_text}")
        self.stack.setCurrentWidget(self.choice_screen)

    def add_voting(self):
        text, ok = QInputDialog.getText(self.voting_screen, "Dodaj głosowanie", "Wpisz temat głosowania:")
        if ok and text:
            self.db_controller.insert_glosowanie(0, text, '2025-01-30 15:00:00', '02:00:00', False)
            self.load_votings()

    def edit_voting(self):
        new_text, ok = QInputDialog.getText(self.choices_screen, "Edytuj głosowanie", "Podaj nowy temat:")
        if ok and new_text:
            self.db_controller.update_glosowanie(self.current_voting_id, temat=new_text)
            self.load_votings()

    def delete_voting(self):
        confirm = QMessageBox.question(self, "Usuń głosowanie", "Czy na pewno chcesz usunąć to głosowanie?",
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
        new_text, ok = QInputDialog.getText(self.choices_screen, "Edytuj wybór", "Podaj nową treść:")
        if ok and new_text:
            print(self.current_choice_id, self.current_voting_id, new_text)
            self.db_controller.update_mozliwy_wybor(self.current_choice_id, self.current_voting_id, new_text)
            self.load_choices()

    def delete_choice(self):
        confirm = QMessageBox.question(self, "Usuń wybór", "Czy na pewno chcesz usunąć ten wybór?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.db_controller.delete_mozliwy_wybor(self.current_choice_id, self.current_voting_id)
            self.load_choices()
            self.stack.setCurrentWidget(self.choices_screen)
