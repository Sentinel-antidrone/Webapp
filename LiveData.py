import requests
import time
import random
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sensor_data.log"),
        logging.StreamHandler()
    ]
)

# API configuration
API_URL = "https://sentinel-drone-api.onrender.com/api/data"
API_KEY = "sentinel-drone-key"  # In a real application, this would be a secure key

# Drone detection simulation parameters
DETECTION_PROBABILITY = 0.2  # 20% chance of detecting a drone in each cycle
BASE_COORDINATES = (38.736946, -9.142685)  # Lisbon coordinates as base
COORDINATE_VARIATION = 0.01  # Small random variation for simulated locations

def generate_sensor_data():
    """Generate simulated sensor data."""
    # Simulate drone detection based on probability
    drone_detected = random.random() < DETECTION_PROBABILITY
    
    # Get current timestamp
    timestamp = datetime.now().isoformat()
    
    # Base sensor data
    sensor_data = {
        "timestamp": timestamp,
        "system_status": "alert" if drone_detected else "operational",
        "rf_detection": {
            "signal_strength": random.randint(10, 90),
            "frequency_mhz": random.uniform(2400, 5800)
        },
        "visual_detection": {
            "confidence": random.randint(0, 100),
            "detected_objects": random.randint(0, 3)
        },
        "acoustic_detection": {
            "decibel_level": random.randint(20, 80),
            "signature_match": random.random() > 0.5
        }
    }
    
    # Add detection-specific data if a drone is detected
    if drone_detected:
        # Generate random coordinates near the base
        lat = BASE_COORDINATES[0] + random.uniform(-COORDINATE_VARIATION, COORDINATE_VARIATION)
        lon = BASE_COORDINATES[1] + random.uniform(-COORDINATE_VARIATION, COORDINATE_VARIATION)
        
        sensor_data["drone_detection"] = {
            "detected": True,
            "coordinates": [lat, lon],
            "altitude_meters": random.randint(50, 200),
            "speed_kmh": random.randint(0, 60),
            "drone_type": random.choice(["quadcopter", "hexacopter", "fixed-wing"])
        }
    else:
        sensor_data["drone_detection"] = {
            "detected": False
        }
    
    return sensor_data

def send_data_to_api(data):
    """Send data to API endpoint."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            logging.info(f"Data sent successfully: Status {response.status_code}")
            return True
        else:
            logging.error(f"Failed to send data: Status {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error sending data: {str(e)}")
        return False

def main():
    """Main function to run the data collection and sending loop."""
    logging.info("Starting Sentinel Anti-Drone data collection system")
    
    try:
        while True:
            # Generate sensor data
            sensor_data = generate_sensor_data()
            
            # Log the data being sent (in production, you might want to reduce this)
            logging.info(f"Sending data: {json.dumps(sensor_data, indent=2)}")
            
            # Send data to API
            send_data_to_api(sensor_data)
            
            # Wait before sending next data point
            time.sleep(10)  # Send every 10 seconds
    except KeyboardInterrupt:
        logging.info("Data collection stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()

# found this online:
# import requests
# import time
#
# API_URL = "https://your-webapp.com/api/data"
# API_KEY = "your_api_key_here"
#
# while True:
#     sensor_data = {"temperature": 25.5, "humidity": 60}  # Replace with real sensor data
#     headers = {"Authorization": f"Bearer {API_KEY}"}
#     
#     try:
#         response = requests.post(API_URL, json=sensor_data, headers=headers)
#         print("Data sent:", response.status_code)
#     except Exception as e:
#         print("Error:", e)
#     
#     time.sleep(10)  # Send every 10 seconds