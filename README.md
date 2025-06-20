# Django Authentication App

A robust Django authentication app providing JWT-based authentication, email verification, OTP login, token blacklisting, and session management. Built with Django REST Framework.

## Features

- **JWT Authentication**: Secure login with short-lived access and refresh tokens.
- **Email Verification**: Users must verify their email before activating their account.
- **OTP Login**: One-time password (OTP) login via email.
- **Token Blacklisting**: Revoke tokens on logout or refresh.
- **Session Management**: Logout from all devices/sessions.
- **Logging & Signals**: Custom signals for login, token refresh, and secure data access.

## Endpoints

| Endpoint              | Method | Description                                 | Auth Required|
|-----------------------|--------|---------------------------------------------|--------------|
| `/api/register/`      | POST   | Register new user (email verification sent) | No           |
| `/api/verify-email/`  | GET    | Verify email with token                     | No           |
| `/api/login/`         | POST   | Login with username & password (JWT issued) | No           |
| `/api/refresh/`       | POST   | Refresh JWT tokens                          | No           |
| `/api/logout/`        | POST   | Logout (blacklist refresh token)            | Yes          |
| `/api/logout-all/`    | POST   | Logout from all devices                     | Yes          |
| `/api/secure/`        | POST   | Access protected endpoint                   | Yes          |
| `/api/request-otp/`   | POST   | Request OTP for email login                 | No           |
| `/api/verify-otp/`    | POST   | Verify OTP and login                        | No           |

## Models

- [`auth_app.models.BlacklistedToken`](app/auth_app/models.py): Stores blacklisted tokens.
- [`auth_app.models.RefreshSession`](app/auth_app/models.py): Tracks user sessions for refresh/access tokens.
- [`auth_app.models.OTP`](app/auth_app/models.py): Stores OTP codes for users.

## Serializers

- [`auth_app.serializers.RegisterSerializer`](app/auth_app/serializers.py): Handles user registration and password hashing.

## Views

- [`auth_app.views.LoginView`](app/auth_app/views.py): Authenticates user and issues JWT tokens.
- [`auth_app.views.SecureDataView`](app/auth_app/views.py): Example protected endpoint.
- [`auth_app.views.RefreshTokenView`](app/auth_app/views.py): Handles token refresh and blacklisting.
- [`auth_app.views.LogoutView`](app/auth_app/views.py): Blacklists a refresh token.
- [`auth_app.views.LogoutAllDevicesView`](app/auth_app/views.py): Blacklists all tokens for a user.
- [`auth_app.views.RegisterView`](app/auth_app/views.py): Registers a new user and sends verification email.
- [`auth_app.views.VerifyEmailView`](app/auth_app/views.py): Verifies email using a token.
- [`auth_app.views.RequestOTPView`](app/auth_app/views.py): Sends OTP to user's email.
- [`auth_app.views.VerifyOTPView`](app/auth_app/views.py): Verifies OTP and logs in user.

## Signals

- [`auth_app.signals`](app/auth_app/signals.py): Logs login, refresh, and secure data access events.

## Utilities

- [`auth_app.utils`](app/auth_app/utils.py): JWT encode/decode, token generation, email token utilities.

## Admin

- [`auth_app.admin`](app/auth_app/admin.py): Admin interface for blacklisted tokens.

## Setup

1. **Install dependencies**
  
   ```python
   pip install -r requirement.txt
   ```

2. **Configure database**  
   Update `DATABASES` in [`app/app/settings.py`](app/app/settings.py).

3. **Apply migrations**

    ```python
    python manage.py migrate
    ```

4. **Run server**

   ```python
   python manage.py runserver
   ```

5. **Testing email**  
   By default, emails are printed to the console.

## Usage

- Register a user via `/api/register/`
- Verify email via link sent to email
- Login via `/api/login/` or request OTP via `/api/request-otp/`
- Use JWT access token for authenticated endpoints (e.g., `/api/secure/`)

## Security Notes

- Change `SECRET_KEY` and database credentials before deploying to production.
- Set up a real email backend for production.
- Use HTTPS in production.

---

**See code for details:**

- [auth_app/views.py](app/auth_app/views.py)  
- [auth_app/models.py](app/auth_app/models.py)  
- [auth_app/serializers.py](app/auth_app/serializers.py)  
- [auth_app/utils.py](app/auth_app/utils.py)  
- [auth_app/signals.py](app/auth_app/signals.py)  
- [auth_app/admin.py](app/auth_app/admin.py)  
- [auth_app/urls.py](app/auth_app/urls.py)
