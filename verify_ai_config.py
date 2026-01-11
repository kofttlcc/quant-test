
import requests
import time

API_URL = "http://localhost:5001/api/v1/ai/config"

def test_config_update():
    print("Testing AI Config Update with Model Selection...")
    
    # Payload with model
    payload = {
        "api_url": "https://generativelanguage.googleapis.com",
        "api_key": "test_key_123",
        "model": "gemini-3-flash"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"Response: {data}")
        
        if data.get("success") == True:
            print("✅ Config updated successfully.")
        else:
            print("❌ Update failed.")
            exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

if __name__ == "__main__":
    # Wait for server to be fully ready
    time.sleep(2)
    test_config_update()
