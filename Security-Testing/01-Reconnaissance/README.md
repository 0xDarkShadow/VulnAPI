# 01 - API Reconnaissance

## Objective

The objective of this phase was to identify and understand the API attack surface of VulnAPI before performing vulnerability testing.

The reconnaissance focused on discovering API endpoints, HTTP methods, parameters, authentication requirements, and application functionality.

---

## Target

**Application:** VulnAPI  
**Environment:** Local Testing Environment  
**Base URL:** `http://127.0.0.1:8000`

---

## Tools Used

- Burp Suite Professional
- Web Browser
---

## Reconnaissance Methodology

### 1. Application Discovery

The VulnAPI application was browsed normally to understand its available functionality.

The following areas were identified:

- User Registration
- User Login
- Vehicle Listing
- Vehicle Details
- User Profile
- Bookings
- Wallet
- Payments
- Password Reset
- OTP Verification
- Roadside Assistance
- User Dashboard

### 2. HTTP Traffic Analysis

Burp Suite was configured as a proxy while interacting with the application.

The HTTP History was reviewed to identify:

- HTTP methods
- API endpoints
- Path parameters
- Query parameters
- Request headers
- Request bodies
- Response status codes
- Response data

### 3. Endpoint Mapping

The discovered API endpoints were documented in an endpoint inventory.

User-controlled identifiers and authenticated endpoints were also noted for further security testing.

---

## Discovered Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/login` | Authentication |
| GET | `/api/user/` | User information |
| GET | `/api/user/{id}` | User details |
| GET | `/api/wallet/{id}` | Wallet information |
| GET | `/api/users/{id}/bookings` | User bookings |
| GET | `/api/cars/{id}` | Car details |
| GET | `/api/user-dashboard` | User dashboard |
| POST | `/api/contact-mechanic` | Mechanic request |

---

## Key Observation

Several endpoints use user-controlled identifiers:

```text
/api/user/2
/api/wallet/2
/api/users/2/bookings
```
These endpoints were identified for further authorization testing.

Evidence
<img width="1920" height="785" alt="Screenshot 2026-10-02 172553" src="https://github.com/user-attachments/assets/254a3890-70ae-44f6-b1dc-9bf7c38e7824" />

========================================================================================================================================================================================

<img width="1920" height="847" alt="Screenshot 2026-10-02 172431" src="https://github.com/user-attachments/assets/b1d7fff3-0c83-4b08-8285-9c9f8d964b59" />

```
Burp Suite HTTP History was used to identify and analyze API requests generated while interacting with the application.
```
Result

The initial API attack surface was successfully mapped.

The discovered endpoints, parameters, and application functionality were documented for subsequent security testing phases.
