# main.py
from flask import Flask, request, Response
import logging
from config.logging_config import setup_logging
from config.settings import PORT, DEBUG
from app.services.sms import SMSService
from app.database.db import init_db

# Initialize application
app = Flask(__name__)
logger = setup_logging()
sms_service = SMSService()

@app.route("/sms", methods=['POST'])
def handle_sms():
    """Handle incoming SMS messages with clean responses"""
    incoming_msg = request.values.get('Body', '')
    phone_number = request.values.get('From', '')
    
    logger.info(f"Received message from {phone_number}: {incoming_msg}")
    
    # Get plain text response from SMS service
    message = sms_service.handle_message(phone_number, incoming_msg)
    
    # Return plain text response
    return Response(message, mimetype='text/plain')

def test_sms_locally():
    """Function to test SMS functionality locally"""
    while True:
        try:
            print("\nEnter command (or 'exit' to quit):")
            message = input("> ")
            
            if message.lower() == 'exit':
                break
                
            test_phone = "+1234567890"
            response = sms_service.handle_message(test_phone, message)
            print("\nResponse:", response)
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    if DEBUG:
        print("\nStarting in DEBUG mode")
        print("1. Run server (s)")
        print("2. Test locally (t)")
        choice = input("Choose option: ").lower()
        
        if choice == 't':
            test_sms_locally()
        else:
            logger.info(f"Starting server on port {PORT}...")
            app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
    else:
        logger.info(f"Starting server on port {PORT}...")
        app.run(host='0.0.0.0', port=PORT, debug=False)