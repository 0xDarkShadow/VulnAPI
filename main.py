import random
import urllib.request
import urllib.error
import jwt

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from sqlalchemy import text

from database.database import engine, Base, SessionLocal
from database import models


# ==========================================
# DATABASE
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# DATABASE MIGRATION
# ==========================================

def migrate_database():

    with engine.connect() as connection:

        # --------------------------------------
        # USERS TABLE
        # --------------------------------------

        user_columns = connection.execute(
            text("PRAGMA table_info(users)")
        ).fetchall()

        user_column_names = [
            column[1]
            for column in user_columns
        ]

        # --------------------------------------
        # ADD BALANCE COLUMN
        # --------------------------------------

        if "balance" not in user_column_names:

            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN balance FLOAT DEFAULT 500"
                )
            )

            connection.commit()

        # --------------------------------------
        # ADD ROLE COLUMN
        # --------------------------------------

        if "role" not in user_column_names:

            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN role VARCHAR DEFAULT 'user'"
                )
            )

            connection.commit()

        # --------------------------------------
        # BOOKINGS TABLE
        # --------------------------------------

        booking_columns = connection.execute(
            text("PRAGMA table_info(bookings)")
        ).fetchall()

        booking_column_names = [
            column[1]
            for column in booking_columns
        ]

        # --------------------------------------
        # ADD STATUS COLUMN
        # --------------------------------------

        if "status" not in booking_column_names:

            connection.execute(
                text(
                    "ALTER TABLE bookings "
                    "ADD COLUMN status VARCHAR "
                    "DEFAULT 'Pending Payment'"
                )
            )

            connection.commit()


migrate_database()


# ==========================================
# APP
# ==========================================

app = FastAPI(
    title="VulnAPI"
)


# ==========================================
# LAB RESET ON SERVICE START
# ==========================================

@app.on_event("startup")
def reset_lab_data():

    db = SessionLocal()

    try:

        # --------------------------------------
        # DELETE PAYMENTS
        # --------------------------------------

        db.query(
            models.Payment
        ).delete(
            synchronize_session=False
        )

        # --------------------------------------
        # DELETE BOOKINGS
        # --------------------------------------

        db.query(
            models.Booking
        ).delete(
            synchronize_session=False
        )

        # --------------------------------------
        # RESET USER BALANCE
        # --------------------------------------

        users = db.query(
            models.User
        ).all()

        for user in users:

            user.balance = 500.0

            # Do NOT overwrite an existing role.
            # This is important for the BFLA lab.

            if user.role is None:

                user.role = "user"

        # --------------------------------------
        # DEFAULT USERS
        # --------------------------------------

        default_users = [

            {
                "username": "james",
                "email": "james@example.com",
                "password": "hello willam 123",
                "role": "user"
            },

            {
                "username": "henry",
                "email": "henry@example.com",
                "password": "hello willam 123",
                "role": "user"
            },

            {
                "username": "michael",
                "email": "michael@example.com",
                "password": "hello willam 123",
                "role": "user"
            },

            {
                "username": "william",
                "email": "william@example.com",
                "password": "hello willam 123",
                "role": "user"
            },

            {
                "username": "alex",
                "email": "alex@example.com",
                "password": "hello willam 123",
                "role": "user"
            },

            # ----------------------------------
            # ADMIN
            # ----------------------------------

            {
                "username": "admin",
                "email": "admin@vulnapi.local",
                "password": "admin123",
                "role": "admin"
            }

        ]

        # --------------------------------------
        # CREATE DEFAULT USERS
        # --------------------------------------

        for user_data in default_users:

            existing_user = db.query(
                models.User
            ).filter(
                models.User.username ==
                user_data["username"]
            ).first()

            if not existing_user:

                new_user = models.User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                    balance=500.0,
                    role=user_data["role"]
                )

                db.add(new_user)

            else:

                # Keep existing database role unchanged.
                #
                # This is important for BFLA.
                # The vulnerability is based on trusting
                # X-User-Role, not changing database roles.

                pass

        db.commit()

        print("==========================================")
        print("VulnAPI lab reset completed")
        print("All bookings deleted")
        print("All payments deleted")
        print("All user balances reset to $500")
        print("Default lab users checked/created")
        print("Admin user checked/created")
        print("==========================================")

    except Exception as error:

        db.rollback()

        print(
            "LAB RESET ERROR:",
            error
        )

    finally:

        db.close()


# ==========================================
# CONSTANTS
# ==========================================

# Practice lab exchange rate
# $1 = ₹90

USD_RATE = 90


# ==========================================
# JWT CONFIGURATION
# ==========================================

