from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import base64
import os
import json
import pickle
from dotenv import load_dotenv
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://pewfike.github.io", "http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Email configuration
SENDER_NAME = "Contact Form"
SENDER_EMAIL = os.getenv('GMAIL_ADDRESS')
FORMATTED_SENDER = formataddr((SENDER_NAME, SENDER_EMAIL))

def get_gmail_service():
    try:
        creds = None
        if os.path.exists('token.pickle'):
            logger.debug("Found token.pickle file")
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            logger.debug("Credentials not valid, refreshing...")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.debug("Getting new credentials from OAuth flow")
                if not os.path.exists('credentials.json'):
                    logger.error("credentials.json file not found!")
                    raise FileNotFoundError("credentials.json is missing")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
                logger.debug("Saved new token.pickle")

        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        logger.error(f"Error in get_gmail_service: {str(e)}")
        raise

def create_message(to, subject, message_text, html_content):
    try:
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = FORMATTED_SENDER
        message['subject'] = subject

        text_part = MIMEText(message_text, 'plain')
        message.attach(text_part)

        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    except Exception as e:
        logger.error(f"Error in create_message: {str(e)}")
        raise

def send_message(service, user_id, message):
    try:
        logger.debug("Attempting to send email...")
        message = service.users().messages().send(userId=user_id, body=message).execute()
        logger.debug(f"Email sent successfully. Message ID: {message['id']}")
        return message
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

def create_plain_text_message(name, email, message_text):
    return f"""
New message from your website contact form:

From: {name}
Email: {email}

Message:
{message_text}

Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

def create_html_message(name, email, message_text):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8fafc;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin: 0; font-size: 28px;">Website Contact Form</h1>
                </div>
                
                <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                    <h2 style="color: #1e40af; margin-top: 0; font-size: 22px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">
                        New Message Received
                    </h2>
                    
                    <div style="margin-top: 20px;">
                        <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                            <p style="margin: 0 0 10px 0;"><strong style="color: #2563eb;">From:</strong> {name}</p>
                            <p style="margin: 0;"><strong style="color: #2563eb;">Email:</strong> 
                                <a href="mailto:{email}" style="color: #2563eb; text-decoration: none;">{email}</a>
                            </p>
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <h3 style="color: #2563eb; margin: 0 0 10px 0; font-size: 18px;">Message:</h3>
                            <div style="background: #f8fafc; padding: 15px; border-radius: 8px; white-space: pre-wrap;">
                                {message_text}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #64748b; font-size: 14px; margin: 0;">
                        This message was sent from your website's contact form at {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    </p>
                </div>
            </div>
        </body>
    </html>
    """

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({'status': 'ok', 'message': 'Backend is working!'}), 200

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        logger.debug("Received email request")
        data = request.json
        logger.debug(f"Request data: {data}")

        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            logger.error("Missing required fields")
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if credentials.json exists
        if not os.path.exists('credentials.json'):
            logger.error("credentials.json not found")
            return jsonify({'error': 'Server configuration error: credentials.json missing'}), 500

        # Check if GMAIL_ADDRESS is set
        if not SENDER_EMAIL:
            logger.error("GMAIL_ADDRESS not set in environment variables")
            return jsonify({'error': 'Server configuration error: GMAIL_ADDRESS not set'}), 500

        # Get Gmail service
        logger.debug("Getting Gmail service...")
        service = get_gmail_service()
        
        # Create both plain text and HTML versions
        subject = f"Contact Form: Message from {name}"
        plain_text = create_plain_text_message(name, email, message)
        html_content = create_html_message(name, email, message)

        # Create and send the message
        logger.debug("Creating email message...")
        email_message = create_message(SENDER_EMAIL, subject, plain_text, html_content)
        
        logger.debug("Sending email...")
        result = send_message(service, "me", email_message)

        if result:
            logger.debug("Email sent successfully")
            return jsonify({'message': 'Email sent successfully'}), 200
        else:
            logger.error("Failed to send email - no result returned")
            return jsonify({'error': 'Failed to send email'}), 500

    except Exception as e:
        logger.error(f"Error in send_email: {str(e)}")
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 