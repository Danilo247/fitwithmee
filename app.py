import re
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime, timedelta
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import secrets
import os
import traceback
from models import db, User, VerificationToken
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import json
import requests
import random


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///gym.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Brevo API configuration
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
BREVO_API_URL = 'https://api.brevo.com/v3/'
HEADERS = {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json'
}

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

def send_verification_email(email, token):
    try:
        if not BREVO_API_KEY:
            print("Error: BREVO_API_KEY is not set")
            return False
            
        email_data = {
            "sender": {"email": "okikidanielayo@gmail.com", "name": "Fit With COACH Daniel"},
            "to": [{"email": email}],
            "subject": "Verify Your Email - Fit With COACH Daniel",
            "htmlContent": f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #4CAF50;">Welcome to Fit With COACH Daniel!</h2>
                    <p>Thank you for registering. Please use the following code to verify your email address:</p>
                    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 24px; letter-spacing: 5px; margin: 20px 0;">
                        <strong>{token}</strong>
                    </div>
                    <p>This code will expire in 24 hours.</p>
                    <p>If you did not create an account, please ignore this email.</p>
                    <hr style="border: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">This is an automated message, please do not reply.</p>
                </div>
            '''
        }
            
        response = requests.post(
            f'{BREVO_API_URL}smtp/email',
            headers=HEADERS,
            data=json.dumps(email_data),
            timeout=10  # Add timeout to prevent hanging
        )
        
        print(f"Email API Response: {response.status_code} - {response.text}")

        if response.status_code == 201:
            return True
        else:
            print(f"Failed to send email: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Network error while sending email: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        traceback.print_exc()
        return False
        


# Helper functions for dashboard
def format_date(date_str):
    """Format a date string to a more readable format."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%B %d, %Y at %I:%M %p")
    except ValueError:
        return date_str

def get_user_stats():
    """Get user statistics."""
    total_users = User.query.count()
    verified_users = User.query.filter_by(verified=True).count()
    unverified_users = total_users - verified_users
    
    return {
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users
    }

def get_customer_stats(user_id):
    """Get customer-specific statistics."""
    # TODO: Replace with actual data from workout tracking
    return {
        'workouts': 0,
        'calories': 0,
        'active_minutes': 0,
        'achievements': 0
    }

def get_recent_activity(user_email):
    """Get recent activity for a user."""
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return []
        
    activities = []
    activities.append({
        'type': 'account_creation',
        'date': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'description': 'Account created'
    })
        
    if user.verified:
        activities.append({
            'type': 'verification',
            'date': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),  # Using created_at as fallback
            'description': 'Email verified'
        })
    
    # Sort activities by date
    activities.sort(key=lambda x: x['date'], reverse=True)
    return activities[:5]  # Return only the 5 most recent activities

# Form validation functions
def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """Validate password strength."""
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
    """Validate the registration form data."""
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    if not name or not email or not password:
        flash('All fields are required.')
        return False
        
    # Email validation
    if not validate_email(email):
        flash('Invalid email format.')
        return False
        
    # Password validation
    if not validate_password(password):
        flash('Password must be at least 8 characters long and contain at least one number and one special character.')
        return False
        
    return True

def validate_login_form():
    """Validate the login form data."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email:
        flash('Email is required.')
        return False
        
    if not password:
        flash('Password is required.')
        return False
        
    # Email validation
    if not validate_email(email):
        flash('Invalid email format.')
        return False
        
    return True

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('All fields are required.')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash('Invalid email or password')
                return redirect(url_for('login'))
                
            if not user.check_password(password):
                flash('Invalid email or password')
                return redirect(url_for('login'))
                
            if not user.verified:
                flash('Please verify your email address first.')
                return redirect(url_for('login'))
                
            login_user(user)
            return redirect(url_for('dashboard'))
                
        except Exception as e:
            print(f"Login error: {e}")
            traceback.print_exc()
            flash('An error occurred during login. Please try again.')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not name or not email or not password or not confirm_password:
                flash('All fields are required', 'error')
                return redirect(url_for('register'))

            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))

            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('register'))

            # Generate a random 8-digit token
            token = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            
            # Create new user
            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            
            # Create verification token
            verification_token = VerificationToken(token=token, email=email)
            db.session.add(verification_token)
            
            try:
                db.session.commit()
                print(f"Successfully created user: {email}")
            except Exception as e:
                db.session.rollback()
                print(f"Database error during registration: {str(e)}")
                traceback.print_exc()
                flash('An error occurred while creating your account. Please try again.', 'error')
                return redirect(url_for('register'))
            
            # Send verification email
            if send_verification_email(email, token):
                flash('Registration successful! Please check your email for verification code.', 'success')
                return render_template('verify_token.html', token=token)
            else:
                flash('Account created but failed to send verification email. Please contact support.', 'warning')
                return render_template('verify_token.html', token=token)
                
        except Exception as e:
            print(f"Registration error: {str(e)}")
            traceback.print_exc()
            flash('An unexpected error occurred. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/verify/<token>', methods=['GET', 'POST'])
def verify_token(token):
    verification = VerificationToken.query.filter_by(token=token).first()
    
    if not verification:
        flash('Invalid verification code', 'error')
        return redirect(url_for('login'))
    
    if verification.is_expired:
        flash('Verification code has expired', 'error')
        return redirect(url_for('resend_verification'))
    
    if request.method == 'POST':
        submitted_token = request.form.get('token')
        
        if submitted_token == token:
            user = User.query.filter_by(email=verification.email).first()
            if user:
                user.verified = True  # Changed from is_verified to verified
                db.session.delete(verification)
                try:
                    db.session.commit()
                    flash('Email verified successfully! You can now login.', 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    db.session.rollback()
                    print(f"Verification error: {e}")
                    traceback.print_exc()
                    flash('An error occurred during verification. Please try again.', 'error')
                    return redirect(url_for('verify_token', token=token))
            else:
                flash('User not found', 'error')
                return redirect(url_for('register'))
        else:
            flash('Invalid verification code', 'error')
            return redirect(url_for('verify_token', token=token))
    
    return render_template('verify_token.html', token=token)

@app.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found', 'error')
            return redirect(url_for('resend_verification'))
        
        if user.is_verified:
            flash('Email is already verified', 'error')
            return redirect(url_for('login'))
        
        # Generate new token
        token = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        # Delete old verification tokens
        VerificationToken.query.filter_by(email=email).delete()
        
        # Create new verification token
        verification_token = VerificationToken(
            token=token,
            email=email,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.session.add(verification_token)
        
        try:
            db.session.commit()
            
            if send_verification_email(email, token):
                flash('Verification code has been resent to your email', 'success')
                return redirect(url_for('verify_token', token=token))
            else:
                flash('Failed to send verification email', 'error')
                return redirect(url_for('resend_verification'))
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('resend_verification'))
    
    return render_template('resend_verification.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user = current_user
        user_dict = user.to_dict()
        user_dict['formatted_created_at'] = format_date(user_dict['created_at'])
        
        # Get stats based on user role
        if user.is_admin:
            stats = get_user_stats()
        else:
            stats = get_customer_stats(user.id)
        
        # Get recent activity
        activities = get_recent_activity(user.email)
        
        return render_template('dashboard.html', user=user_dict, stats=stats, activities=activities)
    except Exception as e:
        print(f"Dashboard error: {e}")
        traceback.print_exc()
        flash('An error occurred while loading the dashboard.')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard/profile')
@login_required
def profile():
    try:
        user = current_user
        user_dict = user.to_dict()
        return render_template('profile.html', user=user_dict)
    except Exception as e:
        print(f"Profile error: {e}")
        traceback.print_exc()
        flash('An error occurred while loading your profile.')
        return redirect(url_for('dashboard'))

@app.route('/dashboard/workouts')
@login_required
def workouts():
    try:
        user = current_user
        # TODO: Add actual workout data
        current_plan = {
            'workouts_per_week': 3,
            'duration': 12,
            'progress': 25
        }
        stats = {
            'total_time': 15,
            'total_calories': 2500,
            'total_workouts': 12,
            'total_achievements': 3
        }
        return render_template('workouts.html', current_plan=current_plan, stats=stats)
    except Exception as e:
        print(f"Workouts error: {e}")
        traceback.print_exc()
        flash('An error occurred while loading workouts.')
        return redirect(url_for('dashboard'))

@app.route('/dashboard/progress')
@login_required
def progress():
    try:
        user = current_user
        # TODO: Add actual progress data
        progress = {
            'current_weight': 75,
            'weight_trend': 'down',
            'weight_change': 2.5
        }
        return render_template('progress.html', progress=progress)
    except Exception as e:
        print(f"Progress error: {e}")
        traceback.print_exc()
        flash('An error occurred while loading progress.')
        return redirect(url_for('dashboard'))

@app.route('/dashboard/messages')
@login_required
def messages():
    try:
        user = current_user
        # TODO: Add actual messages data
        conversations = []
        current_conversation = None
        return render_template('messages.html', conversations=conversations, current_conversation=current_conversation)
    except Exception as e:
        print(f"Messages error: {e}")
        traceback.print_exc()
        flash('An error occurred while loading messages.')
        return redirect(url_for('dashboard'))

@app.route('/dashboard/community')
@login_required
def community():
    try:
        user = current_user
        # TODO: Add actual community data
        stats = {
            'total_members': 100,
            'active_today': 25,
            'total_posts': 50
        }
        return render_template('community.html', stats=stats)
    except Exception as e:
        print(f"Community error: {e}")
        traceback.print_exc()
        flash('An error occurred while loading community.')
        return redirect(url_for('dashboard'))

@app.route('/dashboard/settings')
@login_required
def settings():
    try:
        user = current_user
        # TODO: Add actual settings data
        notifications = {
            'push_workouts': True,
            'push_progress': True,
            'push_messages': False
        }
        return render_template('settings.html', user=user, notifications=notifications)
    except Exception as e:
        print(f"Settings error: {e}")
        traceback.print_exc()
        flash('An error occurred while loading settings.')
        return redirect(url_for('dashboard'))

def init_db():
    """Initialize the database with proper error handling."""
    try:
        with app.app_context():
            print("Initializing database...")
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Check if admin user exists, if not create one
            admin_email = os.getenv('ADMIN_EMAIL')
            admin_password = os.getenv('ADMIN_PASSWORD')
            
            if admin_email and admin_password:
                admin = User.query.filter_by(email=admin_email, role=ROLE_ADMIN).first()
                if not admin:
                    admin = User(
                        name='Admin',
                        email=admin_email,
                        role=ROLE_ADMIN,
                        verified=True
                    )
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()
                    print("Admin user created successfully")
            
            print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        traceback.print_exc()
        raise

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    print(f"Internal server error: {error}")
    traceback.print_exc()
    return render_template('error.html', error="Internal Server Error"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page Not Found"), 404

# Initialize database tables
init_db()

# For local development
if __name__ == '__main__':
    app.run(debug=True)