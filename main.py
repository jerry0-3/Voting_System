from Database import create_tables, DatabaseController, insert_start_values
from GUI.HomeScreen import start_application

if __name__ == '__main__':
    create_tables()
    print("Database and tables created successfully!")
    controller = DatabaseController()
    insert_start_values(controller)

    # Example: Add a new udzialowiec
    udzialowcy = controller.get_all_udzialowcy()
    if len(udzialowcy) == 0:
        controller.insert_udzialowiec("jan_kowalski", "password123", "Jan", "Kowalski", 100)

    # Fetch and print all udzialowcy
    udzialowcy = controller.get_all_udzialowcy()
    print(udzialowcy)
    print(controller.execute_query("SELECT * FROM Spotkania", fetch_all=True))
    print(controller.execute_query("SELECT * FROM Administratorzy", fetch_all=True))

    print(controller.get_all_glosowania())

    choices = controller.get_all_mozliwe_wybory_by_glosowanie_id(2)
    print(choices)
    # for voting in votings:
    #     print(f"{voting[0]}: {voting[2]}")

    # waga_glosu_id = controller.execute_query("SELECT waga_glosu FROM Udzialowcy WHERE id = ?", (2,), fetch_one=True)[0]
    # print(controller.execute_query("SELECT * FROM Wagi_glosow WHERE id = ?", (waga_glosu_id,), fetch_one=True))
    # controller.execute_query("""
    #     UPDATE Wagi_glosow
    #     SET udzialy = COALESCE(?, udzialy)
    #     WHERE id = ?
    #     """, (15, waga_glosu_id))
    # print(controller.execute_query("SELECT * FROM Wagi_glosow WHERE id = ?", (waga_glosu_id,), fetch_one=True))

    start_application(controller)
