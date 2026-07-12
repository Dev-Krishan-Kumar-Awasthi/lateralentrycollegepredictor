import urllib.request
import json

url = "http://127.0.0.1:5000/api/v1/college/route-info?college_name=Shri+G.S.+Institute+of+Technology+%26+Science+Indore+(M.P.)+(1952)&home_city=Bhopal&category=UR"

try:
    print("Testing API route-info connection...")
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode())
    print("API SUCCESS! Data returned:")
    print("College:", data.get("college_name"))
    print("Home City:", data.get("home_city"))
    print("Dest City:", data.get("dest_city"))
    print("Distance:", data.get("distance_text"))
    print("Transit steps:")
    for step in data.get("route_steps", []):
        print(" -", step)
    print("Required Documents Count:", len(data.get("documents", [])))
except Exception as e:
    print("API FAILED or server is down:", e)
