# Fit With COACH Daniel

A web application for managing gym memberships and user accounts.

## Features

- User registration and authentication
- Email verification
- User dashboard
- Secure password handling
- Responsive design

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd emmatos-gym
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```
Edit the `.env` file and add your configuration values:
- Generate a secure `SECRET_KEY`
- Add your Brevo API key for email functionality
- Configure your database URL if needed

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Deployment

### Option 1: Deploy to Heroku

1. Create a Heroku account and install the Heroku CLI
2. Create a new Heroku app:
```bash
heroku create your-app-name
```

3. Add the PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:mini
```

4. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set BREVO_API_KEY=your-brevo-api-key
```

5. Deploy:
```bash
git push heroku main
```

### Option 2: Deploy to Python Anywhere

1. Create a Python Anywhere account
2. Upload your code using Git or the Python Anywhere interface
3. Create a virtual environment and install dependencies
4. Configure your web app to use the virtual environment
5. Set up environment variables in the web app configuration
6. Configure your WSGI file to point to your Flask application

## Security Considerations

- All passwords are hashed using Werkzeug's security functions
- Email verification is required for new accounts
- Session management is handled securely
- CSRF protection is enabled
- Secure headers are configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 