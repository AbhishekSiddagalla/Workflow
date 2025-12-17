import requests

from backend.api_config import api_access_token, api_version, whatsapp_business_account_id

def send_whatsapp_template(phone_number, template_name, language="en_US", components=None):
    base_url = f"https://graph.facebook.com/{api_version}/{whatsapp_business_account_id}/messages"

    headers = {
        "Authorization": f"Bearer {api_access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        }
    }

    if components:
        payload["template"]["components"] = components

    response = requests.post(base_url, headers=headers, json=payload)

    return payload, response.status_code, response.text
