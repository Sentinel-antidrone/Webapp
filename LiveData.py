import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import json
import os

# Define the folder where you want to save the detection files
output_folder = 'detection_data'

# --- Setup Firebase Admin SDK ---
try:
    # Check if running in production with environment variables
    if 'FIREBASE_PROJECT_ID' in os.environ:
        # Use environment variables instead of service account file
        firebase_credentials = {
            "type": "service_account",
            "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
            "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
            "auth_uri": os.environ.get('FIREBASE_AUTH_URI'),
            "token_uri": os.environ.get('FIREBASE_TOKEN_URI'),
            "auth_provider_x509_cert_url": os.environ.get('FIREBASE_AUTH_PROVIDER_CERT_URL'),
            "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL')
        }
        cred = credentials.Certificate(firebase_credentials)
    else:
        print(f"No no no! You need to set the environment variables for Firebase credentials.")
    
    # Get database URL from environment variable or use hardcoded value as fallback
    database_url = os.environ.get('FIREBASE_DATABASE_URL', 
                                 'https://sentinel-d1c9e-default-rtdb.europe-west1.firebasedatabase.app')
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': database_url
    })
    print("Firebase Admin SDK initialized successfully.")
except FileNotFoundError:
    print(f"Error: Service account key file not found. Please check your configuration.")
    exit()
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    exit()

# Get a database reference to the 'detections' node
detections_ref = db.reference('detections')

# --- Ensure the output folder exists ---
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created output folder: {output_folder}")
else:
    print(f"Output folder already exists: {output_folder}")


print(f"\nListening for new detections on: {detections_ref.url}")

# Define a callback function that will be triggered when a new child is added
def new_detection_listener(event):
    """
    Callback function triggered when a new child is added under /detections.
    The 'event' object contains information about the added child.
    """
    print("-" * 20) # Separator for clarity
    print(f"Event Type: {event.event_type}")
    print(f"Relative Path: {event.path}")
    print(f"Data received for new child:")
    # print(json.dumps(event.data, indent=2)) # Optional: print the data nicely

    # Get the unique key (ID) of the new detection
    # event.path starts with '/', so we remove it to get the key
    detection_id = event.path.lstrip('/')

    # Get the actual data of the new detection
    detection_data = event.data

    if detection_id and detection_data is not None:
        # Define the filename using the detection ID
        filename = f"{detection_id}.json"
        filepath = os.path.join(output_folder, filename)

        try:
            # Save the detection data to a JSON file
            with open(filepath, 'w') as f:
                json.dump(detection_data, f, indent=2) # Use indent for readability

            print(f"Saved new detection '{detection_id}' to {filepath}")
        except Exception as e:
            print(f"Error saving detection '{detection_id}' to file: {e}")
    else:
        print("Received empty or invalid data for a new child.")

    print("-" * 20)


# Attach the listener to the 'detections' reference for 'child_added' events
# This means the 'new_detection_listener' function will be called:
# 1. Once for each existing child under /detections when the script starts.
# 2. Once every time a new child is added to /detections after the script starts.
detections_ref.listen(new_detection_listener, 'child_added')

print("Listener started. Waiting for new detections...")
print(f"New detection data will be saved in the '{output_folder}' folder.")
print("Press Ctrl+C to stop.")

# Keep the script running indefinitely to listen for events
try:
    while True:
        time.sleep(1) # Sleep to prevent high CPU usage while waiting
except KeyboardInterrupt:
    print("\nListener stopping...")
    # In a more complex application, you might need to explicitly detach listeners
    # but for this simple script, Ctrl+C stopping the process is usually sufficient.

print("Listener stopped.")

