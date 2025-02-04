from Database import create_tables, DatabaseController, insert_start_values
from GUI.HomeScreen import start_application

if __name__ == '__main__':
    create_tables()
    print("Database and tables created successfully!")
    controller = DatabaseController()
    insert_start_values(controller)

    start_application(controller)
