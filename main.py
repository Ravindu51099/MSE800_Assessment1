# Car Rental System (CUI Version - FULL LINE-BY-LINE COMMENTED)

from abc import ABC, abstractmethod  # Import ABC for creating abstract classes and abstract methods
import mysql.connector  # Import MySQL connector to interact with MySQL database


# DATABASE CONNECTION FUNCTION
def get_db_connection():  # Function to create a database connection
    return mysql.connector.connect(  # Return a connection object
        host="localhost",  # Database is hosted locally
        user="root",  # MySQL username
        password="",  # MySQL password (empty here)
        database="car_rental"  # Name of the database to use
    )  # End connection setup


# USER CLASS
class User:  # Define a User class
    def __init__(self, username, role):  # Constructor method
        self.username = username  # Store username in the object
        self.role = role  # Store user role (admin/customer)


# CAR ABSTRACT CLASS
class Car(ABC):  # Abstract base class for all car types
    def __init__(self, car_id, brand, model, year, mileage, price, min_days, max_days, is_rented=False):
        self._car_id = car_id  # Store car ID (protected variable)
        self._brand = brand  # Store brand name
        self._model = model  # Store model name
        self._year = year  # Store manufacturing year
        self._mileage = mileage  # Store mileage
        self._price = price  # Store price per day
        self._min_days = min_days  # Store minimum rental days allowed
        self._max_days = max_days  # Store maximum rental days allowed
        self._is_rented = is_rented  # Store rental status (default False)

    @abstractmethod  # Force subclasses to implement this method
    def calculate_price(self, days):  # Method to calculate rental cost
        pass  # No implementation here (must be overridden)


# CAR TYPES (INHERITANCE)
class EconomyCar(Car):  # EconomyCar inherits from Car
    def calculate_price(self, days):  # Override abstract method
        return self._price * days  # Simple multiplication pricing


class LuxuryCar(Car):  # LuxuryCar inherits from Car
    def calculate_price(self, days):  # Override method
        return self._price * days * 1.5  # Add 50% surcharge


class SUVCar(Car):  # SUVCar inherits from Car
    def calculate_price(self, days):  # Override method
        return self._price * days * 1.2  # Add 20% surcharge


# FACTORY PATTERN
class CarFactory:  # Factory class to create car objects
    @staticmethod  # Static method (no instance needed)
    def create_car(car_type, *args):  # Method to create car based on type
        car_type = car_type.lower().strip()  # Normalize input

        if car_type == "economy":  # If type is economy
            return EconomyCar(*args)  # Return EconomyCar object
        elif car_type == "luxury":  # If type is luxury
            return LuxuryCar(*args)  # Return LuxuryCar object
        elif car_type == "suv":  # If type is SUV
            return SUVCar(*args)  # Return SUVCar object
        else:  # If invalid type
            raise ValueError("Invalid car type. Use economy/luxury/suv")  # Raise error


