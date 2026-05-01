# Car Rental System (CUI Version - FULL LINE-BY-LINE COMMENTED)

from abc import ABC, abstractmethod  # Import ABC for abstract classes and abstract methods
import mysql.connector  # Import MySQL connector for database connection

# COLORS (ANSI ESCAPE CODES)
GREEN = "\033[92m"  # Green text for success messages
RED = "\033[91m"  # Red text for error messages
YELLOW = "\033[93m"  # Yellow text for warnings
CYAN = "\033[96m"  # Cyan text for menus
RESET = "\033[0m"  # Reset color back to default


# DATABASE CONNECTION FUNCTION
def get_db_connection():  # Function to create and return database connection
    return mysql.connector.connect(  # Return MySQL connection object
        host="localhost",  # Database host (local machine)
        user="root",  # MySQL username
        password="",  # MySQL password (empty here)
        database="car_rental"  # Database name
    )  # End connection setup


# USER CLASS
class User:  # Class representing a system user
    def __init__(self, username, role):  # Constructor for User class
        self.username = username  # Store username
        self.role = role  # Store user role (admin/customer)


# CAR ABSTRACT CLASS
class Car(ABC):  # Abstract base class for cars
    def __init__(self, car_id, brand, model, year, mileage, price, min_days, max_days, is_rented=False):
        self._car_id = car_id  # Store car ID (protected)
        self._brand = brand  # Store brand name
        self._model = model  # Store model name
        self._year = year  # Store manufacturing year
        self._mileage = mileage  # Store mileage
        self._price = price  # Store price per day
        self._min_days = min_days  # Minimum rental days allowed
        self._max_days = max_days  # Maximum rental days allowed
        self._is_rented = is_rented  # Rental status flag

    @abstractmethod  # Force child classes to implement this method
    def calculate_price(self, days):  # Method to calculate price
        pass  # No implementation here


# CAR TYPES (INHERITANCE)
class EconomyCar(Car):  # Economy car class
    def calculate_price(self, days):  # Override abstract method
        return self._price * days  # Basic pricing logic


class LuxuryCar(Car):  # Luxury car class
    def calculate_price(self, days):  # Override method
        return self._price * days * 1.5  # Luxury markup


class SUVCar(Car):  # SUV car class
    def calculate_price(self, days):  # Override method
        return self._price * days * 1.2  # SUV markup


# FACTORY PATTERN
class CarFactory:  # Factory class for creating car objects
    @staticmethod  # Static method (no object required)
    def create_car(car_type, *args):  # Create car based on type
        car_type = car_type.lower().strip()  # Normalize input

        if car_type == "economy":  # If economy selected
            return EconomyCar(*args)  # Return EconomyCar object
        elif car_type == "luxury":  # If luxury selected
            return LuxuryCar(*args)  # Return LuxuryCar object
        elif car_type == "suv":  # If SUV selected
            return SUVCar(*args)  # Return SUVCar object
        else:  # Invalid input
            raise ValueError("Invalid car type")  # Raise error


