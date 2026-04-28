# Car Rental System (CUI Version)
# Features:
# - OOP (Encapsulation, Inheritance, Polymorphism)
# - Factory Design Pattern
# - Robust error handling
# - Command Line Interface

from abc import ABC, abstractmethod  # Import Abstract Base Class tools


# =========================
class SUVCar(Car):  # SUV car type
    def calculate_price(self, days):  # Pricing logic for SUV cars
        return self._base_price_per_day * days * 1.2  # 20% extra cost


# =========================
# FACTORY PATTERN
# =========================
class CarFactory:  # Factory class to create car objects
    @staticmethod
    def create_car(car_type, car_id, brand, model, price):  # Create car based on type
        if car_type == "economy":  # If economy type selected
            return EconomyCar(car_id, brand, model, price)  # Create EconomyCar object
        elif car_type == "luxury":  # If luxury type selected
            return LuxuryCar(car_id, brand, model, price)  # Create LuxuryCar object
        elif car_type == "suv":  # If SUV type selected
            return SUVCar(car_id, brand, model, price)  # Create SUVCar object
        else:
            raise ValueError("Invalid car type")  # Handle invalid input


# =========================
# SERVICE LAYER
# =========================
class RentalService:  # Handles all business logic
    def __init__(self):
        self.cars = []  # List to store all cars

    def add_car(self, car):  # Add new car to system
        self.cars.append(car)  # Append car object to list

    def remove_car(self, car_id):  # Remove car by ID
        car = self.find_car(car_id)  # Search for car
        if car:  # If car exists
            self.cars.remove(car)  # Remove from list
        else:
            raise Exception("Car not found")  # Error if missing

    def list_cars(self):  # Display all cars
        for car in self.cars:  # Loop through cars
            print(car.display())  # Print car details

    def find_car(self, car_id):  # Find car by ID
        for car in self.cars:  # Loop through list
            if car.get_id() == car_id:  # Match ID
                return car  # Return found car
        return None  # If not found

    def rent_car(self, car_id, days):  # Rent a car
        car = self.find_car(car_id)  # Find car first
        if not car:  # If not found
            raise Exception("Car not found")  # Error message
        car.rent()  # Mark as rented
        return car.calculate_price(days)  # Return rental cost

    def return_car(self, car_id):  # Return rented car
        car = self.find_car(car_id)  # Find car
        if not car:  # If missing
            raise Exception("Car not found")  # Error message
        car.return_car()  # Mark as available
