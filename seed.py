from database.database import SessionLocal
from database import models


db = SessionLocal()

cars = [
    {
        "name": "Defender",
        "brand": "Land Rover",
        "price": 8000
    },
    {
        "name": "X5",
        "brand": "BMW",
        "price": 6000
    },
    {
        "name": "C-Class",
        "brand": "Mercedes",
        "price": 5000
    },
    {
        "name": "Q5",
        "brand": "Audi",
        "price": 5500
    },
    {
        "name": "Fortuner",
        "brand": "Toyota",
        "price": 4500
    },
    {
        "name": "XC90",
        "brand": "Volvo",
        "price": 7000
    }
]

for car_data in cars:

    existing_car = db.query(models.Car).filter(
        models.Car.name == car_data["name"],
        models.Car.brand == car_data["brand"]
    ).first()

    if existing_car:
        print(
            f"{car_data['brand']} {car_data['name']} already exists"
        )
    else:
        car = models.Car(
            name=car_data["name"],
            brand=car_data["brand"],
            price=car_data["price"]
        )

        db.add(car)
        print(
            f"Added {car_data['brand']} {car_data['name']}"
        )

db.commit()
db.close()

print("Seed completed!")