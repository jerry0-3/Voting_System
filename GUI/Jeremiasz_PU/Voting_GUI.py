from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                               QListWidget, QStackedWidget, QMessageBox, QInputDialog, QListWidgetItem)
from PySide6.QtCore import Qt


class VotingSystemGUI(QMainWindow):
    def __init__(self, db_controller):
        super().__init__()
        self.db_controller = db_controller

        self.setWindowTitle("System Głosowania")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.create_home_screen()
        self.create_voting_screen()
        self.create_choices_screen()
        self.create_shareholders_screen()

        self.stack.setCurrentWidget(self.home_screen)

    def create_home_screen(self):
        self.home_screen = QWidget()
        layout = QVBoxLayout()

        self.voting_button = QPushButton("Przejdź do głosowań")
        self.voting_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.voting_screen))
        self.shareholders_button = QPushButton("Przejdź do udziałowców")
        self.shareholders_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.shareholders_screen))

        layout.addStretch()
        layout.addWidget(self.voting_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.shareholders_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.home_screen.setLayout(layout)
        self.stack.addWidget(self.home_screen)

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
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_screen))
        buttons_layout.addWidget(back_button)

        layout.addLayout(buttons_layout)

        self.voting_screen.setLayout(layout)
        self.stack.addWidget(self.voting_screen)
        self.load_votings()

    def create_choices_screen(self):
        self.choices_screen = QWidget()
        layout = QVBoxLayout()

        self.choices_label = QLabel("Wybory w głosowaniu")
        layout.addWidget(self.choices_label)

        self.choices_list = QListWidget()
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
        self.voting_id = int(item.text().split(":")[0])
        self.choices_label.setText(f"Wybory w głosowaniu: {item.text().split(':')[1]}")
        self.load_choices()
        self.stack.setCurrentWidget(self.choices_screen)

    def load_choices(self):
        self.choices_list.clear()
        choices = self.db_controller.get_all_mozliwe_wybory_by_glosowanie_id(self.voting_id)
        if choices is not None:
            for choice in choices:
                edit_button = QPushButton("Edytuj")
                delete_button = QPushButton("Usuń")

                list_item_widget = QWidget()
                item_layout = QHBoxLayout()
                item_layout.addWidget(QLabel(choice[1]))
                item_layout.addWidget(edit_button)
                item_layout.addWidget(delete_button)

                list_item_widget.setLayout(item_layout)

                list_item = QListWidgetItem(self.choices_list, 0)
                self.choices_list.addItem(list_item)
                self.choices_list.setItemWidget(list_item, list_item_widget)
        else:
            self.create_choices_screen()

    def add_voting(self):
        text, ok = QInputDialog.getText(self, "Dodaj głosowanie", "Wpisz temat głosowania:")
        if ok and text:
            self.db_controller.insert_glosowanie(0, text, '2025-01-30 15:00:00', '02:00:00', False)
            self.load_votings()

    def add_choice(self):
        text, ok = QInputDialog.getText(self, "Dodaj wybór", "Wpisz treść wyboru:")
        if ok and text:
            self.db_controller.insert_mozliwy_wybor(text, self.voting_id)
            self.load_choices()


def start_application(db_controller):
    app = QApplication([])

    gui = VotingSystemGUI(db_controller)
    gui.show()

    app.exec()
