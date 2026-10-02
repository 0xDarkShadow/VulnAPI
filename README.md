# VulnAPI

VulnAPI is a deliberately vulnerable car-rental API lab created for learning and practicing API security testing.

## Purpose

VulnAPI is designed to help security learners understand common API vulnerabilities by testing them in a controlled local environment using tools such as Burp Suite.

## Technologies

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript
- Burp Suite

## Architecture

```text
Browser
   ↓
Frontend (HTML/CSS/JavaScript)
   ↓
HTTP API Requests
   ↓
FastAPI
   ↓
SQLAlchemy
   ↓
SQLite
```
Burp Suite can be placed between the browser and API during security testing to intercept and modify HTTP requests.

## Features

- User registration and login
- Car listing
- Car details
- Car booking
- Payment functionality
- User profile
- Wallet
- Password reset / OTP flow
- Roadside assistance

## Security Testing Scenarios

The application contains intentionally vulnerable scenarios for educational API security testing, including:

- BOLA
- BFLA
- BOPLA
- SSRF
- JWT security issues
- Parameter tampering
- Business logic vulnerabilities
- OTP brute-force / missing rate limiting

## Testing Tools
- Burp Suite
- Browser Developer Tools
- Swagger UI

## Running the Project

Install the required dependencies:
```
pip install -r requirements.txt
```
Start the FastAPI application:
```
uvicorn main:app --reload
```
Open the application:
```
http://127.0.0.1:8000
```
Swagger API documentation:
```
http://127.0.0.1:8000/docs

```
## Security Testing

The project is intended to be tested locally with Burp Suite.

Example testing areas:

- BOLA
- BFLA
- BOPLA
- SSRF
- JWT
- Parameter Tampering
- Business Logic
- OTP Rate Limiting

## Disclaimer

VulnAPI is intentionally vulnerable and is created only for educational and authorized security-testing purposes.

Do not deploy this application to a public production environment.

Author

Anshika

GitHub: https://github.com/0xDarkShadow