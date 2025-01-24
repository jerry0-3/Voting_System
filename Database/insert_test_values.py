def insert_start_values(controller):
    insert_start_spotkania(controller)
    insert_start_administratorzy(controller)


def insert_start_spotkania(controller):
    if controller.execute_query("SELECT COUNT(*) FROM Spotkania", fetch_all=True)[0][0] == 0:
        controller.execute_query(
            "INSERT INTO Spotkania (termin, czas_trwania, czy_zakonczone, administrator) VALUES (?, ?, ?, ?)",
            params=('2025-01-30 15:00:00', '02:00:00', False, 1)
        )


def insert_start_administratorzy(controller):
    if controller.execute_query("SELECT COUNT(*) FROM Administratorzy", fetch_all=True)[0][0] == 0:
        controller.execute_query(
            "INSERT INTO Administratorzy DEFAULT VALUES"
        )
