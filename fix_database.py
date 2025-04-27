from app import app, db
from models import User, ROLE_CUSTOMER
import sqlite3

def fix_database():
    try:
        # Connect to the database
        with app.app_context():
            conn = sqlite3.connect('instance/gym.db')
            cursor = conn.cursor()
            
            # Check if role column exists
            cursor.execute("PRAGMA table_info(user)")
            columns = cursor.fetchall()
            has_role = any(col[1] == 'role' for col in columns)
            
            if not has_role:
                # Add role column
                cursor.execute("ALTER TABLE user ADD COLUMN role VARCHAR(20)")
                # Set default value for existing rows
                cursor.execute("UPDATE user SET role = ?", (ROLE_CUSTOMER,))
                conn.commit()
                print("Successfully added role column and set default values")
            
            conn.close()
            print("Database fix completed successfully")
            
    except Exception as e:
        print(f"Error fixing database: {str(e)}")
        raise

if __name__ == '__main__':
    fix_database() 