from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import secrets
import os
import traceback
import re
from models import db, User, VerificationToken
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///gym.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Brevo API configuration
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
if not BREVO_API_KEY:
    raise ValueError("BREVO_API_KEY environment variable is not set")

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
        sender = {"name": "Danilo", "email": "okikidanielayo@gmail.com"}
        to = [{"email": email}]
        subject = "Verify your email address"
        html_content = f"""
        <html>
            <body>
                <h2>Welcome to Fit With COACH Daniel!</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{request.host_url}verify/{token}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you did not create an account, please ignore this email.</p>
            </body>
        </html>
        """
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )
        
        api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Error sending email: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending email: {e}")
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
    """Get statistics about users."""
    total_users = User.query.count()
    verified_users = User.query.filter_by(verified=True).count()
    unverified_users = total_users - verified_users
    
    return {
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users
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
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    if not email or not password:
        flash('Email and password are required.')
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
            if not validate_login_form():
                return redirect(url_for('login'))
                
            email = request.form['email']
            password = request.form['password']
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                if not user.verified:
                    flash('Please verify your email address first.')
                    return redirect(url_for('login'))
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
        except Exception as e:
            print(f"Login error: {e}")
            traceback.print_exc()
            flash('An error occurred during login. Please try again.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            if not validate_registration_form():
                return redirect(url_for('register'))
                
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
            else:
                user = User(name=name, email=email)
                user.set_password(password)
                
                # Generate verification token
                token = secrets.token_urlsafe(32)
                verification_token = VerificationToken(token=token, email=email)
                
                db.session.add(user)
                db.session.add(verification_token)
                db.session.commit()
                
                # Send verification email
                if send_verification_email(email, token):
                    flash('Registration successful! Please check your email to verify your account.')
                else:
                    flash('Registration successful but failed to send verification email. Please contact support.')
                
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration error: {e}")
            traceback.print_exc()
            flash('An error occurred during registration. Please try again.')
    
    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    try:
        verification = VerificationToken.query.filter_by(token=token).first()
        
        if not verification:
            flash('Invalid verification link.')
            return redirect(url_for('login'))
            
        if verification.is_expired:
            db.session.delete(verification)
            db.session.commit()
            flash('Verification link has expired. Please request a new one.')
            return redirect(url_for('login'))
            
        user = User.query.filter_by(email=verification.email).first()
        if not user:
            flash('User not found.')
            return redirect(url_for('login'))
            
        user.verified = True
        db.session.delete(verification)
        db.session.commit()
        
        flash('Email verified successfully! You can now login.')
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Verification error: {e}")
        traceback.print_exc()
        flash('An error occurred during verification. Please try again.')
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user = current_user
        user_dict = user.to_dict()
        user_dict['formatted_created_at'] = format_date(user_dict['created_at'])
        
        # Get user statistics
        stats = get_user_stats()
        
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
def init_db():
    with app.app_context():
        db.create_all()

# For local development
if __name__ == '__main__':
    init_db()
    app.run(debug=True)