"""
Authentication utilities for the Fit With COACH Daniel application.
This module provides functions for client-side validation and authentication.
"""

import re
from flask import request, flash, redirect, url_for

def validate_email(email):
    """
    Validate email format.
    
    Args:
        email (str): The email address to validate.
        
    Returns:
        bool: True if the email is valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password (str): The password to validate.
        
    Returns:
        bool: True if the password meets the requirements, False otherwise.
    """
    # Password must be at least 8 characters long
    if len(password) < 8:
        return False
    
    # Password must contain at least one number
    if not re.search(r'\d', password):
        return False
    
    # Password must contain at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_registration_form():
    """
    Validate the registration form data.
    
    Returns:
        bool: True if the form data is valid, False otherwise.
    """
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    if not name or not email or not password:
        return False
        
    # Email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False
        
    # Password validation (at least 8 characters, 1 uppercase, 1 lowercase, 1 number)
    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
    if not re.match(password_pattern, password):
        return False
        
    return True

def validate_login_form():
    """
    Validate the login form data.
    
    Returns:
        bool: True if the form data is valid, False otherwise.
    """
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    if not email or not password:
        return False
        
    # Email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False
        
    return True 