JWT_SECRET = "vulnapi-secret-key"

JWT_ALGORITHM = "HS256"


# ==========================================
# TEMPORARY OTP STORAGE
# ==========================================

otp_storage = {}

otp_verified = {}


# ==========================================
# FRONTEND
# ==========================================

app.mount(
    "/frontend",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)

# ==========================================
# FRONTEND IMAGES
# ==========================================

app.mount(
    "/images",
    StaticFiles(
        directory="frontend/images"
    ),
    name="images"
)
# ==========================================
# FRONTEND PAGE ROUTES
# ==========================================

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# Clean URL + old URL compatibility
@app.get("/index.html")
def old_home_page():
    return FileResponse("frontend/index.html")


@app.get("/cars")
def cars_page():
    return FileResponse("frontend/cars.html")


@app.get("/cars.html")
def old_cars_page():
    return FileResponse("frontend/cars.html")


@app.get("/car")
def car_page():
    return FileResponse("frontend/car.html")


@app.get("/car.html")
def old_car_page():
    return FileResponse("frontend/car.html")


@app.get("/login")
def login_page():
    return FileResponse("frontend/login.html")


@app.get("/login.html")
def old_login_page():
    return FileResponse("frontend/login.html")


@app.get("/register")
def register_page():
    return FileResponse("frontend/register.html")


@app.get("/register.html")
def old_register_page():
    return FileResponse("frontend/register.html")


@app.get("/booking")
def booking_page():
    return FileResponse("frontend/booking.html")


@app.get("/booking.html")
def old_booking_page():
    return FileResponse("frontend/booking.html")


@app.get("/myprofile")
def profile_page():
    return FileResponse("frontend/profile.html")


@app.get("/profile")
def old_profile_page():
    return FileResponse("frontend/profile.html")


@app.get("/profile.html")
def old_profile_html_page():
    return FileResponse("frontend/profile.html")


@app.get("/user-details")
def user_details_page():
    return FileResponse("frontend/user-details.html")


@app.get("/user-details.html")
def old_user_details_page():
    return FileResponse("frontend/user-details.html")


@app.get("/roadsideassistance")
def contact_mechanic_page():
    return FileResponse("frontend/contact-mechanic.html")


@app.get("/contact-mechanic")
def old_contact_mechanic_page():
    return FileResponse("frontend/contact-mechanic.html")


@app.get("/contact-mechanic.html")
def old_contact_mechanic_html_page():
    return FileResponse("frontend/contact-mechanic.html")

@app.get("/forgotpassword")
def forgot_password_page():
    return FileResponse("frontend/forgot-password.html")


@app.get("/forgot-password")
def old_forgot_password_page():
    return FileResponse("frontend/forgot-password.html")


@app.get("/forgot-password.html")
def old_forgot_password_html_page():
    return FileResponse("frontend/forgot-password.html")

# ==========================================
# CARS
# ==========================================

@app.get("/api/cars")
def get_cars():

    db = SessionLocal()

    try:

        cars = db.query(
            models.Car
        ).all()

        result = []

        for car in cars:

            result.append({

                "id": car.id,
                "name": car.name,
                "brand": car.brand,
                "price": car.price

            })

        return result

    finally:

        db.close()


@app.get("/api/cars/{car_id}")
def get_car(car_id: int):

    db = SessionLocal()

    try:

        car = db.query(
            models.Car
        ).filter(
            models.Car.id == car_id
        ).first()

        if not car:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Car not found"
                }
            )

        return {

            "id": car.id,
            "name": car.name,
            "brand": car.brand,
            "price": car.price

        }

    finally:

        db.close()


# ==========================================
# REGISTER
# ==========================================

@app.post("/api/register")
def register(
    username: str,
    email: str,
    password: str
):

    db = SessionLocal()

    try:

        existing_user = db.query(
            models.User
        ).filter(
            (models.User.username == username) |
            (models.User.email == email)
        ).first()

        if existing_user:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "Username or email already exists"
                }
            )

        # --------------------------------------
        # NEW USERS ARE ALWAYS NORMAL USERS
        # --------------------------------------

        user = models.User(
            username=username,
            email=email,
            password=password,
            balance=500.0,
            role="user"
        )

        db.add(user)

        db.commit()

        db.refresh(user)

        return {

            "success": True,

            "message":
            "User registered successfully",

            "user_id": user.id,

            "username":
            user.username,

            "email":
            user.email,

            "balance":
            500.0,

            "currency":
            "USD"

        }

    finally:

        db.close()


