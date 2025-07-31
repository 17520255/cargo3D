import requests
import json

def test_packing_api():
    """Test the packing API endpoint"""
    
    # Sample data
    test_data = {
        "goods": [
            {
                "id": "1",
                "width": 10,
                "height": 10,
                "depth": 10,
                "name": "Box 1",
                "label": "A",
                "weight": 5.0
            },
            {
                "id": "2",
                "width": 15,
                "height": 15,
                "depth": 15,
                "name": "Box 2",
                "label": "B",
                "weight": 8.0
            }
        ],
        "container": {
            "width": 50,
            "height": 50,
            "depth": 50
        },
        "iterations": 5
    }
    
    try:
        print("Testing packing API...")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/api/pack",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Error!")
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_packing_api() 