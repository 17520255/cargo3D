import requests
import json

def test_curl():
    """Test the API with curl-like request"""
    
    data = {
        "goods": [
            {
                "id": "1",
                "width": 10,
                "height": 10,
                "depth": 10,
                "name": "Box 1",
                "label": "A",
                "weight": 5.0
            }
        ],
        "container": {
            "width": 50,
            "height": 50,
            "depth": 50
        }
    }
    
    try:
        print("Testing API with simple request...")
        response = requests.post(
            "http://localhost:8000/api/pack",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_curl() 