# ==========================================
# LOGIN
# JWT AUTHENTICATION
# ==========================================
#
# JWT is generated after successful login.
#
# The frontend receives the JWT after login
# and stores it for the next authenticated
# request.
#
# The JWT is then sent in:
#
# Authorization: Bearer <JWT>
#
# ==========================================

@app.post("/api/login")
def login(
    username: str,
    password: str
):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.username == username
        ).first()

        # --------------------------------------
        # INVALID USER
        # --------------------------------------

        if not user:

            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message":
                    "Invalid username or password"
                }
            )

        # --------------------------------------
        # INVALID PASSWORD
        # --------------------------------------

        if user.password != password:

            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message":
                    "Invalid username or password"
                }
            )

        # --------------------------------------
        # DEFAULT BALANCE
        # --------------------------------------

        if user.balance is None:

            user.balance = 500.0

            db.commit()

        # ======================================
        # CREATE JWT
        # ======================================
        #
        # iat = issued-at timestamp
        # exp = expiration timestamp
        #
        # These claims make the JWT look like
        # a normal authentication token.
        # ======================================

        import time

        current_time = int(
            time.time()
        )

        token_payload = {

            "user_id":
            user.id,

            "username":
            user.username,

            "role":
            user.role,

            "iat":
            current_time,

            "exp":
            current_time + 3600

        }

        access_token = jwt.encode(

            token_payload,

            JWT_SECRET,

            algorithm=JWT_ALGORITHM

        )

        # ======================================
        # LOGIN RESPONSE
        # ======================================
        #
        # The token is returned so the frontend
        # can store it and send it in the NEXT
        # request.
        #
        # The JWT itself is NOT used as a cookie.
        #
        # ======================================

        return {

            "success":
            True,

            "message":
            "Login successful",

            "user_id":
            user.id,

            "username":
            user.username,

            "role":
            user.role,

            "balance":
            round(
                user.balance,
                2
            ),

            "currency":
            "USD",

            "token_type":
            "Bearer",

            "access_token":
            access_token

        }

    finally:

        db.close()

# ==========================================
# BFLA - USER / ADMIN FUNCTION
# INTENTIONALLY VULNERABLE
# ==========================================

@app.get("/api/user/")
def get_user_function(request: Request):

    db = SessionLocal()

    try:

        user_id = request.headers.get(
            "X-User-ID"
        )

        if not user_id:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "X-User-ID header is required"
                }
            )

        try:

            user_id = int(user_id)

        except (TypeError, ValueError):

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "X-User-ID must be a valid number"
                }
            )

        requested_role = request.headers.get(
            "X-User-Role",
            "user"
        ).lower()

        user = db.query(
            models.User
        ).filter(
            models.User.id == user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        # ======================================
        # NORMAL USER FUNCTION
        # ======================================

        if requested_role == "user":

            return {

                "success":
                True,

                "message":
                "User profile accessed",

                "profile": {

                    "id":
                    user.id,

                    "username":
                    user.username,

                    "email":
                    user.email,

                    "role":
                    "user"

                }

            }

        # ======================================
        # ADMIN FUNCTION
        # ======================================

        if requested_role == "admin":

            admin_user = db.query(
                models.User
            ).filter(
                models.User.role == "admin"
            ).first()

            if not admin_user:

                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "message":
                        "Admin user not found"
                    }
                )

            return {

                "success":
                True,

                "message":
                "Admin function accessed",

                "profile": {

                    "id":
                    admin_user.id,

                    "username":
                    admin_user.username,

                    "email":
                    admin_user.email,

                    "role":
                    "admin"

                },

                "admin_function": {

                    "can_view_all_users":
                    True,

                    "can_view_all_bookings":
                    True

                }

            }

        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "message":
                "Invalid role"
            }
        )

    except Exception as error:

        print(
            "BFLA USER FUNCTION ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message":
                "Unable to load user profile"
            }
        )

    finally:

        db.close()


# ==========================================
# BOLA - USER DETAILS
# INTENTIONALLY VULNERABLE
# ==========================================

@app.get("/api/user/{user_id}")
def get_user(user_id: int):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.id == user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        if user.balance is None:

            user.balance = 500.0

            db.commit()

        return {

            "id":
            user.id,

            "username":
            user.username,

            "email":
            user.email,

            "balance":
            round(
                user.balance,
                2
            ),

            "currency":
            "USD"

        }

    finally:

        db.close()


# ==========================================
# BOPLA - UPDATE USER PROPERTY
# API3
# INTENTIONALLY VULNERABLE
# ==========================================

