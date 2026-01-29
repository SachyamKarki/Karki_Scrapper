#!/usr/bin/env python3
"""
Create an initial admin user. Run from backend/ directory.
Usage: python scripts/create_admin.py [email] [password]
Or set ADMIN_EMAIL and ADMIN_PASSWORD in .env
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.models import User

def main():
    email = sys.argv[1] if len(sys.argv) > 1 else os.getenv('ADMIN_EMAIL')
    password = sys.argv[2] if len(sys.argv) > 2 else os.getenv('ADMIN_PASSWORD')

    if not email or not password:
        print("Usage: python scripts/create_admin.py <email> <password>")
        print("Or set ADMIN_EMAIL and ADMIN_PASSWORD in .env")
        sys.exit(1)

    existing = User.get_by_email(email)
    if existing:
        print(f"User {email} already exists. Use update_role to make them admin.")
        sys.exit(1)

    user = User.create(email, password, role='superadmin')
    if user:
        print(f"Admin created: {email} (superadmin)")
    else:
        print("Failed to create admin.")
        sys.exit(1)

if __name__ == '__main__':
    main()
