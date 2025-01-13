"""Authentication API examples."""

LOGIN_REQUEST = {
    "email": "john.doe@example.com",
    "password": "securePassword123"
}

LOGIN_RESPONSE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}

PASSWORD_RESET_REQUEST = {
    "email": "john.doe@example.com"
}

PASSWORD_UPDATE_REQUEST = {
    "current_password": "oldPassword123",
    "new_password": "newSecurePassword456"
}

EMAIL_VERIFICATION_SUCCESS = {
    "message": "Email successfully verified"
}

examples = {
    "login": {
        "summary": "Login with email and password",
        "description": "Authenticate a user and return an access token",
        "value": LOGIN_REQUEST
    },
    "login_response": {
        "summary": "Successful login response",
        "description": "Returns a JWT access token for authenticated requests",
        "value": LOGIN_RESPONSE
    },
    "password_reset": {
        "summary": "Request password reset",
        "description": "Send a password reset email to the user",
        "value": PASSWORD_RESET_REQUEST
    },
    "password_update": {
        "summary": "Update user password",
        "description": "Change user's password with current and new password",
        "value": PASSWORD_UPDATE_REQUEST
    },
    "email_verification": {
        "summary": "Email verification success",
        "description": "Response when email is successfully verified",
        "value": EMAIL_VERIFICATION_SUCCESS
    }
}
