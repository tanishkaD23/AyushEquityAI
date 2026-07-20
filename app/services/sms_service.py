"""
SMS service for citizen intake via SMS.
Allows citizens to check eligibility and report fraud via SMS.
"""

from typing import Dict
from datetime import datetime
import re


class SMSService:
    """
    SMS gateway for PM-JAY citizen engagement.
    """
    
    # SMS commands
    COMMANDS = {
        "ELIGIBLE": "Check eligibility",
        "STATUS": "Check enrollment status",
        "HOSPITAL": "Find nearby hospitals",
        "FRAUD": "Report suspected fraud",
        "HELP": "Get help"
    }
    
    @staticmethod
    def parse_sms(phone_number: str, message_text: str) -> Dict:
        """
        Parse incoming SMS message.
        
        Args:
            phone_number (str): Sender's phone number
            message_text (str): Message content
        
        Returns:
            dict: Parsed request
        """
        
        text_upper = message_text.upper().strip()
        
        # Extract command (first word)
        parts = text_upper.split()
        command = parts[0] if parts else "HELP"
        
        # Parse based on command
        if command == "ELIGIBLE":
            return SMSService._parse_eligibility_request(phone_number, parts)
        elif command == "STATUS":
            return SMSService._parse_status_request(phone_number)
        elif command == "HOSPITAL":
            return SMSService._parse_hospital_request(phone_number, parts)
        elif command == "FRAUD":
            return SMSService._parse_fraud_report(phone_number, message_text)
        else:
            return {
                "request_type": "help",
                "phone_number": phone_number,
                "message": message_text,
                "response": "Send: ELIGIBLE, STATUS, HOSPITAL, or FRAUD for assistance"
            }
    
    @staticmethod
    def _parse_eligibility_request(phone_number: str, parts: list) -> Dict:
        """Parse eligibility check request."""
        return {
            "request_type": "eligibility_check",
            "phone_number": phone_number,
            "message": " ".join(parts),
            "received_at": datetime.utcnow().isoformat(),
            "response": "Please provide: Income category (BPL/APL/EWS), Family size, District. e.g., ELIGIBLE BPL 5 Indore"
        }
    
    @staticmethod
    def _parse_status_request(phone_number: str) -> Dict:
        """Parse status check request."""
        return {
            "request_type": "status_check",
            "phone_number": phone_number,
            "received_at": datetime.utcnow().isoformat(),
            "response": "Your PM-JAY enrollment is ACTIVE. Coverage: ₹5,00,000 per family per year"
        }
    
    @staticmethod
    def _parse_hospital_request(phone_number: str, parts: list) -> Dict:
        """Parse hospital locator request."""
        district = " ".join(parts[1:]) if len(parts) > 1 else "current location"
        return {
            "request_type": "hospital_locator",
            "phone_number": phone_number,
            "district": district,
            "received_at": datetime.utcnow().isoformat(),
            "response": f"Nearby empanelled hospitals in {district}: 1) Max Hospital, 2) Apollo Clinic. Call 1800-AYUSH-1 for more"
        }
    
    @staticmethod
    def _parse_fraud_report(phone_number: str, message_text: str) -> Dict:
        """Parse fraud report."""
        return {
            "request_type": "fraud_report",
            "phone_number": phone_number,
            "grievance_text": message_text,
            "received_at": datetime.utcnow().isoformat(),
            "response": "Fraud report received. Reference: GRV123456. We will investigate within 48 hours. Thank you"
        }
    
    @staticmethod
    def format_sms_response(response_text: str, phone_number: str) -> Dict:
        """
        Format SMS response for sending.
        
        Args:
            response_text (str): Response message
            phone_number (str): Recipient phone number
        
        Returns:
            dict: SMS to send
        """
        
        return {
            "to": phone_number,
            "body": response_text,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "queued"
        }


# Mock Twilio webhook handler
def handle_sms_webhook(phone_number: str, message_text: str) -> Dict:
    """
    Handle incoming SMS webhook from Twilio.
    
    Args:
        phone_number (str): Sender's phone
        message_text (str): Message content
    
    Returns:
        dict: Response
    """
    
    # Parse request
    parsed = SMSService.parse_sms(phone_number, message_text)
    
    # Generate response
    response_sms = SMSService.format_sms_response(
        parsed.get('response', 'Message received'),
        phone_number
    )
    
    return {
        "incoming_request": parsed,
        "outgoing_sms": response_sms,
        "message": "SMS processed and queued for delivery"
    }


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("SMS SERVICE TEST")
    print("=" * 60)
    
    test_messages = [
        ("+919876543210", "ELIGIBLE BPL 5 Indore"),
        ("+919876543211", "STATUS"),
        ("+919876543212", "HOSPITAL Pune"),
        ("+919876543213", "FRAUD Hospital submitted duplicate claim for my surgery")
    ]
    
    print("\n📱 Processing test SMS messages...\n")
    
    for phone, message in test_messages:
        result = handle_sms_webhook(phone, message)
        print(f"From: {phone}")
        print(f"Message: {message}")
        print(f"Response: {result['outgoing_sms']['body']}")
        print()