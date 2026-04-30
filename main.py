# Car Rental System (CUI Version - FULL LINE-BY-LINE COMMENTED)

from abc import ABC, abstractmethod  # Import ABC for abstraction and abstractmethod decorator
import mysql.connector  # Import MySQL connector library for database operations


# DATABASE CONNECTION FUNCTION

def get_db_connection():  # Define function to create and return DB connection
    return mysql.connector.connect(  # Return a new MySQL connection object
        host="localhost",  # Specify database host (local machine)
        user="root",  # MySQL username
        password="",  # MySQL password (empty here, should be set if required)
        database="car_rental"  # Name of database to connect to
    )  # End of connection setup



# USER CLASS
class User:  # Define User class
    def __init__(self, username, role):  # Constructor for User object
        self.username = username  # Store username in object
        self.role = role  # Store role (admin/customer)

# CAR ABSTRACT CLASS
class Car(ABC):  # Abstract base class for all cars
    def __init__(self, car_id, brand, model, year, mileage, price, min_days, max_days, is_rented=False):  # Constructor
        self._car_id = car_id  # Store car ID (protected variable)
        self._brand = brand  # Store car brand
        self._model = model  # Store car model
        self._year = year  # Store manufacturing year
        self._mileage = mileage  # Store mileage of car
        self._price = price  # Store price per day
        self._min_days = min_days  # Store minimum rental days
        self._max_days = max_days  # Store maximum rental days
        self._is_rented = is_rented  # Store rental status (default False)

    @abstractmethod  # Force subclasses to implement this method
    def calculate_price(self, days):  # Method to calculate rental price
        pass  # No implementation here (abstract method)

# CAR TYPES (INHERITANCE)
class EconomyCar(Car):  # Economy car class inherits Car
    def calculate_price(self, days):  # Override method
        return self._price * days  # Basic price calculation

class LuxuryCar(Car):  # Luxury car class inherits Car
    def calculate_price(self, days):  # Override method
        return self._price * days * 1.5  # Luxury surcharge applied

class SUVCar(Car):  # SUV car class inherits Car
    def calculate_price(self, days):  # Override method
        return self._price * days * 1.2  # SUV surcharge applied

# FACTORY PATTERN
class CarFactory:  # Factory class to create car objects
    @staticmethod  # Method can be called without creating object
    def create_car(car_type, *args):  # Create car dynamically based on type
        car_type = car_type.lower().strip()  # Normalize input string

        if car_type == "economy":  # If economy selected
            return EconomyCar(*args)  # Create EconomyCar object
        elif car_type == "luxury":  # If luxury selected
            return LuxuryCar(*args)  # Create LuxuryCar object
        elif car_type == "suv":  # If SUV selected
            return SUVCar(*args)  # Create SUVCar object
        else:  # If invalid type entered
            raise ValueError("Invalid car type. Use economy/luxury/suv")  # Raise error

# SERVICE LAYER (DATABASE LOGIC)
class RentalService:  # Handles all DB operations
    def __init__(self):  # Constructor
        self.conn = get_db_connection()  # Create DB connection
        self.cursor = self.conn.cursor()  # Create cursor for queries

    def register_user(self, username, password, role):  # Register new user
        self.cursor.execute("INSERT INTO users VALUES (%s,%s,%s)", (username, password, role))  # Insert user
        self.conn.commit()  # Save changes to database

    def add_car(self, car):  # Add car to database
        self.cursor.execute(  # Execute SQL query
            "INSERT INTO cars VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",  # SQL insert statement
            (car._car_id, car._brand, car._model, car._year, car._mileage,  # Car details
             car._price, car._min_days, car._max_days, car._is_rented)  # More car details
        )  # End query execution
        self.conn.commit()  # Save changes
        print("Car added successfully")  # Confirmation message

    def update_car(self, car_id, price):  # Update car price
        self.cursor.execute("UPDATE cars SET price=%s WHERE id=%s", (price, car_id))  # Update query
        self.conn.commit()  # Save changes

    def delete_car(self, car_id):  # Delete car from DB
        self.cursor.execute("DELETE FROM cars WHERE id=%s", (car_id,))  # Delete query
        self.conn.commit()  # Save changes

    def list_cars(self):  # List all cars
        self.cursor.execute("SELECT * FROM cars")  # Fetch all cars
        cars = self.cursor.fetchall()  # Store results

        if not cars:  # If no cars found
            print("No cars available")  # Print message
            return  # Exit function

        print("\n===== CAR LIST =====")  # Header

        for (id, brand, model, year, mileage, price, min_days, max_days, is_rented) in cars:  # Loop cars
            status = "Rented" if is_rented else "Available"  # Determine status

            print("\n----------------------------")  # Separator
            print(f"Car ID        : {id}")  # Print ID
            print(f"Brand         : {brand}")  # Print brand
            print(f"Model         : {model}")  # Print model
            print(f"Year          : {year}")  # Print year
            print(f"Mileage       : {mileage} km")  # Print mileage
            print(f"Price/Day     : ${price}")  # Print price
            print(f"Min Rent Days : {min_days}")  # Print min days
            print(f"Max Rent Days : {max_days}")  # Print max days
            print(f"Status        : {status}")  # Print status
            print("----------------------------")  # Separator end

    def get_car(self, car_id):  # Get single car
        self.cursor.execute("SELECT * FROM cars WHERE id=%s", (car_id,))  # Query
        return self.cursor.fetchone()  # Return single result

    def create_booking(self, username, car_id, days):  # Create booking
        car = self.get_car(car_id)  # Fetch car

        if not car:  # If car not found
            raise Exception("Car not found")  # Error

        if car[8]:  # If rented
            raise Exception("Car already rented")  # Error

        if days < car[6] or days > car[7]:  # Validate days
            raise Exception("Invalid rental duration")  # Error

        self.cursor.execute(  # Insert booking
            "INSERT INTO bookings (username, car_id, days, status) VALUES (%s,%s,%s,%s)",
            (username, car_id, days, "pending")  # Booking data
        )
        self.conn.commit()  # Save
        print("Booking request submitted")  # Success

    def view_bookings(self):  # View all bookings
        self.cursor.execute("SELECT * FROM bookings")  # Fetch
        for booking in self.cursor.fetchall():  # Loop
            print(booking)  # Print booking

    def approve_booking(self, booking_id):  # Approve booking
        self.cursor.execute("UPDATE bookings SET status='approved' WHERE booking_id=%s", (booking_id,))  # Update
        self.conn.commit()  # Save

    def reject_booking(self, booking_id):  # Reject booking
        self.cursor.execute("UPDATE bookings SET status='rejected' WHERE booking_id=%s", (booking_id,))  # Update
        self.conn.commit()  # Save

    def return_car(self, car_id):  # Return car
        car = self.get_car(car_id)  # Get car

        if not car:  # If not found
            raise Exception("Car not found")  # Error

        if not car[8]:  # If already available
            raise Exception("Car already available, cannot return")  # Error

        self.cursor.execute("UPDATE cars SET is_rented=FALSE WHERE id=%s", (car_id,))  # Update
        self.conn.commit()  # Save

