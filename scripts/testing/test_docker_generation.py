import requests
import json
import time

API_URL = "http://localhost:8000/api/v1/generate-treatment-summary"

payload = {
    "patient_name": "Docker Test Patient",
    "tier": "moderate",
    "patient_age": 25,
    "treatment_type": "clear aligners",
    "area_treated": "both",
    "duration_range": "12-14 months",
    "case_difficulty": "moderate",
    "audience": "patient",
    "tone": "reassuring",
    "dentist_note": "Great candidate for aligners."
}

print(f"Sending request to {API_URL}...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    start_time = time.time()
    response = requests.post(API_URL, json=payload)
    duration = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess! (Time: {duration:.2f}s)")
        print("\nGenerated Summary:")
        print("-" * 50)
        print(data)
        print("-" * 50)
        
        if data.get("cdt_codes"):
            print("\nCDT Codes:")
            cdt = data["cdt_codes"]
            print(f"Primary: {cdt.get('primary_code')} - {cdt.get('primary_description')}")
            for addon in cdt.get("suggested_add_ons", []):
                print(f"Add-on: {addon['code']} - {addon['description']}")
    else:
        print(f"\nError {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"\nConnection Failed: {str(e)}")
