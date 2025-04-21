"""
Dashboard utilities for the Fit With COACH Daniel application.
This module provides functions for dashboard data processing and display.
"""

from datetime import datetime

def format_date(date_str):
    """
    Format a date string to a more readable format.
    
    Args:
        date_str (str): The date string to format.
        
    Returns:
        str: The formatted date string.
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%B %d, %Y at %I:%M %p")
    except ValueError:
        return date_str

def get_user_stats(users):
    """
    Get statistics about users.
    
    Args:
        users (dict): The users dictionary.
        
    Returns:
        dict: A dictionary containing user statistics.
    """
    total_users = len(users)
    verified_users = sum(1 for user in users.values() if user.get('verified', False))
    unverified_users = total_users - verified_users
    
    return {
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users
    }

def get_recent_activity(users, current_user_email):
    """
    Get recent activity for a user.
    
    Args:
        users (dict): The users dictionary.
        current_user_email (str): The current user's email.
        
    Returns:
        list: A list of recent activities.
    """
    activities = []
    for email, user in users.items():
        if email == current_user_email:
            activities.append({
                'type': 'account_creation',
                'date': user['created_at'],
                'description': 'Account created'
            })
            
            if user.get('verified', False):
                activities.append({
                    'type': 'verification',
                    'date': user.get('verified_at', user['created_at']),
                    'description': 'Email verified'
                })
    
    # Sort activities by date
    activities.sort(key=lambda x: x['date'], reverse=True)
    return activities[:5]  # Return only the 5 most recent activities 