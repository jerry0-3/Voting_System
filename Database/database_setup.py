import sqlite3


def create_tables():
    connection = sqlite3.connect("Database\\voting_system.db")
    cursor = connection.cursor()

    # Table: Administratorzy
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Administratorzy (
        id INTEGER PRIMARY KEY AUTOINCREMENT
    )
    """)

    # Table: Wagi_glosow
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Wagi_glosow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            udzialy INTEGER NOT NULL
        )
        """)

    # Table: Spotkania
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Spotkania (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        termin DATETIME NOT NULL,
        czas_trwania INTERVAL NOT NULL,
        czy_zakonczone BOOLEAN NOT NULL,
        administrator INTEGER NOT NULL,
        FOREIGN KEY (administrator) REFERENCES Administratorzy (id)
    )
    """)

    # Table: Glosowania
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Glosowania (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        minimalne_udzialy INTEGER NOT NULL,
        temat TEXT NOT NULL,
        termin DATETIME NOT NULL,
        czas_trwania INTERVAL NOT NULL,
        czy_zakonczone BOOLEAN NOT NULL,
        spotkanie INTEGER NOT NULL,
        administrator INTEGER NOT NULL,
        FOREIGN KEY (spotkanie) REFERENCES Spotkania (id),
        FOREIGN KEY (administrator) REFERENCES Administratorzy (id)
    )
    """)

    # Table: Mozliwe_wybory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Mozliwe_wybory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tresc VARCHAR(255) NOT NULL,
        glosowanie INTEGER NOT NULL,
        FOREIGN KEY (glosowanie) REFERENCES Glosowania (id)
    )
    """)

    # Table: Wyniki
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Wyniki (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zatwierdzenie TEXT NOT NULL,
        wybor INTEGER NOT NULL,
        administrator INTEGER NOT NULL,
        glosowanie INTEGER NOT NULL,
        FOREIGN KEY (wybor) REFERENCES Mozliwe_wybory (id),
        FOREIGN KEY (administrator) REFERENCES Administratorzy (id),
        FOREIGN KEY (glosowanie) REFERENCES Glosowania (id)
    )
    """)

    # Table: Udzialowcy
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Udzialowcy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login VARCHAR(255) NOT NULL,
        haslo VARCHAR(255) NOT NULL,
        imie VARCHAR(255) NOT NULL,
        nazwisko VARCHAR(255) NOT NULL,
        waga_glosu INTEGER NOT NULL,
        FOREIGN KEY (waga_glosu) REFERENCES Wagi_glosow (id)
    )
    """)

    # Table: Glosy
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Glosy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        czas_oddanie DATETIME NOT NULL,
        id_udzialowca INTEGER NOT NULL,
        wybor INTEGER NOT NULL,
        glosowanie INTEGER NOT NULL,
        waga INTEGER NOT NULL,
        FOREIGN KEY (id_udzialowca) REFERENCES Udzialowcy (id),
        FOREIGN KEY (wybor) REFERENCES Mozliwe_wybory (id),
        FOREIGN KEY (glosowanie) REFERENCES Glosowania (id),
        FOREIGN KEY (waga) REFERENCES Wagi_glosow (id)
    )
    """)

    connection.commit()
    cursor.close()
    connection.close()
