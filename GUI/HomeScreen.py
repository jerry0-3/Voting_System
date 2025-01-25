from PySide6.QtWidgets import QVBoxLayout, QPushButton, QMainWindow, QApplication, QStackedWidget, QWidget
from PySide6.QtCore import Qt

from GUI.Jeremiasz_PU.VotingScreen import VotingScreen


class HomeScreen(QMainWindow):
    def __init__(self, db_controller):
        super().__init__()
        self.setWindowTitle("System Głosowania")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.db_controller = db_controller

        self.init_ui()
        self.stack.setCurrentWidget(self.home_screen)

    def init_ui(self):
        """Inicjalizuje podstawowy ekran główny."""
        self.home_screen = QWidget()
        self.layout = QVBoxLayout()

        self.voting_button = QPushButton("Przejdź do głosowań")
        self.voting_button.clicked.connect(self.on_voting_clicked)

        self.shareholders_button = QPushButton("Przejdź do udziałowców")
        self.shareholders_button.clicked.connect(self.on_shareholders_clicked)

        self.layout.addStretch()
        self.layout.addWidget(self.voting_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.shareholders_button, alignment=Qt.AlignCenter)
        self.layout.addStretch()

        self.home_screen.setLayout(self.layout)
        self.stack.addWidget(self.home_screen)

    def add_custom_button(self, text, callback):
        """Dodaj dodatkowy przycisk do ekranu głównego."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        self.layout.insertWidget(self.layout.count() - 1, button, alignment=Qt.AlignCenter)

    def on_voting_clicked(self):
        """Metoda wywoływana po kliknięciu 'Przejdź do głosowań'."""
        print("Przejdź do głosowań.")

    def on_shareholders_clicked(self):
        """Metoda wywoływana po kliknięciu 'Przejdź do udziałowców'."""
        print("Przejdź do udziałowców.")


def start_application(db_controller):
    app = QApplication([])

    home_screen = HomeScreen(db_controller)

    # Rejestracja dodatkowych ekranów
    voting_screen = VotingScreen(home_screen.stack, db_controller)

    # Przypisanie akcji do przycisku w HomeScreen
    home_screen.voting_button.clicked.connect(
        lambda: home_screen.stack.setCurrentWidget(voting_screen.voting_screen)
    )

    home_screen.show()
    app.exec()