# MAIN APPLICATION
class CarRentalApp:  # Main app class
    def __init__(self):  # Constructor
        self.service = RentalService()  # Create service
        self.user = None  # No user logged in

    def register(self):  # Register user
        username = input("Username: ")  # Input username
        password = input("Password: ")  # Input password
        role = input("Role (admin/customer): ").lower()  # Input role
        self.service.register_user(username, password, role)  # Register

    def login(self):  # Login user
        username = input("Username: ")  # Input username
        password = input("Password: ")  # Input password

        conn = get_db_connection()  # Connect DB
        cursor = conn.cursor()  # Cursor

        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))  # Query
        result = cursor.fetchone()  # Fetch result

        if result:  # If valid
            self.user = User(username, result[0])  # Create session
            print(f"Logged in as {result[0]}")  # Success
        else:  # If invalid
            print("Invalid login")  # Error

    def admin_menu(self):  # Admin menu
        while self.user and self.user.role == "admin":  # Loop menu
            print("\n--- ADMIN MENU ---")  # Header
            print("1.View Cars 2.Add 3.Update 4.Delete 5.Bookings 6.Approve 7.Reject 8.Logout")  # Options

            choice = input()  # User choice

            try:  # Error handling
                if choice == "1":  # View cars
                    self.service.list_cars()

                elif choice == "2":  # Add car
                    while True:  # Validate type
                        car_type = input("Type (economy/luxury/suv): ").lower().strip()
                        if car_type in ["economy", "luxury", "suv"]:
                            break
                        print("Invalid type. Try again.")

                    car = CarFactory.create_car(  # Create car
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

                    self.service.add_car(car)  # Add to DB

                elif choice == "3":  # Update
                    self.service.update_car(int(input("ID: ")), float(input("New Price: ")))

                elif choice == "4":  # Delete
                    self.service.delete_car(int(input("ID: ")))

                elif choice == "5":  # View bookings
                    self.service.view_bookings()

                elif choice == "6":  # Approve
                    self.service.approve_booking(int(input("Booking ID: ")))

                elif choice == "7":  # Reject
                    self.service.reject_booking(int(input("Booking ID: ")))

                elif choice == "8":  # Logout
                    self.user = None  # End session
                    print("Logged out successfully")  # Message

            except Exception as e:  # Catch errors
                print("Error:", e)  # Print error

    def customer_menu(self):  # Customer menu
        while self.user and self.user.role == "customer":  # Loop
            print("\n--- CUSTOMER MENU ---")  # Header
            print("1.View Cars 2.Book Car 3.Logout")  # Options

            choice = input()  # Input

            try:  # Error handling
                if choice == "1":  # View cars
                    self.service.list_cars()

                elif choice == "2":  # Book car
                    self.service.create_booking(
                        self.user.username,
                        int(input("Car ID: ")),
                        int(input("Days: "))
                    )

                elif choice == "3":  # Logout
                    self.user = None  # End session
                    print("Logged out successfully")  # Message

            except Exception as e:  # Handle errors
                print("Error:", e)

    def run(self):  # Main loop
        while True:  # Infinite loop
            if not self.user:  # If no login
                print("\n1.Register 2.Login")  # Options
                choice = input()  # Input

                if choice == "1":  # Register
                    self.register()

                elif choice == "2":  # Login
                    self.login()

            elif self.user.role == "admin":  # Admin
                self.admin_menu()

            elif self.user.role == "customer":  # Customer
                self.customer_menu()

if __name__ == "__main__":  # Start program
    app = CarRentalApp()  # Create app
    app.run()  # Run app