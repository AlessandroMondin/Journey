#!/usr/bin/env python
import os
import sys
from datetime import datetime, timedelta, timezone
from jose import jwt

# Read the secret key from .env file or use default
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"


def generate_token(owner_id="test-user-123", expires_delta=None):
    """Generate a test JWT token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": owner_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


if __name__ == "__main__":
    # Use command line argument for owner_id if provided
    owner_id = sys.argv[1] if len(sys.argv) > 1 else "test-user-123"
    token = generate_token(owner_id)
    print(f"JWT Token for {owner_id}:")
    print(token)
