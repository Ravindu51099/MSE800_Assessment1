# Car Rental System (CUI Version - FINAL FIXED VERSION)

from abc import ABC, abstractmethod  # Import abstraction tools
import mysql.connector  # Import MySQL connector


# =========================
# DATABASE CONNECTION
# =========================
def get_db_connection():
    return mysql.connector.connect(  # Connect to MySQL database
        host="localhost",
        user="root",
        password="",  # SET YOUR PASSWORD HERE
        database="car_rental"
    )


# =========================
# USER CLASS
# =========================
class User:
    def __init__(self, username, role):
        self.username = username  # Store username
        self.role = role  # Store role (admin/customer)


# =========================
# CAR ABSTRACT CLASS
# =========================
class Car(ABC):
    def __init__(self, car_id, brand, model, year, mileage, price, min_days, max_days, is_rented=False):
        self._car_id = car_id  # Car ID
        self._brand = brand  # Brand
        self._model = model  # Model
        self._year = year  # Year
        self._mileage = mileage  # Mileage
        self._price = price  # Price per day
        self._min_days = min_days  # Minimum rental days
        self._max_days = max_days  # Maximum rental days
        self._is_rented = is_rented  # Rental status

    @abstractmethod
    def calculate_price(self, days):  # Abstract method
        pass


# =========================
# CAR TYPES (INHERITANCE)
# =========================
class EconomyCar(Car):
    def calculate_price(self, days):
        return self._price * days  # Basic pricing


class LuxuryCar(Car):
    def calculate_price(self, days):
        return self._price * days * 1.5  # 50% higher


class SUVCar(Car):
    def calculate_price(self, days):
        return self._price * days * 1.2  # 20% higher


# =========================
# FACTORY PATTERN
# =========================
class CarFactory:
    @staticmethod
    def create_car(car_type, *args):
        car_type = car_type.lower().strip()  # FIX: normalize user input

        if car_type == "economy":
            return EconomyCar(*args)
        elif car_type == "luxury":
            return LuxuryCar(*args)
        elif car_type == "suv":
            return SUVCar(*args)
        else:
            raise ValueError("Invalid car type. Use economy/luxury/suv")


# =========================
# SERVICE LAYER
# =========================
class RentalService:
    def __init__(self):
        self.conn = get_db_connection()  # Open DB connection
        self.cursor = self.conn.cursor()  # Create cursor

    # USER REGISTRATION
    def register_user(self, username, password, role):
        self.cursor.execute("INSERT INTO users VALUES (%s,%s,%s)", (username, password, role))
        self.conn.commit()

    # ADD CAR
    def add_car(self, car):
        self.cursor.execute(
            "INSERT INTO cars VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (car._car_id, car._brand, car._model, car._year, car._mileage,
             car._price, car._min_days, car._max_days, car._is_rented)
        )
        self.conn.commit()
        print("Car added successfully")

    # UPDATE CAR
    def update_car(self, car_id, price):
        self.cursor.execute("UPDATE cars SET price=%s WHERE id=%s", (price, car_id))
        self.conn.commit()

    # DELETE CAR
    def delete_car(self, car_id):
        self.cursor.execute("DELETE FROM cars WHERE id=%s", (car_id,))
        self.conn.commit()

    # LIST ALL CARS
    def list_cars(self):
        self.cursor.execute("SELECT * FROM cars")
        cars = self.cursor.fetchall()

        if not cars:
            print("No cars available")
            return

        for car in cars:
            print(car)

    # GET CAR BY ID
    def get_car(self, car_id):
        self.cursor.execute("SELECT * FROM cars WHERE id=%s", (car_id,))
        return self.cursor.fetchone()

    # CREATE BOOKING
    def create_booking(self, username, car_id, days):
        car = self.get_car(car_id)

        if not car:
            raise Exception("Car not found")

        if car[8]:  # is_rented check
            raise Exception("Car already rented")

        # Validate rental duration
        if days < car[6] or days > car[7]:
            raise Exception("Invalid rental duration")

        self.cursor.execute(
            "INSERT INTO bookings (username, car_id, days, status) VALUES (%s,%s,%s,%s)",
            (username, car_id, days, "pending")
        )
        self.conn.commit()
        print("Booking request submitted")

    # VIEW BOOKINGS
    def view_bookings(self):
        self.cursor.execute("SELECT * FROM bookings")
        for booking in self.cursor.fetchall():
            print(booking)

    # APPROVE BOOKING
    def approve_booking(self, booking_id):
        self.cursor.execute("UPDATE bookings SET status='approved' WHERE booking_id=%s", (booking_id,))
        self.conn.commit()

    # REJECT BOOKING
    def reject_booking(self, booking_id):
        self.cursor.execute("UPDATE bookings SET status='rejected' WHERE booking_id=%s", (booking_id,))
        self.conn.commit()

    # RETURN CAR (FIXED)
    def return_car(self, car_id):
        car = self.get_car(car_id)

        if not car:
            raise Exception("Car not found")

        if not car[8]:  # FIX: already available
            raise Exception("Car already available, cannot return")

        self.cursor.execute("UPDATE cars SET is_rented=FALSE WHERE id=%s", (car_id,))
        self.conn.commit()