# SERVICE LAYER (DATABASE LOGIC)
class RentalService:  # Handles all DB operations
    def __init__(self):  # Constructor
        self.conn = get_db_connection()  # Create DB connection
        self.cursor = self.conn.cursor()  # Create cursor for queries

    def register_user(self, username, password, role):  # Register new user
        self.cursor.execute(  # Execute SQL insert
            "INSERT INTO users VALUES (%s,%s,%s)", (username, password, role)
        )  # End query
        self.conn.commit()  # Save changes
        print(GREEN + "User registered successfully" + RESET)  # Success message

    def add_car(self, car):  # Add car to database
        self.cursor.execute(  # Insert car into DB
            "INSERT INTO cars VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (car._car_id, car._brand, car._model, car._year, car._mileage,
             car._price, car._min_days, car._max_days, car._is_rented)
        )
        self.conn.commit()  # Save changes
        print(GREEN + "Car added successfully" + RESET)  # Success message

    def update_car(self, car_id, price):  # Update car price
        self.cursor.execute(  # SQL update query
            "UPDATE cars SET price=%s WHERE id=%s", (price, car_id)
        )
        self.conn.commit()  # Save changes
        print(GREEN + "Car updated successfully" + RESET)  # Success message

    def delete_car(self, car_id):  # Delete car
        self.cursor.execute(  # SQL delete query
            "DELETE FROM cars WHERE id=%s", (car_id,)
        )
        self.conn.commit()  # Save changes
        print(YELLOW + "Car deleted" + RESET)  # Warning message

    def list_cars(self):  # Show all cars
        self.cursor.execute("SELECT * FROM cars")  # Fetch all cars
        cars = self.cursor.fetchall()  # Get results

        if not cars:  # If no cars found
            print(YELLOW + "No cars available" + RESET)  # Warning message
            return  # Exit function

        print(CYAN + "\n===== CAR LIST =====" + RESET)  # Menu header

        for (id, brand, model, year, mileage, price, min_days, max_days, is_rented) in cars:
            status = "Rented" if is_rented else "Available"  # Status check

            print("\n----------------------------")  # Separator
            print(f"Car ID        : {id}")  # Display ID
            print(f"Brand         : {brand}")  # Display brand
            print(f"Model         : {model}")  # Display model
            print(f"Year          : {year}")  # Display year
            print(f"Mileage       : {mileage}")  # Display mileage
            print(f"Price/Day     : {price}")  # Display price
            print(f"Min Days      : {min_days}")  # Display min days
            print(f"Max Days      : {max_days}")  # Display max days
            print(f"Status        : {status}")  # Display status
            print("----------------------------")  # End separator

    def get_car(self, car_id):  # Get single car
        self.cursor.execute("SELECT * FROM cars WHERE id=%s", (car_id,))  # Query car
        return self.cursor.fetchone()  # Return result

    def create_booking(self, username, car_id, days):  # Create booking
        car = self.get_car(car_id)  # Fetch car

        if not car:  # If car not found
            raise Exception("Car not found")  # Error

        if car[8]:  # If already rented
            raise Exception("Car already rented")  # Error

        self.cursor.execute(  # Check duplicate booking
            "SELECT * FROM bookings WHERE username=%s AND car_id=%s AND status='pending'",
            (username, car_id)
        )
        if self.cursor.fetchone():  # If exists
            raise Exception("Duplicate pending booking")  # Error

        self.cursor.execute(
            "SELECT is_rented FROM cars WHERE id=%s",
            (car_id,)
        )
        car_status = self.cursor.fetchone()

        if car_status and car_status[0] == 1:
            raise Exception("Car is already rented")

        if days < car[6] or days > car[7]:  # Validate days
            raise Exception("Invalid rental duration")  # Error

        self.cursor.execute(  # Insert booking
            "INSERT INTO bookings VALUES (NULL,%s,%s,%s,%s)",
            (username, car_id, days, "pending")
        )
        self.conn.commit()  # Save
        print(GREEN + "Booking submitted" + RESET)  # Success

    def view_bookings(self):  # View all bookings with clear labels
        self.cursor.execute("SELECT * FROM bookings")  # Fetch all bookings
        bookings = self.cursor.fetchall()  # Store results

        if not bookings:  # If no bookings exist
            print(YELLOW + "No bookings found" + RESET)  # Show warning
            return  # Exit function

        print(CYAN + "\n===== BOOKING LIST =====" + RESET)  # Header

        for (booking_id, username, car_id, days, status) in bookings:  # Loop through each booking
            print("\n----------------------------")  # Separator
            print(f"Booking ID : {booking_id}")  # Show booking ID
            print(f"Username   : {username}")  # Show user
            print(f"Car ID     : {car_id}")  # Show car
            print(f"Days       : {days}")  # Show duration
            print(f"Status     : {status}")  # Show booking status
            print("----------------------------")  # End separator

    def approve_booking(self, booking_id):  # Approve booking
        self.cursor.execute(
            "SELECT car_id FROM bookings WHERE booking_id=%s",
            (booking_id,)
        )
        result = self.cursor.fetchone()  # Fetch result

        if not result:  # If not found
            raise Exception("Booking not found")  # Error

        car_id = result[0]  # Extract car ID

        self.cursor.execute(  # Check existing approval
            "SELECT * FROM bookings WHERE car_id=%s AND status='approved'",
            (car_id,)
        )
        if self.cursor.fetchone():  # If exists
            raise Exception("Already approved booking for this Vehicle exists")  # Error

        self.cursor.execute(  # Approve booking
            "UPDATE bookings SET status='approved' WHERE booking_id=%s",
            (booking_id,)
        )

        self.cursor.execute(  # Mark car rented
            "UPDATE cars SET is_rented=TRUE WHERE id=%s",
            (car_id,)
        )

        self.conn.commit()  # Save changes
        print(GREEN + "Booking approved" + RESET)  # Success

    def reject_booking(self, booking_id):  # Reject booking
        self.cursor.execute(  # Update status
            "UPDATE bookings SET status='rejected' WHERE booking_id=%s",
            (booking_id,)
        )
        self.conn.commit()  # Save
        print(YELLOW + "Booking rejected" + RESET)  # Warning

    def return_car(self, car_id):  # Return car
        self.cursor.execute(  # Update car status
            "UPDATE cars SET is_rented=FALSE WHERE id=%s",
            (car_id,)
        )
        self.conn.commit()  # Save
        print(GREEN + "Car returned" + RESET)  # Success