@app.put("/api/user/{user_id}")
async def update_user_property(
    user_id: int,
    request: Request
):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.id == user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        try:

            data = await request.json()

        except Exception:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "Invalid JSON body"
                }
            )

        if "username" in data:

            user.username = data["username"]

        if "email" in data:

            user.email = data["email"]

        if "balance" in data:

            try:

                user.balance = float(
                    data["balance"]
                )

            except (TypeError, ValueError):

                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message":
                        "Balance must be a valid number"
                    }
                )

        db.commit()

        db.refresh(user)

        return {

            "success":
            True,

            "message":
            "User property updated",

            "user": {

                "id":
                user.id,

                "username":
                user.username,

                "email":
                user.email,

                "balance":
                round(
                    user.balance,
                    2
                ),

                "currency":
                "USD"

            }

        }

    except Exception as error:

        db.rollback()

        print(
            "BOPLA ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message":
                "Unable to update user property"
            }
        )

    finally:

        db.close()


# ==========================================
# WALLET
# ==========================================

@app.get("/api/wallet/{user_id}")
def get_wallet(user_id: int):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.id == user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        if user.balance is None:

            user.balance = 500.0

            db.commit()

        return {

            "success":
            True,

            "user_id":
            user_id,

            "balance":
            round(
                user.balance,
                2
            ),

            "currency":
            "USD"

        }

    finally:

        db.close()


# ==========================================
# CREATE BOOKING
# ==========================================

@app.post("/api/bookings")
def create_booking(
    user_id: int,
    car_id: int,
    days: int,
    total_price: float | None = None
):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.id == user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        if user.balance is None:

            user.balance = 500.0

        car = db.query(
            models.Car
        ).filter(
            models.Car.id == car_id
        ).first()

        if not car:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "Car not found"
                }
            )

        if days <= 0:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "Days must be greater than 0"
                }
            )

        calculated_price = (
            car.price * days
        )

        # ======================================
        # INTENTIONALLY VULNERABLE
        # PRICE MANIPULATION
        # ======================================

        if total_price is None:

            final_price = calculated_price

        else:

            final_price = total_price

        total_usd = round(
            final_price / USD_RATE,
            2
        )

        if user.balance < total_usd:

            return JSONResponse(
                status_code=400,
                content={

                    "success": False,

                    "message":
                    "Insufficient wallet balance",

                    "required":
                    total_usd,

                    "balance":
                    round(
                        user.balance,
                        2
                    ),

                    "currency":
                    "USD"

                }
            )

        booking = models.Booking(

            user_id=user_id,

            car_id=car_id,

            days=days,

            total_price=final_price,

            status="Pending Payment"

        )

        db.add(booking)

        db.commit()

        db.refresh(booking)

        return {

            "success":
            True,

            "message":
            "Booking created successfully",

            "id":
            booking.id,

            "booking_id":
            booking.id,

            "user_id":
            user_id,

            "car_id":
            car_id,

            "days":
            days,

            "total_price":
            final_price,

            "total_usd":
            total_usd,

            "currency":
            "USD",

            "status":
            "Pending Payment"

        }

    except Exception as error:

        db.rollback()

        print(
            "BOOKING ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={

                "success": False,

                "message":
                "Booking creation failed",

                "error":
                str(error)

            }
        )

    finally:

        db.close()


# ==========================================
# GET USER BOOKINGS
# ==========================================

@app.get("/api/users/{user_id}/bookings")
def get_user_bookings(user_id: int):

    db = SessionLocal()

    try:

        bookings = db.query(
            models.Booking
        ).filter(
            models.Booking.user_id == user_id
        ).order_by(
            models.Booking.id.desc()
        ).all()

        result = []

        for booking in bookings:

            total_usd = round(
                booking.total_price /
                USD_RATE,
                2
            )

            result.append({

                "id":
                booking.id,

                "booking_id":
                booking.id,

                "user_id":
                booking.user_id,

                "car_id":
                booking.car_id,

                "days":
                booking.days,

                "total_price":
                booking.total_price,

                "total_usd":
                total_usd,

                "currency":
                "USD",

                "status":
                booking.status or
                "Pending Payment"

            })

        return result

    finally:

        db.close()


# ==========================================
# GET SINGLE USER BOOKING
# ==========================================

@app.get(
    "/api/users/{user_id}/bookings/{booking_id}"
)
def get_single_user_booking(
    user_id: int,
    booking_id: int
):

    db = SessionLocal()

    try:

        booking = db.query(
            models.Booking
        ).filter(
            models.Booking.id == booking_id
        ).first()

        if not booking:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "Booking not found"
                }
            )

        # ======================================
        # INTENTIONALLY VULNERABLE BOLA
        # ======================================

        total_usd = round(
            booking.total_price /
            USD_RATE,
            2
        )

        return {

            "success":
            True,

            "booking": {

                "id":
                booking.id,

                "booking_id":
                booking.id,

                "user_id":
                booking.user_id,

                "car_id":
                booking.car_id,

                "days":
                booking.days,

                "total_price":
                booking.total_price,

                "total_usd":
                total_usd,

                "currency":
                "USD",

                "status":
                booking.status or
                "Pending Payment"

            }

        }

    finally:

        db.close()