# =========================
# MAIN APPLICATION
# =========================
class CarRentalApp:
    def __init__(self):
        self.service = RentalService()
        self.user = None

    # REGISTER
    def register(self):
        username = input("Username: ")
        password = input("Password: ")
        role = input("Role (admin/customer): ").lower()
        self.service.register_user(username, password, role)

    # LOGIN
    def login(self):
        username = input("Username: ")
        password = input("Password: ")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()

        if result:
            self.user = User(username, result[0])
            print(f"Logged in as {result[0]}")
        else:
            print("Invalid login")

    # ADMIN MENU
    def admin_menu(self):
        print("\n--- ADMIN MENU ---")
        print("1.View Cars 2.Add 3.Update 4.Delete 5.Bookings 6.Approve 7.Reject")

        choice = input()

        try:
            if choice == "1":
                self.service.list_cars()

            elif choice == "2":
                # FIX: VALIDATION LOOP FOR CAR TYPE
                while True:
                    car_type = input("Type (economy/luxury/suv): ").lower().strip()
                    if car_type in ["economy", "luxury", "suv"]:
                        break
                    print("Invalid type. Try again.")

                car = CarFactory.create_car(
                    car_type,
                    int(input("ID: ")),
                    input("Brand: "),
                    input("Model: "),
                    int(input("Year: ")),
                    int(input("Mileage: ")),
                    float(input("Price: ")),
                    int(input("Min days: ")),
                    int(input("Max days: "))
                )

                self.service.add_car(car)

            elif choice == "3":
                self.service.update_car(int(input("ID: ")), float(input("New Price: ")))

            elif choice == "4":
                self.service.delete_car(int(input("ID: ")))

            elif choice == "5":
                self.service.view_bookings()

            elif choice == "6":
                self.service.approve_booking(int(input("Booking ID: ")))

            elif choice == "7":
                self.service.reject_booking(int(input("Booking ID: ")))

        except Exception as e:
            print("Error:", e)

    # CUSTOMER MENU
    def customer_menu(self):
        print("\n--- CUSTOMER MENU ---")
        print("1.View Cars 2.Book Car")

        choice = input()

        try:
            if choice == "1":
                self.service.list_cars()

            elif choice == "2":
                self.service.create_booking(
                    self.user.username,
                    int(input("Car ID: ")),
                    int(input("Days: "))
                )

        except Exception as e:
            print("Error:", e)

    # MAIN LOOP
    def run(self):
        while True:
            # If no user logged in → show login/register
            if not self.user:
                print("\n1.Register 2.Login")
                choice = input()

                if choice == "1":
                    self.register()

                elif choice == "2":
                    self.login()

            # If Admin logged in → stay in admin menu
            elif self.user.role == "admin":
                self.admin_menu()

            # If Customer logged in → stay in customer menu
            elif self.user.role == "customer":
                self.customer_menu()


# =========================
# RUN PROGRAM
# =========================
if __name__ == "__main__":
    app = CarRentalApp()
    app.run()