# MAIN APPLICATION
class CarRentalApp:  # Main app class
    def __init__(self):  # Constructor
        self.service = RentalService()  # Create service
        self.user = None  # No logged user

    def register(self):  # Register user
        username = input("Username: ")  # Input username
        password = input("Password: ")  # Input password
        role = input("Role: ")  # Input role
        self.service.register_user(username, password, role)  # Save user

    def login(self):  # Login system
        username = input("Username: ")  # Input username
        password = input("Password: ")  # Input password

        conn = get_db_connection()  # Connect DB
        cursor = conn.cursor()  # Cursor

        cursor.execute(  # Check login
            "SELECT role FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        result = cursor.fetchone()  # Get result

        if result:  # If valid
            self.user = User(username, result[0])  # Create session
            print(GREEN + "Login successful" + RESET)  # Success
        else:
            print(RED + "Invalid login" + RESET)  # Error

    def admin_menu(self):  # Admin menu
        while self.user and self.user.role == "admin":
            print(CYAN + "\n--- ADMIN MENU ---" + RESET)  # Menu header
            print("1.View 2.Add 3.Update 4.Delete 5.Bookings 6.Approve 7.Reject 8.Logout")

            choice = input()  # User input

            try:
                if choice == "1":
                    self.service.list_cars()

                elif choice == "2":
                    car_type = input("Type: ")  # Input type

                    car = CarFactory.create_car(
                        car_type,
                        int(input("ID: ")),
                        input("Brand: "),
                        input("Model: "),
                        int(input("Year: ")),
                        int(input("Mileage: ")),
                        float(input("Price: ")),
                        int(input("Min: ")),
                        int(input("Max: "))
                    )

                    self.service.add_car(car)

                elif choice == "3":
                    self.service.update_car(int(input("ID: ")), float(input("Price: ")))

                elif choice == "4":
                    self.service.delete_car(int(input("ID: ")))

                elif choice == "5":
                    self.service.view_bookings()

                elif choice == "6":
                    self.service.approve_booking(int(input("Booking ID: ")))

                elif choice == "7":
                    self.service.reject_booking(int(input("Booking ID: ")))

                elif choice == "8":
                    self.user = None
                    print(GREEN + "Logged out" + RESET)

            except Exception as e:
                print(RED + str(e) + RESET)

    def customer_menu(self):  # Customer menu
        while self.user and self.user.role == "customer":
            print(CYAN + "\n--- CUSTOMER MENU ---" + RESET)  # Menu header
            print("1.View Cars 2.Book 3.Logout")

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

                elif choice == "3":
                    self.user = None
                    print(GREEN + "Logged out" + RESET)

            except Exception as e:
                print(RED + str(e) + RESET)

    def run(self):  # Main loop
        while True:
            if not self.user:
                print(CYAN + "\n1.Register 2.Login" + RESET)  # Menu
                choice = input()

                if choice == "1":
                    self.register()
                elif choice == "2":
                    self.login()

            elif self.user.role == "admin":
                self.admin_menu()

            elif self.user.role == "customer":
                self.customer_menu()


if __name__ == "__main__":  # Start program
    app = CarRentalApp()  # Create app
    app.run()  # Run app