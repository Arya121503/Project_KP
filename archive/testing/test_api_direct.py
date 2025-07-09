#!/usr/bin/env python3

import requests
import json

def test_total_properti_api():
    """Test the /api/total-properti endpoint directly"""
    try:
        url = "http://127.0.0.1:5000/api/total-properti"
        print(f"Testing API endpoint: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2, default=str))
            
            if data.get('success'):
                properties = data.get('data', {}).get('all_properties', [])
                print(f"\nData Summary:")
                print(f"- Total properties: {len(properties)}")
                if properties:
                    print(f"- First property: {properties[0]}")
                    print(f"- Property types: {set(p.get('tipe') for p in properties)}")
                    print(f"- Kecamatan: {set(p.get('kecamatan') for p in properties[:10])}")  # Show first 10
            else:
                print(f"API returned error: {data.get('error')}")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Server tidak berjalan di http://127.0.0.1:5000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_total_properti_api()
