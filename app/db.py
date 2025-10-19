import firebase_admin
from firebase_admin import firestore, initialize_app

def get_db():
    try:
        firebase_admin.get_app()
    except ValueError: 
        initialize_app()
    return firestore.client()