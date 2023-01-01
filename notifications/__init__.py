from firebase_admin import credentials, messaging, initialize_app
import os

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firebase_credentials.json")
firebase_cred = credentials.Certificate(file_path)
firebase_app = initialize_app(firebase_cred)


def send_notification(target: float, direction: str, token: str):
    data = {
        "target": str(target),
        "direction": direction
    }
    message = messaging.Message(notification=messaging.Notification(), token=token, data=data)
    messaging.send(message)
