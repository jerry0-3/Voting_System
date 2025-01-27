import sqlite3


class DatabaseController:
    def __init__(self, db_name="Database\\voting_system.db"):
        self.db_name = db_name

    def execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
        """
        Executes a query with parameters and optional fetch results.
        """
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        try:
            cursor.execute(query, params)

            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None

            connection.commit()
            return result
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()

    # CRUD Operations

    # Insert record into Udzialowcy and Wagi_glosow
    def insert_udzialowiec(self, login, haslo, imie, nazwisko, udzialy):
        try:
            # Insert into Wagi_glosow
            waga_id = self.execute_query(
                "INSERT INTO Wagi_glosow (udzialy) VALUES (?) RETURNING id",
                (udzialy,),
                fetch_one=True
            )[0]

            # Insert into Udzialowcy
            self.execute_query(
                """
                INSERT INTO Udzialowcy (login, haslo, imie, nazwisko, waga_glosu)
                VALUES (?, ?, ?, ?, ?)
                """,
                (login, haslo, imie, nazwisko, waga_id)
            )
        except sqlite3.Error as e:
            print(f"An error occurred during insertion: {e}")

    def get_all_udzialowcy(self):
        query = "SELECT * FROM Udzialowcy"
        return self.execute_query(query, fetch_all=True)

    def get_udzialowiec_by_id(self, udzialowiec_id):
        query = "SELECT * FROM Udzialowcy WHERE id = ?"
        return self.execute_query(query, (udzialowiec_id,), fetch_one=True)

    def update_udzialowiec(self, udzialowiec_id, login=None, haslo=None, imie=None, nazwisko=None, udzialy=None):
        # Update udzialowiec
        query = """
        UPDATE Udzialowcy
        SET login = COALESCE(?, login),
            haslo = COALESCE(?, haslo),
            imie = COALESCE(?, imie),
            nazwisko = COALESCE(?, nazwisko)
        WHERE id = ?
        """
        self.execute_query(query, (login, haslo, imie, nazwisko, udzialowiec_id))

        # Update waga glosu
        waga_glosu_id = self.execute_query("SELECT waga_glosu FROM Udzialowcy WHERE id = ?", (udzialowiec_id,),
                                           fetch_one=True)[0]
        self.update_waga_glosu(waga_glosu_id, udzialy)

    def get_waga_glosu_by_id(self, waga_glosu_id):
        query = "SELECT * FROM Wagi_glosow WHERE id = ?"
        return self.execute_query(query, (waga_glosu_id,), fetch_one=True)

    def update_waga_glosu(self, waga_glosu_id, udzialy):
        query = """
                UPDATE Wagi_glosow
                SET udzialy = COALESCE(?, udzialy)
                WHERE id = ?
                """
        self.execute_query(query, (udzialy, waga_glosu_id))

    def delete_udzialowiec(self, udzialowiec_id):
        try:
            waga_id = self.execute_query(
                "SELECT waga_glosu FROM Udzialowcy WHERE id = ?",
                (udzialowiec_id,),
                fetch_one=True
            )

            self.execute_query("DELETE FROM Udzialowcy WHERE id = ?", (udzialowiec_id,))

            if waga_id:
                self.execute_query("DELETE FROM Wagi_glosow WHERE id = ?", (waga_id[0],))
        except sqlite3.Error as e:
            print(f"An error occurred during deletion: {e}")

    def insert_glosowanie(self, minimalne_udzialy, temat, termin, czas_trwania, czy_zakonczone, spotkanie,
                          wybor_1='wybor 1', wybor_2='wybor 2', administrator=1):
        try:
            if spotkanie is None: spotkanie = 1
            # Insert into Glosowania
            self.execute_query(
                """
                INSERT INTO Glosowania (minimalne_udzialy, temat, termin, czas_trwania, czy_zakonczone, spotkanie, 
                    administrator)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (minimalne_udzialy, temat, termin, czas_trwania, czy_zakonczone, spotkanie, administrator)
            )
            glosowanie_id = self.get_all_glosowania()[-1][0]

            self.insert_mozliwy_wybor(f'glosowanie {glosowanie_id} {wybor_1}', glosowanie_id)
            self.insert_mozliwy_wybor(f'glosowanie {glosowanie_id} {wybor_2}', glosowanie_id)

        except sqlite3.Error as e:
            print(f"An error occurred during insertion: {e}")

    def get_all_glosowania(self):
        query = "SELECT * FROM Glosowania"
        return self.execute_query(query, fetch_all=True)

    def get_glosowanie_by_id(self, glosowanie_id):
        query = "SELECT * FROM Glosowania WHERE id = ?"
        return self.execute_query(query, (glosowanie_id,), fetch_one=True)

    def get_glosowania_by_meeting_id(self, meeting_id):
        query = "SELECT * FROM Glosowania WHERE spotkanie = ?"
        return self.execute_query(query, (meeting_id,), fetch_all=True)

    def update_glosowanie(self, glosowanie_id, minimalne_udzialy=None, temat=None, termin=None, czas_trwania=None,
                          czy_zakonczone=None):
        query = """
                UPDATE Glosowania
                SET minimalne_udzialy = COALESCE(?, minimalne_udzialy),
                    temat = COALESCE(?, temat),
                    termin = COALESCE(?, termin),
                    czas_trwania = COALESCE(?, czas_trwania),
                    czy_zakonczone = COALESCE(?, czy_zakonczone)
                WHERE id = ?
                """
        self.execute_query(query, (minimalne_udzialy, temat, termin, czas_trwania, czy_zakonczone, glosowanie_id))

    def delete_glosowanie(self, glosowanie_id):
        try:
            self.execute_query("DELETE FROM Glosowania WHERE id = ?", (glosowanie_id,))
        except sqlite3.Error as e:
            print(f"An error occurred during deletion: {e}")

    def insert_mozliwy_wybor(self, tresc, glosowanie_id):
        try:
            # Insert into Glosowania
            self.execute_query(
                """
                INSERT INTO Mozliwe_wybory (tresc, glosowanie)
                VALUES (?, ?)
                """,
                (tresc, glosowanie_id)
            )
        except sqlite3.Error as e:
            print(f"An error occurred during insertion: {e}")

    def get_all_mozliwe_wybory_by_glosowanie_id(self, glosowanie_id):
        query = "SELECT * FROM Mozliwe_wybory WHERE glosowanie = ?"
        return self.execute_query(query, (glosowanie_id,), fetch_all=True)

    def get_mozliwy_wybor_by_id_by_glosowanie_id(self, mozliwy_wybor_id, glosowanie_id):
        query = "SELECT * FROM Mozliwe_wybory WHERE glosowanie = ? AND id = ?"
        return self.execute_query(query, (glosowanie_id, mozliwy_wybor_id), fetch_one=True)

    def update_mozliwy_wybor(self, mozliwy_wybor_id, glosowanie_id, tresc=None):
        query = """
                UPDATE Mozliwe_wybory
                SET tresc = COALESCE(?, tresc)
                WHERE glosowanie = ? AND id = ?
                """
        self.execute_query(query, (tresc, glosowanie_id, mozliwy_wybor_id))

    def delete_mozliwy_wybor(self, mozliwy_wybor_id, glosowanie_id):
        try:
            self.execute_query("DELETE FROM Mozliwe_wybory WHERE glosowanie = ? AND id = ?",
                               (glosowanie_id, mozliwy_wybor_id))
        except sqlite3.Error as e:
            print(f"An error occurred during deletion: {e}")

    def get_count_mozliwe_wybory(self, glosowanie_id):
        query = "SELECT COUNT(*) FROM Mozliwe_wybory WHERE glosowanie = ?"
        return self.execute_query(query, (glosowanie_id,), fetch_one=True)[0]

    def approve_glosowanie(self, voting_id):
        query = "UPDATE Glosowania SET czy_zakonczone = 1 WHERE id = ?"
        self.execute_query(query, (voting_id,))
        print(f"Głosowanie o ID {voting_id} zostało zatwierdzone.")

    def get_all_meetings(self):
        """Zwraca wszystkie spotkania."""
        query = "SELECT id, termin FROM Spotkania"
        return self.execute_query(query, fetch_all=True)

    def insert_meeting(self, date, duration, is_completed, admin_id):
        """Dodaje nowe spotkanie do bazy danych."""
        query = """
        INSERT INTO Spotkania (termin, czas_trwania, czy_zakonczone, administrator)
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (date, duration, is_completed, admin_id))

    def delete_meeting(self, meeting_id):
        """Usuwa spotkanie na podstawie ID."""
        query = "DELETE FROM Spotkania WHERE id = ?"
        self.execute_query(query, (meeting_id,))

    def update_meeting(self, meeting_id, date=None, duration=None, is_completed=None):
        """Aktualizuje dane spotkania."""
        query = """
        UPDATE Spotkania
        SET termin = COALESCE(?, termin),
            czas_trwania = COALESCE(?, czas_trwania),
            czy_zakonczone = COALESCE(?, czy_zakonczone)
        WHERE id = ?
        """
        self.execute_query(query, (date, duration, is_completed, meeting_id))