# SERVICE LAYER (DATABASE LOGIC)
class RentalService:  # Handles all database operations
    def __init__(self):  # Constructor
        self.conn = get_db_connection()  # Establish DB connection
        self.cursor = self.conn.cursor()  # Create cursor for executing queries

    def register_user(self, username, password, role):  # Register a new user
        self.cursor.execute("INSERT INTO users VALUES (%s,%s,%s)", (username, password, role))  # Insert user record
        self.conn.commit()  # Save changes

    def add_car(self, car):  # Add a new car to DB
        self.cursor.execute(
            "INSERT INTO cars VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",  # SQL insert statement
            (car._car_id, car._brand, car._model, car._year, car._mileage,
             car._price, car._min_days, car._max_days, car._is_rented)  # Pass car data
        )
        self.conn.commit()  # Save changes
        print("Car added successfully")  # Confirmation message

    def update_car(self, car_id, price):  # Update car price
        self.cursor.execute("UPDATE cars SET price=%s WHERE id=%s", (price, car_id))  # SQL update
        self.conn.commit()  # Save changes

    def delete_car(self, car_id):  # Delete a car
        self.cursor.execute("DELETE FROM cars WHERE id=%s", (car_id,))  # SQL delete
        self.conn.commit()  # Save changes

    def list_cars(self):  # Display all cars
        self.cursor.execute("SELECT * FROM cars")  # Fetch all cars
        cars = self.cursor.fetchall()  # Store results

        if not cars:  # If no cars exist
            print("No cars available")  # Inform user
            return  # Exit function

        print("\n===== CAR LIST =====")  # Header

        for (id, brand, model, year, mileage, price, min_days, max_days, is_rented) in cars:  # Loop through cars
            status = "Rented" if is_rented else "Available"  # Determine availability

            print("\n----------------------------")  # Separator
            print(f"Car ID        : {id}")  # Display ID
            print(f"Brand         : {brand}")  # Display brand
            print(f"Model         : {model}")  # Display model
            print(f"Year          : {year}")  # Display year
            print(f"Mileage       : {mileage} km")  # Display mileage
            print(f"Price/Day     : ${price}")  # Display price
            print(f"Min Rent Days : {min_days}")  # Display minimum days
            print(f"Max Rent Days : {max_days}")  # Display maximum days
            print(f"Status        : {status}")  # Display status
            print("----------------------------")  # End separator

    def get_car(self, car_id):  # Get a specific car
        self.cursor.execute("SELECT * FROM cars WHERE id=%s", (car_id,))  # Query by ID
        return self.cursor.fetchone()  # Return one result

    # CREATE BOOKING 
    def create_booking(self, username, car_id, days):  # Create booking request
        car = self.get_car(car_id)  # Fetch car

        if not car:  # If car doesn't exist
            raise Exception("Car not found")  # Error

        if car[8]:  # If already rented
            raise Exception("Car already rented")  # Prevent booking

        # Prevent duplicate pending booking by same user
        self.cursor.execute(
            "SELECT * FROM bookings WHERE username=%s AND car_id=%s AND status='pending'",
            (username, car_id)
        )
        if self.cursor.fetchone():  # If exists
            raise Exception("You already have a pending booking for this car")

        # Prevent booking if already approved
        self.cursor.execute(
            "SELECT * FROM bookings WHERE car_id=%s AND status='approved'",
            (car_id,)
        )
        if self.cursor.fetchone():  # If exists
            raise Exception("Car is already booked")

        if days < car[6] or days > car[7]:  # Validate rental days
            raise Exception("Invalid rental duration")

        self.cursor.execute(
            "INSERT INTO bookings (username, car_id, days, status) VALUES (%s,%s,%s,%s)",
            (username, car_id, days, "pending")
        )
        self.conn.commit()  # Save
        print("Booking request submitted")  # Success

    def view_bookings(self):  # View all bookings
        self.cursor.execute("SELECT * FROM bookings")  # Fetch all bookings
        for booking in self.cursor.fetchall():  # Loop through results
            print(booking)  # Display each booking

    # APPROVE BOOKING
    def approve_booking(self, booking_id):  # Approve a booking
        self.cursor.execute(
            "SELECT car_id FROM bookings WHERE booking_id=%s",
            (booking_id,)
        )
        result = self.cursor.fetchone()  # Get result

        if not result:  # If booking doesn't exist
            raise Exception("Booking not found")

        car_id = result[0]  # Extract car ID

        # Prevent multiple approvals for same car
        self.cursor.execute(
            "SELECT * FROM bookings WHERE car_id=%s AND status='approved'",
            (car_id,)
        )
        if self.cursor.fetchone():  # If exists
            raise Exception("Car already has an approved booking")

        self.cursor.execute(
            "UPDATE bookings SET status='approved' WHERE booking_id=%s",
            (booking_id,)
        )

        self.cursor.execute(
            "UPDATE cars SET is_rented=TRUE WHERE id=%s",
            (car_id,)
        )

        self.conn.commit()  # Save changes
        print("Booking approved successfully")  # Confirmation

    def reject_booking(self, booking_id):  # Reject booking
        self.cursor.execute("UPDATE bookings SET status='rejected' WHERE booking_id=%s", (booking_id,))
        self.conn.commit()  # Save changes

    def return_car(self, car_id):  # Return a car
        car = self.get_car(car_id)  # Get car

        if not car:  # If not found
            raise Exception("Car not found")

        if not car[8]:  # If already available
            raise Exception("Car already available, cannot return")

        self.cursor.execute("UPDATE cars SET is_rented=FALSE WHERE id=%s", (car_id,))
        self.conn.commit()  # Save


# MAIN APPLICATION
class CarRentalApp:  # Main application class
    def __init__(self):  # Constructor
        self.service = RentalService()  # Create service instance
        self.user = None  # No user logged in

    def register(self):  # Register user
        username = input("Username: ")  # Get username
        password = input("Password: ")  # Get password
        role = input("Role (admin/customer): ").lower()  # Get role
        self.service.register_user(username, password, role)  # Save user

    def login(self):  # Login function
        username = input("Username: ")  # Input username
        password = input("Password: ")  # Input password

        conn = get_db_connection()  # Connect to DB
        cursor = conn.cursor()  # Create cursor

        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()  # Get result

        if result:  # If valid login
            self.user = User(username, result[0])  # Create session
            print(f"Logged in as {result[0]}")  # Show role
        else:
            print("Invalid login")  # Error message

    def admin_menu(self):  # Admin menu loop
        while self.user and self.user.role == "admin":
            print("\n--- ADMIN MENU ---")
            print("1.View Cars 2.Add 3.Update 4.Delete 5.Bookings 6.Approve 7.Reject 8.Logout")

            choice = input()

            try:
                if choice == "1":
                    self.service.list_cars()

                elif choice == "2":
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

                elif choice == "8":
                    self.user = None
                    print("Logged out successfully")

            except Exception as e:
                print("Error:", e)

    def customer_menu(self):  # Customer menu loop
        while self.user and self.user.role == "customer":
            print("\n--- CUSTOMER MENU ---")
            print("1.View Cars 2.Book Car 3.Logout")

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
                    print("Logged out successfully")

            except Exception as e:
                print("Error:", e)

    def run(self):  # Main loop
        while True:
            if not self.user:
                print("\n1.Register 2.Login")
                choice = input()

                if choice == "1":
                    self.register()
                elif choice == "2":
                    self.login()

            elif self.user.role == "admin":
                self.admin_menu()

            elif self.user.role == "customer":
                self.customer_menu()


if __name__ == "__main__":  # Entry point
    app = CarRentalApp()  # Create app instance
    app.run()  # Start application