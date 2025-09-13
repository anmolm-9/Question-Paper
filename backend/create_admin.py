#!/usr/bin/env python3
"""
Script to create the first admin user for the QP application.
Run this script to create an initial admin account.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_model import create_user, find_user_by_email
import getpass

def create_first_admin():
    print("=== Create First Admin User ===\n")
    
    # Get admin details
    first_name = input("Enter admin first name: ").strip()
    last_name = input("Enter admin last name: ").strip()
    email = input("Enter admin email: ").strip()
    
    # Validate input
    if len(first_name) < 2:
        print("Error: First name must be at least 2 characters")
        return False
    
    if len(last_name) < 2:
        print("Error: Last name must be at least 2 characters")
        return False
    
    if "@" not in email:
        print("Error: Please enter a valid email address")
        return False
    
    # Check if email already exists
    if find_user_by_email(email):
        print(f"Error: Email {email} is already registered!")
        return False
    
    # Get password
    while True:
        password = getpass.getpass("Enter admin password: ")
        confirm_password = getpass.getpass("Confirm admin password: ")
        
        if password != confirm_password:
            print("Error: Passwords do not match. Please try again.")
            continue
        
        if len(password) < 6:
            print("Error: Password must be at least 6 characters")
            continue
        
        break
    
    try:
        # Create admin user
        user_doc = create_user(first_name, last_name, email, password, role="admin")
        print(f"\n✅ Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Role: admin")
        print(f"User ID: {user_doc['_id']}")
        print("\nYou can now login to the admin panel with these credentials.")
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

if __name__ == "__main__":
    success = create_first_admin()
    if not success:
        sys.exit(1)