# ==========================================
# POST USER BOOKING STATUS
# ==========================================

@app.post(
    "/api/users/{user_id}/bookings"
)
async def post_user_booking_status(
    user_id: int,
    request: Request
):

    db = SessionLocal()

    try:

        data = await request.json()

        booking_id = data.get(
            "booking_id"
        )

        status = data.get(
            "status"
        )

        if booking_id is None:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "booking_id is required"
                }
            )

        if not status:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "status is required"
                }
            )

        booking = db.query(
            models.Booking
        ).filter(
            models.Booking.id ==
            int(booking_id)
        ).first()

        if not booking:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "Booking not found"
                }
            )

        # ======================================
        # INTENTIONALLY VULNERABLE BOLA
        # ======================================

        booking.status = status

        db.commit()

        db.refresh(booking)

        total_usd = round(
            booking.total_price /
            USD_RATE,
            2
        )

        return {

            "success":
            True,

            "message":
            "Booking status updated",

            "booking": {

                "id":
                booking.id,

                "booking_id":
                booking.id,

                "user_id":
                booking.user_id,

                "car_id":
                booking.car_id,

                "days":
                booking.days,

                "total_price":
                booking.total_price,

                "total_usd":
                total_usd,

                "currency":
                "USD",

                "status":
                booking.status

            }

        }

    finally:

        db.close()


# ==========================================
# PAYMENT
# ==========================================

@app.post("/api/payments")
def create_payment(
    booking_id: int,
    user_id: int
):

    db = SessionLocal()

    try:

        booking = db.query(
            models.Booking
        ).filter(
            models.Booking.id ==
            booking_id
        ).first()

        if not booking:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "Booking not found"
                }
            )

        # --------------------------------------
        # AUTHORIZATION
        # --------------------------------------

        if booking.user_id != user_id:

            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message":
                    "Unauthorized"
                }
            )

        if booking.status == "Cancelled":

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "Booking is cancelled"
                }
            )

        user = db.query(
            models.User
        ).filter(
            models.User.id == user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        if user.balance is None:

            user.balance = 500.0

        existing_payment = db.query(
            models.Payment
        ).filter(

            models.Payment.booking_id ==
            booking.id,

            models.Payment.user_id ==
            user_id,

            models.Payment.status ==
            "Successful"

        ).first()

        if existing_payment:

            booking.status = (
                "Payment Successful"
            )

            db.commit()

            return {

                "success":
                True,

                "message":
                "Payment already completed",

                "payment_id":
                existing_payment.id,

                "booking_id":
                booking.id,

                "amount_usd":
                round(
                    existing_payment.amount,
                    2
                ),

                "currency":
                "USD",

                "status":
                "Payment Successful",

                "remaining_balance":
                round(
                    user.balance,
                    2
                )

            }

        amount_usd = round(
            booking.total_price /
            USD_RATE,
            2
        )

        if user.balance < amount_usd:

            return JSONResponse(
                status_code=400,
                content={

                    "success": False,

                    "message":
                    "Insufficient wallet balance",

                    "required":
                    amount_usd,

                    "balance":
                    round(
                        user.balance,
                        2
                    ),

                    "currency":
                    "USD"

                }
            )

        user.balance = round(
            user.balance - amount_usd,
            2
        )

        payment = models.Payment(

            booking_id=booking.id,

            user_id=user_id,

            amount=amount_usd,

            status="Successful"

        )

        db.add(payment)

        booking.status = (
            "Payment Successful"
        )

        db.commit()

        db.refresh(payment)

        remaining_balance = round(
            user.balance,
            2
        )

        return {

            "success":
            True,

            "message":
            "Payment successful",

            "payment_id":
            payment.id,

            "booking_id":
            booking.id,

            "amount_inr":
            booking.total_price,

            "amount_usd":
            amount_usd,

            "currency":
            "USD",

            "status":
            "Payment Successful",

            "remaining_balance":
            remaining_balance

        }

    except Exception as error:

        db.rollback()

        print(
            "PAYMENT ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={

                "success": False,

                "message":
                "Payment processing failed",

                "error":
                str(error)

            }
        )

    finally:

        db.close()


# ==========================================
# VULNERABLE PAYMENT PRICE UPDATE
# API6 - SENSITIVE BUSINESS FLOW
# ==========================================

