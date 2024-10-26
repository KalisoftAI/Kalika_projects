# sap_integration.py
import requests

class SAPIntegration:
    def __init__(self):
        self.base_url = "https://your-sap-instance.com/api"
        self.api_key = "your_api_key_here"

    def create_order(self, order):
        endpoint = f"{self.base_url}/create_order"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "order_id": order.id,
            "items": [{"product_id": item.product_id, "quantity": item.quantity} for item in order.items],
            "total_amount": order.total_amount
        }
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['sap_order_id']
        else:
            raise Exception("Failed to create order in SAP")

