import requests
from datetime import datetime

JSONBIN_BIN_ID = "693813dbae596e708f8d8d1f"
JSONBIN_ACCESS_KEY = "$2a$10$fsFe1YMuzcva0dqyNdmvT.vS.awBw9pPoW00SwklTHStp/1JhfuUO"

JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

def save_latest_reply(text):
    data = {
        "text": text,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    
    try:
        response = requests.put(
            JSONBIN_URL,
            json=data,
            headers={
                "X-Access-Key": JSONBIN_ACCESS_KEY,
                "Content-Type": "application/json"
            }
        )
        if response.status_code != 200:
            print(f"JSONBin Save Error: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"JSONBin Save Exception: {e}")
        return False

def get_latest_reply():
    try:
        response = requests.get(
            JSONBIN_URL + "/latest",
            headers={"X-Access-Key": JSONBIN_ACCESS_KEY}
        )
        if response.status_code == 200:
            data = response.json().get("record", {})
            if not data.get("read", False):
                data["read"] = True
                requests.put(
                    JSONBIN_URL,
                    json=data,
                    headers={"X-Access-Key": JSONBIN_ACCESS_KEY}
                )
                return {"has_new": True, "text": data.get("text")}
        return {"has_new": False, "text": None}
    except:
        return {"has_new": False, "text": None}