@app.put("/api/payments")
async def update_payment_amount(
    booking_id: int,
    request: Request
):

    db = SessionLocal()

    try:

        data = await request.json()

        amount_usd = data.get(
            "amount_usd"
        )

        if amount_usd is None:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "amount_usd is required"
                }
            )

        try:

            amount_usd = float(
                amount_usd
            )

        except (TypeError, ValueError):

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "amount_usd must be a valid number"
                }
            )

        booking = db.query(
            models.Booking
        ).filter(
            models.Booking.id ==
            booking_id
        ).first()

        if not booking:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "Booking not found"
                }
            )

        user = db.query(
            models.User
        ).filter(
            models.User.id ==
            booking.user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        wallet_before = round(
            user.balance,
            2
        )

        # ======================================
        # INTENTIONALLY VULNERABLE
        # BUSINESS LOGIC
        # ======================================

        if amount_usd < 0:

            wallet_change = abs(
                amount_usd
            )

        else:

            wallet_change = -amount_usd

        user.balance = round(
            user.balance +
            wallet_change,
            2
        )

        booking.total_price = round(
            amount_usd * USD_RATE,
            2
        )

        payment = db.query(
            models.Payment
        ).filter(

            models.Payment.booking_id ==
            booking.id,

            models.Payment.user_id ==
            booking.user_id

        ).order_by(
            models.Payment.id.desc()
        ).first()

        if payment:

            payment.amount = round(
                amount_usd,
                2
            )

        db.commit()

        db.refresh(user)

        db.refresh(booking)

        if payment:

            db.refresh(payment)

        return {

            "success":
            True,

            "message":
            "Payment amount updated",

            "booking_id":
            booking.id,

            "amount_usd":
            round(
                amount_usd,
                2
            ),

            "total_price":
            round(
                booking.total_price,
                2
            ),

            "wallet_before":
            wallet_before,

            "wallet_change":
            round(
                wallet_change,
                2
            ),

            "wallet_balance":
            round(
                user.balance,
                2
            ),

            "currency":
            "USD",

            "status":
            booking.status

        }

    except Exception as error:

        db.rollback()

        print(
            "PAYMENT UPDATE ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message":
                "Payment amount update failed",
                "error":
                str(error)
            }
        )

    finally:

        db.close()


# ==========================================
# CANCEL BOOKING
# ==========================================

@app.post(
    "/api/bookings/{booking_id}/cancel"
)
async def cancel_booking(
    booking_id: int,
    request: Request
):

    db = SessionLocal()

    try:

        try:

            data = await request.json()

        except Exception:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "Invalid JSON body"
                }
            )

        booking = db.query(
            models.Booking
        ).filter(
            models.Booking.id ==
            booking_id
        ).first()

        if not booking:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "Booking not found"
                }
            )

        requested_status = data.get(
            "status"
        )

        if requested_status != "Cancelled":

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "Invalid booking status"
                }
            )

        user = db.query(
            models.User
        ).filter(
            models.User.id ==
            booking.user_id
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        payment = db.query(
            models.Payment
        ).filter(

            models.Payment.booking_id ==
            booking.id,

            models.Payment.user_id ==
            booking.user_id,

            models.Payment.status ==
            "Successful"

        ).first()

        booking.status = "Cancelled"

        if payment:

            refund_amount = payment.amount

            user.balance = round(
                user.balance +
                refund_amount,
                2
            )

            payment.status = "Refunded"

            message = (
                "Booking cancelled and "
                "payment refunded successfully"
            )

        else:

            message = (
                "Booking cancelled successfully. "
                "No successful payment found."
            )

        db.commit()

        db.refresh(booking)

        if payment:

            db.refresh(payment)

        db.refresh(user)

        return {

            "success":
            True,

            "message":
            message,

            "booking": {

                "id":
                booking.id,

                "user_id":
                booking.user_id,

                "car_id":
                booking.car_id,

                "days":
                booking.days,

                "total_price":
                booking.total_price,

                "status":
                booking.status

            },

            "payment": {

                "payment_id":
                payment.id
                if payment
                else None,

                "amount":
                payment.amount
                if payment
                else 0,

                "status":
                payment.status
                if payment
                else "No Payment"

            },

            "wallet": {

                "balance":
                round(
                    user.balance,
                    2
                ),

                "currency":
                "USD"

            }

        }

    except Exception as error:

        db.rollback()

        print(
            "CANCEL BOOKING ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message":
                "Unable to cancel booking"
            }
        )

    finally:

        db.close()


# ==========================================
# PAYMENTS HISTORY
# ==========================================

