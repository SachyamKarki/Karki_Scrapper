#!/usr/bin/env python3
"""
Reset a user's password. Run from backend/ directory.
Usage: python scripts/reset_password.py <email> <new_password>
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from werkzeug.security import generate_password_hash
from app.database import get_users_collection

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/reset_password.py <email> <new_password>")
        sys.exit(1)

    email = sys.argv[1]
    new_password = sys.argv[2]

    users = get_users_collection()
    result = users.update_one(
        {'email': email},
        {'$set': {'password_hash': generate_password_hash(new_password)}}
    )

    if result.matched_count == 0:
        print(f"User {email} not found.")
        sys.exit(1)

    print(f"Password reset for {email}")

if __name__ == '__main__':
    main()
