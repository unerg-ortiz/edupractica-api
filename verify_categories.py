import urllib.request
import json
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            response_body = response.read().decode('utf-8')
            return status, json.loads(response_body)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def verify():
    print("--- Starting Verification ---")
    
    # 1. Create Category: Matemáticas
    print("\n1. Create Category: Matemáticas")
    status, res = make_request("POST", "/categories/", {
        "name": "Matemáticas",
        "description": "Ciencia formal",
        "icon": "math-icon"
    })
    print(f"Status: {status}")
    print(f"Response: {res}")
    math_id = res.get("id")

    # 2. Create Category: Ciencias
    print("\n2. Create Category: Ciencias")
    status, res = make_request("POST", "/categories/", {
        "name": "Ciencias",
        "description": "Ciencias naturales",
        "icon": "science-icon"
    })
    print(f"Status: {status}")
    print(f"Response: {res}")
    science_id = res.get("id")

    # 3. Get All Categories
    print("\n3. Get All Categories")
    status, res = make_request("GET", "/categories/")
    print(f"Status: {status}")
    print(f"Response: {res}")
    assert len(res) >= 2

    # 4. Get Category by ID
    print(f"\n4. Get Category by ID ({math_id})")
    status, res = make_request("GET", f"/categories/{math_id}")
    print(f"Status: {status}")
    print(f"Response: {res}")
    assert res['name'] == "Matemáticas"

    # 5. Update Category
    print(f"\n5. Update Category ({math_id})")
    status, res = make_request("PUT", f"/categories/{math_id}", {
        "name": "Matemáticas Avanzadas"
    })
    print(f"Status: {status}")
    print(f"Response: {res}")
    assert res['name'] == "Matemáticas Avanzadas"

    # 6. Delete Category
    print(f"\n6. Delete Category ({science_id})")
    status, res = make_request("DELETE", f"/categories/{science_id}")
    print(f"Status: {status}")
    print(f"Response: {res}")
    
    # 7. Verification: Get All again
    print("\n7. Get All Categories (after delete)")
    status, res = make_request("GET", "/categories/")
    print(f"Status: {status}")
    print(f"Response: {res}")

    print("\n--- Verification Completed ---")

if __name__ == "__main__":
    verify()
