import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_brevo_api():
    # Get API key from environment variable
    api_key = os.getenv('BREVO_API_KEY')
    if not api_key:
        print("Error: BREVO_API_KEY not found in environment variables")
        return False
    
    # Print first 10 characters of API key for debugging
    print(f"API Key (first 10 chars): {api_key[:10]}...")

    try:
        # Configure API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = api_key

        # Create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        # Create a test email
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": "okikiayodaniel@gmail.com", "name": "Test Recipient"}],
            sender={"name": "Danilo", "email": "okikidanielayo@gmail.com"},
            subject="Test Email from Brevo",
            html_content="<html><body><h1>Test Email</h1><p>This is a test email from Brevo API.</p></body></html>"
        )

        # Send the test email
        result = api_instance.send_transac_email(email)
        print("Email sent successfully!")
        print(f"Message ID: {result}")
        return True

    except ApiException as e:
        print(f"Error calling Send Transac Email: {e}")
        print(f"Error response body: {e.body}")
        print(f"Error response headers: {e.headers}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_brevo_api() 