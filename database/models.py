from sqlalchemy import Column, Integer, String, Float
from database.database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    price = Column(Float)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    # Every new user gets $500
    balance = Column(Float, default=500.0)

    # User role for BFLA testing
    # Normal users = user
    # Admin users = admin
    role = Column(String, default="user")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    car_id = Column(Integer)
    days = Column(Integer)
    total_price = Column(Float)

    # Pending Payment / Payment Successful / Cancelled
    status = Column(
        String,
        default="Pending Payment"
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer)
    user_id = Column(Integer)
    amount = Column(Float)
    status = Column(String)