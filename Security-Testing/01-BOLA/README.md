# 01 - Broken Object Level Authorization (BOLA)

## Objective

The objective of this test was to identify whether an authenticated user could access another user's object by modifying the object identifier in an API request.

Target

Application: VulnAPI
Environment: Local Testing Environment
Base URL: http://127.0.0.1:8000

Tools Used
Burp Suite Professional
Web Browser

## What is BOLA?

**Broken Object Level Authorization (BOLA)** is an API vulnerability that occurs when an authenticated user can access another user's object or resource by modifying its identifier because the server fails to properly enforce object-level authorization.

## Why Does BOLA Occur?

BOLA usually occurs when an API directly uses a user-controlled object identifier to retrieve data without checking object ownership or access permissions.

For example:
```
@app.get("/api/user/{user_id}")
def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user
```
The API takes the user_id directly from the request and searches the database.


The problem is that the server does not verify whether the currently authenticated user is actually allowed to access User 3's object.
This missing authorization check can result in BOLA.

Target Endpoint
```
GET /api/user/{user_id}
```
The endpoint uses a user-controlled object identifier.

## Testing Methodology

## Step 1 - Authenticate as a user

Logged into VulnAPI as:

Username: hello42
User ID: 2

<img width="1557" height="867" alt="Screenshot 2026-10-02 194021" src="https://github.com/user-attachments/assets/ec9af5a8-4138-48b7-8f7a-b297a86600e9" />


The authenticated user's profile was accessible through:
```
/api/user/2
```
## Step 2 - Capture the API Request

The corresponding API request was identified in Burp Suite:

GET /api/user/2

<img width="1381" height="338" alt="Screenshot 2026-10-02 192230" src="https://github.com/user-attachments/assets/29990a48-f1d5-4dcb-b050-ff133303578a" />

The response contained the authenticated user's information.

```
{
    "id": 2,
    "username": "hello42",
    "email": "hell@gmail.com",
    "balance": 411.11,
    "currency": "USD"
}
```
## Step 3 - Modify the Object Identifier

The user_id value was changed from:
```
2
to:
3
```
Modified request:

GET /api/user/3

The rest of the request remained unchanged.

## Step 4 - Analyze the Response

The API returned information belonging to User 3.

<img width="1415" height="344" alt="Screenshot 2026-10-02 192244" src="https://github.com/user-attachments/assets/9f7d6c6e-5a59-4fde-b733-75f798003a01" />

```
{
    "id": 3,
    "username": "hell1",
    "email": "hell1@gmail.com",
    "balance": 500.0,
    "currency": "USD"
}
```
The authenticated user was hello42 (User ID 2), but the API returned the object belonging to User ID 3.
This demonstrates that the API did not properly enforce object-level authorization.

Finding
```
BOLA confirmed

The API allows an authenticated user to access another user's object by modifying the user_id value.

The test demonstrated the following:

Authenticated User
        |
        v
hello42 (User ID 2)
        |
        | GET /api/user/3
        v
VulnAPI
        |
        | Missing object-level authorization check
        v
User 3 data returned
```
## Impact

An attacker who knows or can enumerate valid user IDs may be able to access other users' information.
Depending on the affected endpoint and available operations, BOLA can potentially lead to:

- Unauthorized access to user information
- Exposure of personal data
- Unauthorized access to bookings or wallet information
- Unauthorized modification or deletion of objects
  
## Remediation

- The server should perform an object-level authorization check before returning or modifying any object.

- The application should verify that the authenticated user has permission to access the requested object.

For example, instead of only checking:
```
user = db.query(User).filter(User.id == user_id).first()
```
- the application should verify the relationship between the authenticated user and the requested object before returning it.

- Authorization checks should be implemented server-side and should not rely on the client-controlled user_id.
