
#Flask App
# from os import name
# from todolist import create_app

# app = create_app()
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)


from os import name
from todolist import create_app
from flask import request, abort
import re
import datetime
import requests

app = create_app()

BLACKLISTED_PATTERNS = [
    r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
    r"<script.*?>.*?</script.*?>",
    r"(\b(select|union|insert|update|delete|drop|alter)\b)",
]

WEBHOOK_URL = "https://webhook.site/7e7fc2f7-6fe2-4458-acad-fdcd16ca134e"

def check_attack(value):
    if not value:
        return False
    for pattern in BLACKLISTED_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False

def send_waf_alert(reason):
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": request.remote_addr,
        "path": request.path,
        "method": request.method,
        "reason": reason,
        "user_agent": request.headers.get("User-Agent", "")
    }
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=2)
    except Exception as e:
        print(f"❗️ Lỗi khi gửi webhook: {e}")

@app.before_request
def waf_middleware():
    for key, value in request.args.items():
        if check_attack(value):
            reason = f"Query param '{key}' = '{value}'"
            send_waf_alert(reason)
            abort(403, description="Forbidden by WAF")

    for key, value in request.form.items():
        if check_attack(value):
            reason = f"Form param '{key}' = '{value}'"
            send_waf_alert(reason)
            abort(403, description="Forbidden by WAF")

    if request.is_json:
        json_data = request.get_json()

        def check_json(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if check_json(v):
                        send_waf_alert(f"JSON param '{k}' = '{v}'")
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if check_json(item):
                        return True
            elif isinstance(obj, str):
                if check_attack(obj):
                    return True
            return False

        if check_json(json_data):
            abort(403, description="Forbidden by WAF")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

