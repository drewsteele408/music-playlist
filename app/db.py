from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

def get_db():
    if not firebase_admin.apps:
        initialize_app()
    return firestore.client()