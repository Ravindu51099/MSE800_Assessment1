# Car Rental System

from abc import ABC, abstractmethod  # Import abstract base class for abstraction
import mysql.connector  # Import MySQL connector

# DATABASE CONNECTION
def get_db_connection():
    return mysql.connector.connect(  # Establish connection to MySQL
        host="localhost",  # Database host
        user="root",  # MySQL username
        password="",  # MySQL password (SET YOUR PASSWORD HERE)
        database="car_rental"  # Database name
    )

# USER CLASS
class User:
    def __init__(self, username, role):
        self.username = username  # Store username
        self.role = role  # Store role (admin/customer)


# CAR ABSTRACT CLASS
class Car(ABC):  # Abstract base class
    def __init__(self, car_id, brand, model, base_price_per_day, is_rented=False):
        self._car_id = car_id  # Unique ID
        self._brand = brand  # Brand name
        self._model = model  # Model name
        self._base_price_per_day = base_price_per_day  # Daily price
        self._is_rented = is_rented  # Rental status

    def get_id(self):
        return self._car_id  # Return ID

    def is_rented(self):
        return self._is_rented  # Return rental status

    def rent(self):
        if self._is_rented:  # If already rented
            raise Exception("Car already rented!")  # Prevent duplicate rent
        self._is_rented = True  # Mark rented

    def return_car(self):
        if not self._is_rented:  # If not rented
            raise Exception("Car is not rented!")  # Prevent invalid return
        self._is_rented = False  # Mark available

    @abstractmethod
    def calculate_price(self, days):  # Abstract method
        pass

    def display(self):
        status = "Rented" if self._is_rented else "Available"  # Determine status
        return f"ID: {self._car_id} | {self._brand} {self._model} | Status: {status}"

# CAR TYPES (INHERITANCE)
class EconomyCar(Car):
    def calculate_price(self, days):
        return self._base_price_per_day * days  # Normal pricing

class LuxuryCar(Car):
    def calculate_price(self, days):
        return self._base_price_per_day * days * 1.5  # 50% extra

class SUVCar(Car):
    def calculate_price(self, days):
        return self._base_price_per_day * days * 1.2  # 20% extra


# FACTORY PATTERN
class CarFactory:
    @staticmethod
    def create_car(car_type, car_id, brand, model, price, is_rented=False):
        if car_type == "economy":
            return EconomyCar(car_id, brand, model, price, is_rented)
        elif car_type == "luxury":
            return LuxuryCar(car_id, brand, model, price, is_rented)
        elif car_type == "suv":
            return SUVCar(car_id, brand, model, price, is_rented)
        else:
            raise ValueError("Invalid car type")


# SERVICE LAYER (MYSQL)
class RentalService:
    def __init__(self):
        self.conn = get_db_connection()  # Connect to database
        self.cursor = self.conn.cursor()  # Create cursor

    def add_car(self, car):
        query = "INSERT INTO cars (id, brand, model, price, is_rented) VALUES (%s,%s,%s,%s,%s)"
        self.cursor.execute(query, (car._car_id, car._brand, car._model, car._base_price_per_day, car._is_rented))
        self.conn.commit()
        print("Car added successfully")

    def remove_car(self, car_id):
        self.cursor.execute("DELETE FROM cars WHERE id=%s", (car_id,))
        self.conn.commit()
        print("Car removed successfully")

    def list_cars(self):
        self.cursor.execute("SELECT * FROM cars")
        cars = self.cursor.fetchall()

        if not cars:
            print("No cars available")
            return

        for (id, brand, model, price, is_rented) in cars:
            status = "Rented" if is_rented else "Available"
            print(f"ID: {id} | {brand} {model} | Status: {status}")

    def find_car(self, car_id):
        self.cursor.execute("SELECT * FROM cars WHERE id=%s", (car_id,))
        return self.cursor.fetchone()

    def rent_car(self, car_id, days):
        if days <= 0:
            raise Exception("Invalid number of days")

        car = self.find_car(car_id)

        if not car:
            raise Exception("Car not found")

        if car[4]:  # is_rented
            raise Exception("Car already rented")

        base_cost = car[3] * days

        # Discount logic
        discount = 0
        if days >= 14:
            discount = 0.10
        elif days >= 7:
            discount = 0.05

        discount_amount = base_cost * discount
        final_cost = base_cost - discount_amount

        self.cursor.execute("UPDATE cars SET is_rented=TRUE WHERE id=%s", (car_id,))
        self.conn.commit()

        print(f"Base Cost: ${base_cost}")
        print(f"Discount: ${discount_amount}")
        print(f"Final Cost: ${final_cost}")

    def return_car(self, car_id):
        car = self.find_car(car_id)  # Get car from DB

        if not car:
            raise Exception("Car not found")

        if not car[4]:  # FIX: Check if already available
            raise Exception("Car is already available, cannot return")

        self.cursor.execute("UPDATE cars SET is_rented=FALSE WHERE id=%s", (car_id,))
        self.conn.commit()
        print("Car returned successfully")


# MAIN APPLICATION
class CarRentalApp:
    def __init__(self):
        self.service = RentalService()
        self.current_user = None

    def login(self):
        print("\n--- LOGIN ---")
        username = input("Username: ")
        password = input("Password: ")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()

        if result:
            self.current_user = User(username, result[0])
            print(f"Login successful! Logged in as {result[0]}")
        else:
            print("Invalid credentials")

    def admin_menu(self):
        print("\n--- ADMIN MENU ---")
        print("1. View Cars")
        print("2. Add Car")
        print("3. Remove Car")
        print("4. Logout")

        choice = input("Enter choice: ")

        try:
            if choice == "1":
                self.service.list_cars()

            elif choice == "2":
                car_id = int(input("ID: "))
                brand = input("Brand: ")
                model = input("Model: ")
                price = float(input("Price: "))
                car_type = input("Type (economy/luxury/suv): ")

                car = CarFactory.create_car(car_type, car_id, brand, model, price)
                self.service.add_car(car)

            elif choice == "3":
                car_id = int(input("Enter ID: "))
                self.service.remove_car(car_id)

            elif choice == "4":
                self.current_user = None

            else:
                print("Invalid choice")

        except Exception as e:
            print("Error:", e)

    def customer_menu(self):
        print("\n--- CUSTOMER MENU ---")
        print("1. View Cars")
        print("2. Rent Car")
        print("3. Return Car")
        print("4. Logout")

        choice = input("Enter choice:")

        try:
            if choice == "1":
                self.service.list_cars()

            elif choice == "2":
                car_id = int(input("Car ID: "))
                days = int(input("Days: "))
                self.service.rent_car(car_id, days)

            elif choice == "3":
                car_id = int(input("Car ID: "))
                self.service.return_car(car_id)

            elif choice == "4":
                self.current_user = None

            else:
                print("Invalid choice")

        except Exception as e:
            print("Error:", e)

    def run(self):
        while True:
            if not self.current_user:
                self.login()
            elif self.current_user.role == "admin":
                self.admin_menu()
            elif self.current_user.role == "customer":
                self.customer_menu()

# RUN APPLICATION
if __name__ == "__main__":
    app = CarRentalApp()
    app.run()