@app.get("/api/payments/{user_id}")
def get_user_payments(user_id: int):

    db = SessionLocal()

    try:

        payments = db.query(
            models.Payment
        ).filter(
            models.Payment.user_id ==
            user_id
        ).all()

        result = []

        for payment in payments:

            result.append({

                "payment_id":
                payment.id,

                "booking_id":
                payment.booking_id,

                "user_id":
                payment.user_id,

                "amount":
                payment.amount,

                "amount_usd":
                payment.amount,

                "currency":
                "USD",

                "status":
                payment.status

            })

        return result

    finally:

        db.close()


# ==========================================
# FORGOT PASSWORD - OTP
# ==========================================

@app.post("/api/forgot-password")
def forgot_password(
    username: str
):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.username ==
            username
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "message":
                    "User not found",
                    "success":
                    False
                }
            )

        otp = str(
            random.randint(
                1000,
                9999
            )
        )

        otp_storage[user.id] = otp

        return {

            "message":
            "OTP generated successfully",

            "success":
            True

        }

    finally:

        db.close()


# ==========================================
# VERIFY OTP
# ==========================================

@app.post("/api/verify-otp")
def verify_otp(
    username: str,
    otp: str
):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.username ==
            username
        ).first()

        if not user:

            return JSONResponse(
                status_code=400,
                content={
                    "message":
                    "Invalid username",
                    "success":
                    False
                }
            )

        stored_otp = otp_storage.get(
            user.id
        )

        if stored_otp == otp:

            otp_verified[user.id] = True

            return RedirectResponse(
                url=
                "/frontend/forgot-password.html",
                status_code=302
            )

        return JSONResponse(
            status_code=200,
            content={
                "message":
                "Invalid OTP",
                "success":
                False
            }
        )

    except Exception as error:

        db.rollback()

        print(
            "VERIFY OTP ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "message":
                "OTP verification failed",
                "success":
                False
            }
        )

    finally:

        db.close()


# ==========================================
# OTP STATUS
# ==========================================

@app.get("/api/otp-status")
def otp_status(
    username: str
):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.username ==
            username
        ).first()

        if not user:

            return {
                "verified":
                False
            }

        return {

            "verified":
            bool(
                otp_verified.get(
                    user.id
                )
            )

        }

    except Exception as error:

        print(
            "OTP STATUS ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "verified":
                False,
                "message":
                "Unable to check OTP status"
            }
        )

    finally:

        db.close()


# ==========================================
# RESET PASSWORD
# ==========================================

@app.post("/api/reset-password")
def reset_password(
    username: str,
    new_password: str
):

    db = SessionLocal()

    try:

        user = db.query(
            models.User
        ).filter(
            models.User.username ==
            username
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        if not otp_verified.get(
            user.id
        ):

            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message":
                    "OTP verification required"
                }
            )

        user.password = new_password

        otp_verified.pop(
            user.id,
            None
        )

        db.commit()

        return {

            "success":
            True,

            "message":
            "Password reset successful",

            "username":
            user.username

        }

    except Exception as error:

        db.rollback()

        print(
            "RESET PASSWORD ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message":
                "Password reset failed"
            }
        )

    finally:

        db.close()


# ==========================================
# CONTACT MECHANIC
# API7 - SSRF
# INTENTIONALLY VULNERABLE
# ==========================================

@app.post("/api/contact-mechanic")
async def contact_mechanic(request: Request):

    try:

        data = await request.json()

        target_url = data.get(
            "url"
        )

        if not target_url:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message":
                    "Mechanic service URL is required"
                }
            )

        # ======================================
        # NORMAL LAB REQUEST
        # ======================================

        if target_url == "http://127.0.0.1:8000":

            return {

                "success":
                True,

                "message":
                "Mechanic service contacted successfully",

                "request_url":
                target_url,

                "status_code":
                200

            }

        # ======================================
        # INTENTIONALLY VULNERABLE SSRF
        # ======================================

        try:

            req = urllib.request.Request(

                target_url,

                headers={
                    "User-Agent":
                    "VulnAPI-Mechanic-Service"
                }

            )

            with urllib.request.urlopen(
                req,
                timeout=8
            ) as response:

                response_body = response.read(
                    5000
                ).decode(
                    "utf-8",
                    errors="replace"
                )

                return {

                    "success":
                    True,

                    "message":
                    "Mechanic service contacted successfully",

                    "request_url":
                    target_url,

                    "status_code":
                    response.status,

                    "response":
                    response_body

                }

        except Exception as error:

            return JSONResponse(
                status_code=500,
                content={

                    "success":
                    False,

                    "message":
                    "Mechanic service request failed",

                    "request_url":
                    target_url,

                    "error_type":
                    type(error).__name__,

                    "error_details":
                    str(error)

                }
            )

    except Exception as error:

        return JSONResponse(
            status_code=400,
            content={

                "success":
                False,

                "message":
                "Invalid request",

                "error_type":
                type(error).__name__,

                "error_details":
                str(error)

            }
        )


