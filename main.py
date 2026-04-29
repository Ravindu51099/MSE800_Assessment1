# Car Rental System (CUI Version)
# Features:
# - OOP (Encapsulation, Inheritance, Polymorphism)
# - Factory Design Pattern
# - Robust error handling
# - Command Line Interface

from abc import ABC, abstractmethod  # Import abstract base class for OOP abstraction
import mysql.connector  # Import MySQL connector library
 
# DATABASE CONNECTION
def get_db_connection():
    return mysql.connector.connect(  # Create connection to MySQL database
        host="localhost",  # Database host
        user="root",  # MySQL username
        password="yourpassword",  # MySQL password (Temp Password for now)
        database="car_rental"  # Database name
    )

 
# USER CLASS
class User:
    def __init__(self, username, role):
        self.username = username  # Store username
        self.role = role  # Store user role (admin/customer)


# CAR CLASSES
class Car(ABC):  # Abstract base class for all cars
    def __init__(self, car_id, brand, model, base_price_per_day, is_rented=False):
        self._car_id = car_id  # Unique ID of car
        self._brand = brand  # Car brand
        self._model = model  # Car model
        self._base_price_per_day = base_price_per_day  # Price per day
        self._is_rented = is_rented  # Rental status

    def get_id(self):
        return self._car_id  # Return car ID

    def is_rented(self):
        return self._is_rented  # Return rental status

    def rent(self):
        if self._is_rented:  # Check if already rented
            raise Exception("Car already rented!")  # Prevent double rent
        self._is_rented = True  # Mark as rented

    def return_car(self):
        if not self._is_rented:  # Check if not rented
            raise Exception("Car is not rented!")  # Prevent invalid return
        self._is_rented = False  # Mark as available

    @abstractmethod
    def calculate_price(self, days):  # Abstract method for price calculation
        pass

    def display(self):
        status = "Rented" if self._is_rented else "Available"  # Determine status
        return f"ID: {self._car_id} | {self._brand} {self._model} | Status: {status}"  # Return formatted string


class EconomyCar(Car):  # Economy car type
    def calculate_price(self, days):
        return self._base_price_per_day * days  # Simple pricing


class LuxuryCar(Car):  # Luxury car type
    def calculate_price(self, days):
        return self._base_price_per_day * days * 1.5  # 50% extra cost


class SUVCar(Car):  # SUV car type
    def calculate_price(self, days):
        return self._base_price_per_day * days * 1.2  # 20% extra cost


# FACTORY PATTERN
class CarFactory:
    @staticmethod
    def create_car(car_type, car_id, brand, model, price, is_rented=False):
        if car_type == "economy":  # Create economy car
            return EconomyCar(car_id, brand, model, price, is_rented)
        elif car_type == "luxury":  # Create luxury car
            return LuxuryCar(car_id, brand, model, price, is_rented)
        elif car_type == "suv":  # Create SUV car
            return SUVCar(car_id, brand, model, price, is_rented)
        else:
            raise ValueError("Invalid car type")  # Handle invalid type
        
# SERVICE LAYER (MYSQL)
class RentalService:
    def __init__(self):
        self.conn = get_db_connection()  # Open DB connection
        self.cursor = self.conn.cursor()  # Create cursor for queries

    def add_car(self, car):
        query = "INSERT INTO cars (id, brand, model, price, is_rented) VALUES (%s,%s,%s,%s,%s)"  # SQL insert
        self.cursor.execute(query, (car._car_id, car._brand, car._model, car._base_price_per_day, car._is_rented))  # Execute query
        self.conn.commit()  # Save changes
        print("Car added successfully")

    def remove_car(self, car_id):
        self.cursor.execute("DELETE FROM cars WHERE id=%s", (car_id,))  # Delete query
        self.conn.commit()  # Save changes
        print("Car removed successfully")

    def list_cars(self):
        self.cursor.execute("SELECT * FROM cars")  # Fetch all cars
        cars = self.cursor.fetchall()  # Get results

        if not cars:  # If no cars
            print("No cars available")
            return

        for (id, brand, model, price, is_rented) in cars:  # Loop through results
            status = "Rented" if is_rented else "Available"  # Determine status
            print(f"ID: {id} | {brand} {model} | Status: {status}")  # Display

    def find_car(self, car_id):
        self.cursor.execute("SELECT * FROM cars WHERE id=%s", (car_id,))  # Search by ID
        return self.cursor.fetchone()  # Return result

    def rent_car(self, car_id, days):
        if days <= 0:  # Validate days
            raise Exception("Invalid number of days")

        car = self.find_car(car_id)  # Get car
        if not car:
            raise Exception("Car not found")

        if car[4]:  # Check if rented
            raise Exception("Car already rented")

        base_cost = car[3] * days  # Calculate base cost

        # Discount logic
        discount = 0
        if days >= 14:
            discount = 0.10
        elif days >= 7:
            discount = 0.05

        discount_amount = base_cost * discount  # Calculate discount
        final_cost = base_cost - discount_amount  # Final price

        self.cursor.execute("UPDATE cars SET is_rented=TRUE WHERE id=%s", (car_id,))  # Update DB
        self.conn.commit()

        print(f"Base Cost: ${base_cost}")
        print(f"Discount: ${discount_amount}")
        print(f"Final Cost: ${final_cost}")

    def return_car(self, car_id):
        self.cursor.execute("UPDATE cars SET is_rented=FALSE WHERE id=%s", (car_id,))  # Update DB
        self.conn.commit()
        print("Car returned successfully")
