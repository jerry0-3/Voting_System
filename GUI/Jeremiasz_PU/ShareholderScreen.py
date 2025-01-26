from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox,
                               QLineEdit, QDialog)


class ShareholderScreen:
    def __init__(self, stack, db_controller):
        self.current_shareholder_id = None
        self.fields = None
        self.shareholder_label = None
        self.shareholder_screen = None
        self.shareholders_list = None
        self.shareholders_screen = None
        self.stack = stack
        self.db_controller = db_controller
        self.init_ui()

    def init_ui(self):
        """Tworzy potrzebne ekrany po naciśnięciu przycisku."""
        self.create_shareholders_screen()
        self.create_shareholder_screen()

    def create_shareholders_screen(self):
        self.shareholders_screen = QWidget()
        layout = QVBoxLayout()

        shareholders_label = QLabel("Udziałowcy")
        layout.addWidget(shareholders_label)

        self.shareholders_list = QListWidget()
        self.shareholders_list.itemClicked.connect(self.open_shareholder_screen)
        layout.addWidget(self.shareholders_list)

        buttons_layout = QHBoxLayout()

        add_shareholder_button = QPushButton("Dodaj udziałowca")
        add_shareholder_button.clicked.connect(self.add_shareholder)
        buttons_layout.addWidget(add_shareholder_button)

        back_button = QPushButton("Powrót")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(0)))
        buttons_layout.addWidget(back_button)

        layout.addLayout(buttons_layout)

        self.shareholders_screen.setLayout(layout)
        self.stack.addWidget(self.shareholders_screen)
        self.load_shareholders()

    def create_shareholder_screen(self):
        self.shareholder_screen = QWidget()
        layout = QVBoxLayout()

        self.shareholder_label = QLabel("Udziałowiec")
        layout.addWidget(self.shareholder_label)

        self.fields = {}  # Przechowuje pola tekstowe dla edycji
        fields_data = ["Login", "Hasło", "Imię", "Nazwisko", "Udziały"]

        for field in fields_data:
            field_layout = QHBoxLayout()
            label = QLabel(field + ":")
            field_input = QLineEdit()
            self.fields[field.lower()] = field_input

            field_layout.addWidget(label)
            field_layout.addWidget(field_input)
            layout.addLayout(field_layout)

        # Przyciski akcji
        buttons_layout = QHBoxLayout()

        save_button = QPushButton("Zapisz zmiany")
        save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_button)

        delete_button = QPushButton("Usuń udziałowca")
        delete_button.clicked.connect(self.delete_shareholder)
        buttons_layout.addWidget(delete_button)

        back_button = QPushButton("Powrót")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.shareholders_screen))
        buttons_layout.addWidget(back_button)

        layout.addLayout(buttons_layout)

        self.shareholder_screen.setLayout(layout)
        self.stack.addWidget(self.shareholder_screen)

    def load_shareholders(self):
        """Ładuje listę udziałowców."""
        self.shareholders_list.clear()
        shareholders = self.db_controller.get_all_udzialowcy()
        for shareholder in shareholders:
            self.shareholders_list.addItem(f"{shareholder[0]}: {shareholder[3]} {shareholder[4]}")

    def add_shareholder(self):
        dialog = QDialog(self.shareholders_screen)
        dialog.setWindowTitle("Dodaj udziałowca")
        dialog_layout = QVBoxLayout()

        fields = {}
        fields_data = ["Login", "Hasło", "Imię", "Nazwisko", "Udziały"]

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
        save_button.clicked.connect(lambda: self.save_new_shareholder(dialog, fields))
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)

        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)
        dialog.exec()

    def save_new_shareholder(self, dialog, fields):
        login = fields["login"].text()
        haslo = fields["hasło"].text()
        imie = fields["imię"].text()
        nazwisko = fields["nazwisko"].text()
        udzialy = fields["udziały"].text()

        if login and haslo and imie and nazwisko and udzialy.isdigit():
            self.db_controller.insert_udzialowiec(login, haslo, imie, nazwisko, int(udzialy))
            self.load_shareholders()
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "Błąd", "Wszystkie pola muszą być wypełnione poprawnie!", QMessageBox.Ok)

    def open_shareholder_screen(self, item):
        """Otwiera ekran szczegółów udziałowca."""
        self.current_shareholder_id = int(item.text().split(":")[0])
        self.shareholder_label.setText(f"Udziałowiec: {item.text().split(':')[1]}")
        self.load_shareholder()
        self.stack.setCurrentWidget(self.shareholder_screen)

    def load_shareholder(self):
        """Wczytuje dane udziałowca i wypełnia pola tekstowe."""
        shareholder = self.db_controller.get_udzialowiec_by_id(self.current_shareholder_id)
        udzialy = self.db_controller.get_waga_glosu_by_id(shareholder[5])[1]
        if shareholder:
            self.fields["login"].setText(shareholder[1])
            self.fields["hasło"].setText(shareholder[2])
            self.fields["imię"].setText(shareholder[3])
            self.fields["nazwisko"].setText(shareholder[4])
            self.fields["udziały"].setText(str(udzialy))

    def save_changes(self):
        """Zapisuje zmiany udziałowca."""
        confirm = QMessageBox.question(
            self.shareholder_screen, "Potwierdzenie", "Czy na pewno zapisać zmiany?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            login = self.fields["login"].text()
            haslo = self.fields["hasło"].text()
            imie = self.fields["imię"].text()
            nazwisko = self.fields["nazwisko"].text()
            udzialy = self.fields["udziały"].text()

            self.db_controller.update_udzialowiec(
                self.current_shareholder_id,
                login=login,
                haslo=haslo,
                imie=imie,
                nazwisko=nazwisko,
                udzialy=int(udzialy) if udzialy.isdigit() else None
            )
            self.load_shareholders()
            self.stack.setCurrentWidget(self.shareholders_screen)

    def delete_shareholder(self):
        """Usuwa udziałowca."""
        confirm = QMessageBox.question(
            self.shareholder_screen, "Potwierdzenie", "Czy na pewno usunąć udziałowca?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.db_controller.delete_udzialowiec(self.current_shareholder_id)
            self.load_shareholders()
            self.stack.setCurrentWidget(self.shareholders_screen)