# ==========================================
# DEBUG INFORMATION
# API8 - SECURITY MISCONFIGURATION
# INTENTIONALLY VULNERABLE
# ==========================================

@app.get("/api/debug")
def debug_information():

    return {

        "success":
        True,

        "debug":
        True,

        "environment":
        "development",

        "server":
        "uvicorn",

        "database":
        "SQLite",

        "database_file":
        "vulnapi.db",

        "application":
        "VulnAPI",

        "api_version":
        "1.0"

    }


# ==========================================
# JWT PROFILE
# API2 - BROKEN AUTHENTICATION
# INTENTIONALLY VULNERABLE
# ==========================================
#
# The endpoint accepts JWT from:
#
# 1. Authorization header
# 2. access_token cookie
#
# Normal:
#
# Authorization: Bearer <JWT>
#
# OR:
#
# Cookie: access_token=<JWT>
#
# For the lab, alg:none is intentionally
# accepted without signature verification.
#
# ==========================================
# USER DASHBOARD
# API2 - BROKEN AUTHENTICATION
# INTENTIONALLY VULNERABLE JWT LAB
# ==========================================
#
# Normal request:
#
# GET /api/user-dashboard
# Authorization: Bearer <JWT>
#
# The endpoint intentionally accepts:
#
# alg = none
#
# without verifying the JWT signature.
#
# This is for the local VulnAPI JWT lab.
#
# ==========================================

@app.get("/api/user-dashboard")
def user_dashboard(request: Request):

    # ======================================
    # GET AUTHORIZATION HEADER
    # ======================================

    authorization = request.headers.get(
        "Authorization"
    )

    if not authorization:

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message":
                "Authorization header is required"
            }
        )

    # ======================================
    # CHECK BEARER FORMAT
    # ======================================

    if not authorization.startswith(
        "Bearer "
    ):

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message":
                "Bearer token is required"
            }
        )

    token = authorization.split(
        " ",
        1
    )[1]

    if not token:

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message":
                "JWT token is required"
            }
        )

    db = SessionLocal()

    try:

        # ==================================
        # READ JWT HEADER
        # ==================================

        unverified_header = (
            jwt.get_unverified_header(
                token
            )
        )

        algorithm = (
            unverified_header.get(
                "alg"
            )
        )

        # ==================================
        # INTENTIONALLY VULNERABLE
        #
        # alg:none
        #
        # Signature verification disabled.
        # ==================================

        if algorithm == "none":

            payload = jwt.decode(

                token,

                options={
                    "verify_signature":
                    False
                }

            )

        else:

            # ==================================
            # NORMAL JWT VALIDATION
            # ==================================

            payload = jwt.decode(

                token,

                JWT_SECRET,

                algorithms=[
                    JWT_ALGORITHM
                ]

            )

        # ==================================
        # GET USER ID FROM JWT
        # ==================================

        user_id = payload.get(
            "user_id"
        )

        if user_id is None:

            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message":
                    "user_id claim is missing"
                }
            )

        # ==================================
        # GET ACTUAL USER FROM DATABASE
        # ==================================

        user = db.query(
            models.User
        ).filter(
            models.User.id == int(user_id)
        ).first()

        if not user:

            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message":
                    "User not found"
                }
            )

        # ==================================
        # RETURN ACTUAL USER DATA
        # ==================================

        return {

            "success":
            True,

            "message":
            "User dashboard accessed successfully",

            "user": {

                "id":
                user.id,

                "username":
                user.username,

                "email":
                user.email,

                "role":
                user.role,

                "balance":
                round(
                    user.balance,
                    2
                ),

                "currency":
                "USD"

            }

        }

    # ======================================
    # EXPIRED JWT
    # ======================================

    except jwt.ExpiredSignatureError:

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message":
                "JWT token has expired"
            }
        )

    # ======================================
    # INVALID JWT
    # ======================================

    except jwt.InvalidTokenError as error:

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message":
                "Invalid JWT token",
                "error":
                str(error)
            }
        )

    # ======================================
    # OTHER ERROR
    # ======================================

    except Exception as error:

        print(
            "JWT DASHBOARD ERROR:",
            error
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message":
                "JWT authentication failed"
            }
        )

    finally:

        db.close()