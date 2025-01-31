from PySide6.QtWidgets import QMessageBox


class ApproveVoting:
    def __init__(self, db_controller, stack):
        self.db_controller = db_controller
        self.stack = stack

    def check_voting_conditions(self, voting_id):
        """Sprawdza, czy głosowanie spełnia wymagania do zatwierdzenia."""
        choices_count = self.db_controller.get_count_mozliwe_wybory(voting_id)
        return choices_count >= 2

    def approve_voting(self, voting_id, choices_screen, voting_screen, load_votings_callback):
        """Zatwierdza głosowanie, jeśli spełnia odpowiednie kryteria."""
        if self.check_voting_conditions(voting_id):
            confirm = QMessageBox.question(
                choices_screen,
                "Zatwierdź głosowanie",
                "Czy na pewno chcesz zatwierdzić to głosowanie?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.db_controller.approve_glosowanie(voting_id)
                QMessageBox.information(choices_screen, "Sukces", "Głosowanie zostało zatwierdzone!", QMessageBox.Ok)
                self.stack.setCurrentWidget(voting_screen)
                load_votings_callback()
        else:
            QMessageBox.warning(
                choices_screen,
                "Błąd",
                "Nie można zatwierdzić głosowania! Sprawdź warunki.",
                QMessageBox.Ok
            )
