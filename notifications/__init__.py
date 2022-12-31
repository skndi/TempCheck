import firebase_admin
from firebase_admin import credentials, messaging

firebase_cred = credentials.Certificate("notifications/firebase_credentials.json")
firebase_app = firebase_admin.initialize_app(firebase_cred)


def send_notification(target: float, direction: str, token: str):
    data = {
        "target": str(target),
        "direction": direction
    }
    message = messaging.Message(notification=messaging.Notification(), token=token, data=data)
    messaging.send(message)
