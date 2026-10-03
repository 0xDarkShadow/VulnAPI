# 02 - Broken Authentication

## Objective

The objective of this test was to determine whether the authentication and password-reset mechanisms of VulnAPI could be abused through repeated OTP verification attempts.

## Target

**Application:** VulnAPI
**Environment:** Local Testing Environment
**Base URL:** `http://127.0.0.1:8000`

## Tools Used

* Burp Suite Professional
* Web Browser
* Burp Suite Intruder

## What is Broken Authentication?

**Broken Authentication** is an API vulnerability that occurs when authentication mechanisms are incorrectly implemented or insecurely configured, allowing an attacker to bypass or abuse authentication controls and potentially gain unauthorized access to a victim's account.

## Why Does Broken Authentication Occur?

Broken Authentication can occur because of:

* Missing or insufficient rate limiting.
* No restriction on repeated OTP verification attempts.
* Weak password-reset verification.
* Weak password policies or vulnerable login mechanisms.
* Improper handling of authentication tokens or sessions.

In this test, the focus was on OTP brute-force protection during the password-reset process.

---

## Target Endpoints

| Method | Endpoint               | Purpose                                                   |
| ------ | ---------------------- | --------------------------------------------------------- |
| POST   | `/api/forgot-password` | Initiates the password-reset process and generates an OTP |
| POST   | `/api/verify-otp`      | Verifies the OTP supplied by the user                     |

The exact parameters were observed in Burp Suite HTTP History.

---

## Testing Methodology

### Step 1 - Open the Forgot Password Page

- The forgot-password page was opened in the browser.
- The username `hello42` was entered, and the **Generate OTP** button was clicked.

The application displayed the message:

`OTP generated successfully.`

This confirmed that the password-reset flow had been initiated.

**Evidence:** <img width="988" height="733" alt="Screenshot 2026-10-02 234200" src="https://github.com/user-attachments/assets/42fbf0fd-7e29-4051-988a-36cbb1f8cfdf" />

### Step 2 - Capture the OTP Verification Request

- The OTP verification request was captured using Burp Suite.
- The request contained the username and a user-supplied OTP value.
request:

```http
POST /api/verify-otp?username=hello42&otp=1245 HTTP/1.1
Host: 127.0.0.1:8000
```

The submitted OTP was `1245`, and the server returned:

```json
{
    "message": "Invalid OTP",
    "success": false
}
```

This indicated that the submitted OTP was incorrect.

**Evidence:** <img width="928" height="460" alt="Screenshot 2026-10-02 234248" src="https://github.com/user-attachments/assets/ecd7791e-2ba0-4678-b105-4ddbd4c62b09" />

### Step 3 - Configure Burp Suite Intruder

- The OTP verification request was sent to Burp Suite Intruder.
- The `otp` parameter was selected as the payload position.
- A numeric payload range from `0000` to `9999` was configured to test the four-digit OTP space.
- The attack was run against the local VulnAPI lab to assess whether repeated OTP guesses were restricted.

**Evidence:** <img width="1920" height="967" alt="Screenshot 2026-10-02 234334" src="https://github.com/user-attachments/assets/6d71c3f2-22c2-42bd-84eb-b747a592ee8f" />

### Step 4 - Analyze the Intruder Results

- The Intruder results showed multiple requests receiving responses from the application.
- The results were reviewed to identify differences in response status, response length, and response behavior that could indicate a valid OTP.
- The screenshot shows a request using OTP `4117` receiving an HTTP `302 Found` response and a redirect to:

```text
/frontend/forgot-password
```

- This response differed from the ordinary `Invalid OTP` JSON response.
- This difference was treated as an indication requiring validation against the application's normal OTP-verification behavior.

**Evidence:** <img width="1874" height="1080" alt="Screenshot 2026-10-02 234419" src="https://github.com/user-attachments/assets/41e6ed70-c81d-4ba8-930a-5474de674e14" />


### Step 5 - Verify the OTP and Continue the Reset Flow

- The candidate OTP `4117` was submitted through the OTP verification interface.
  
- **Evidence:** <img width="1556" height="850" alt="Screenshot 2026-10-02 234442" src="https://github.com/user-attachments/assets/25416aa1-e2fe-477c-9cfa-a02d259d1d0b" />

- The application then displayed the **Reset Password** form, allowing a new password and confirmation to be entered.
- 
  <img width="1339" height="875" alt="Screenshot 2026-10-02 234452" src="https://github.com/user-attachments/assets/1ca1a7ef-4a4d-4214-9562-a47a7f56274d" />
  
- This demonstrated that the candidate OTP was accepted by the application's password-reset flow.
 - After successful verification, the user could proceed to the password-reset step.
---
**Observation:**

The OTP verification mechanism accepted repeated verification requests. During testing, a four-digit OTP candidate was identified through Intruder response analysis, and the application proceeded to the Reset Password form after the candidate was submitted.
This indicates that the OTP verification flow may lack sufficient controls against repeated guessing.
The finding should be confirmed by checking whether the endpoint enforces attempt limits, temporary lockouts, OTP expiration, and single-use verification.

**Result:** OTP brute-force protection requires further validation and remediation.

---

## Impact

If an attacker can repeatedly guess OTP values without effective restrictions, they may be able to:

* Discover a valid password-reset OTP.
* Pass the OTP verification step for a targeted account.
* Reach the password-reset stage without being the legitimate account owner.
* Potentially take over an account if the remaining password-reset controls also fail to prevent unauthorized resets.

The final impact depends on whether the OTP is correctly bound to the intended account and reset session, expires appropriately, and can only be used once.

---

## Remediation

### 1. Implement Rate Limiting
Limit the number of OTP verification attempts allowed for an account and within a defined time window.

### 2. Add Temporary Lockouts or Progressive Delays
Temporarily block or delay further attempts after repeated invalid OTP submissions.

### 3. Use Cryptographically Secure OTPs
Generate unpredictable OTPs using a secure random number generator.

### 4. Enforce OTP Expiration
Make OTPs valid only for a short period and reject expired values.

### 5. Enforce Single-Use OTPs
Invalidate the OTP immediately after successful verification.

### 6. Log and Monitor Failed Attempts
Record repeated OTP failures and detect suspicious guessing patterns without logging the OTP itself.

---

## Conclusion

- The VulnAPI password-reset flow was tested for OTP brute-force weaknesses using Burp Suite and Intruder.
- The test identified a candidate OTP associated with a different response, and the application proceeded to the Reset Password form after the candidate was submitted.
- Further validation of attempt restrictions, OTP expiration, and reset-session binding is necessary to establish the complete security impact.

The results and supporting screenshots are documented as part of the VulnAPI API security testing project.
