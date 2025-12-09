import requests
import time
import json

# 配置 (与 jsonbin.py 保持一致)
BIN_ID = "693813dbae596e708f8d8d1f"
ACCESS_KEY = "$2a$10$fsFe1YMuzcva0dqyNdmvT.vS.awBw9pPoW00SwklTHStp/1JhfuUO"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
HEADERS = {"X-Access-Key": ACCESS_KEY}

print(f"🎧 开始监听 JSONBin ({BIN_ID})...")
print("按 Ctrl+C 停止")
print("-" * 30)

last_text = None

try:
    while True:
        try:
            # 1. 获取最新数据
            response = requests.get(URL, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json().get("record", {})
                current_text = data.get("text")
                is_read = data.get("read")
                timestamp = data.get("timestamp")

                # 2. 如果内容变了，或者是新生成的未读消息，就打印
                if current_text != last_text:
                    print(f"\n[新消息] {timestamp}")
                    print(f"内容: {current_text}")
                    print(f"状态: {'已读' if is_read else '未读'}")
                    print("-" * 30)
                    last_text = current_text
            else:
                print(f"获取失败: {response.status_code}")

        except Exception as e:
            print(f"发生错误: {e}")
            
        # 3. 每2秒查一次
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 停止监听")

