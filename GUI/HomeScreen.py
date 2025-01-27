from PySide6.QtWidgets import QVBoxLayout, QPushButton, QMainWindow, QApplication, QStackedWidget, QWidget, QLabel
from PySide6.QtCore import Qt

from Voting_System.GUI.Jeremiasz_PU.ShareholderScreen import ShareholderScreen
from Voting_System.GUI.Jeremiasz_PU.VotingScreen import VotingScreen

from Voting_System.GUI.Piotr_PU.MeetingsScreen import MeetingsScreen


class HomeScreen(QMainWindow):
    def __init__(self, db_controller):
        super().__init__()
        self.shareholders_button = None
        self.voting_button = None
        self.layout = None
        self.home_screen = QWidget()
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

        title_label = QLabel("<h1>System Głosowania</h1>")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        self.voting_button = QPushButton("Przejdź do głosowań")
        self.voting_button.clicked.connect(lambda: print("placeholder function"))

        self.shareholders_button = QPushButton("Przejdź do udziałowców")
        self.shareholders_button.clicked.connect(lambda: print("placeholder function"))

        self.meetings_button = QPushButton("Przejdź do spotkań")
        self.meetings_button.clicked.connect(lambda: print("placeholder function"))

        self.layout.addStretch()
        self.layout.addWidget(self.voting_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.shareholders_button, alignment=Qt.AlignCenter)
        self.layout.addStretch()

        self.home_screen.setLayout(self.layout)
        self.stack.addWidget(self.home_screen)


def start_application(db_controller):
    app = QApplication([])

    home_screen = HomeScreen(db_controller)

    # Rejestracja dodatkowych ekranów
    voting_screen = VotingScreen(home_screen.stack, db_controller)
    shareholder_screen = ShareholderScreen(home_screen.stack, db_controller)
    meetings_screen = MeetingsScreen(home_screen.stack, db_controller)

    # Przypisanie akcji do przycisku w HomeScreen
    home_screen.voting_button.clicked.connect(
        lambda: home_screen.stack.setCurrentWidget(voting_screen.voting_screen)
    )
    home_screen.shareholders_button.clicked.connect(
        lambda: home_screen.stack.setCurrentWidget(shareholder_screen.shareholders_screen)
    )
    home_screen.meetings_button.clicked.connect(
        lambda: home_screen.stack.setCurrentWidget(shareholder_screen.shareholders_screen)
    )
    home_screen.show()
    app.exec()
