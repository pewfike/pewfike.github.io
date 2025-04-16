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

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Email configuration
SENDER_NAME = "Contact Form"
SENDER_EMAIL = os.getenv('GMAIL_ADDRESS', 'your-email@gmail.com')
FORMATTED_SENDER = formataddr((SENDER_NAME, SENDER_EMAIL))

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def create_message(to, subject, message_text, html_content):
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = FORMATTED_SENDER
    message['subject'] = subject

    # Add plain text version
    text_part = MIMEText(message_text, 'plain')
    message.attach(text_part)

    # Add HTML version
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

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

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get Gmail service
        service = get_gmail_service()
        
        # Create both plain text and HTML versions
        subject = f"Contact Form: Message from {name}"
        plain_text = create_plain_text_message(name, email, message)
        html_content = create_html_message(name, email, message)

        # Create and send the message
        email_message = create_message(SENDER_EMAIL, subject, plain_text, html_content)
        result = send_message(service, "me", email_message)

        if result:
            return jsonify({'message': 'Email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Failed to send email'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 