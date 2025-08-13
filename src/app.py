from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SHIPPO_API_TOKEN = os.getenv("SHIPPO_API_TOKEN")
if not SHIPPO_API_TOKEN:
    raise ValueError("SHIPPO_API_TOKEN not set in environment or .env file")

SHIPPO_API_URL = "https://api.goshippo.com/shipments/"

HEADERS = {
    "Authorization": f"ShippoToken {SHIPPO_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_shippo_rates(package_details):
    """
    Get shipping rates from Shippo API for the given package dimensions and addresses
    """

    # Get addresses from user input
    address_from = package_details.get("address_from", {})
    address_to = package_details.get("address_to", {})
    
    # format addresses for Shippo API
    def format_address(addr, addr_type):
        if not addr:
            raise ValueError(f"{addr_type} address is required")
        
        required_fields = ["name", "street1", "city", "state", "zip"]
        missing_fields = [field for field in required_fields if not addr.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in {addr_type} address: {', '.join(missing_fields)}")
        
        return {
            "name": addr["name"].strip(),
            "street1": addr["street1"].strip(),
            "city": addr["city"].strip(),
            "state": addr["state"].strip(),
            "zip": addr["zip"].strip(),
            "country": "US"
        }
    
    try:
        address_from = format_address(address_from, "from")
        address_to = format_address(address_to, "to")
    except ValueError as e:
        print(f"Address validation error: {e}")
        raise

    parcel = {
        "length": str(package_details["length"]),
        "width": str(package_details["width"]),
        "height": str(package_details["height"]),
        "distance_unit": "in",
        "weight": str(package_details["weight"]),
        "mass_unit": "lb"
    }

    payload = {
        "address_from": address_from,
        "address_to": address_to,
        "parcels": [parcel],
        "async": False,
        "carrier_accounts": [],
        "extra": {
            "include_rates": True
        }
    }

    try:
        response = requests.post(SHIPPO_API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        shipment = response.json()

        # Count carriers for logging
        carriers_found = set()
        for rate in shipment.get("rates", []):
            carriers_found.add(rate["provider"])
        
        print(f"Found {len(carriers_found)} carriers: {', '.join(sorted(carriers_found))}")

        rates = shipment.get("rates", [])
        results = []
        for rate in rates:
            # Get delivery time from API or infer from service name
            delivery_days = rate.get('days')
            service_name = rate["servicelevel"]["name"].lower()
            
            if delivery_days:
                delivery_time = f"{delivery_days} days"
            else:
                # Infer delivery time from service name
                if "priority mail express" in service_name or "next day air" in service_name:
                    delivery_time = "1 day"
                elif "2nd day air" in service_name or "second day air" in service_name:
                    delivery_time = "2 days"
                elif "priority mail" in service_name or "3 day select" in service_name:
                    delivery_time = "3 days"
                elif "ground advantage" in service_name or "ground" in service_name:
                    delivery_time = "5 days"
                else:
                    delivery_time = "N/A"
            
            results.append({
                "carrier": rate["provider"],
                "service": rate["servicelevel"]["name"],
                "price": float(rate["amount"]),
                "delivery_time": delivery_time
            })

        return results

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

@app.route("/")
def index():
    """Show the main page"""
    return render_template("index.html")

@app.route("/compare", methods=["POST"])
def compare():
    data = request.get_json()

    try:
        results = get_shippo_rates(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    # Helper function to extract delivery days for comparison
    def delivery_days(carrier):
        try:
            dt = carrier["delivery_time"]
            if dt.lower() == "n/a":
                # Try to infer delivery time from service name
                service_name = carrier["service"].lower()
                
                # USPS services
                if "priority mail express" in service_name:
                    return 1
                elif "priority mail" in service_name:
                    return 3
                elif "ground advantage" in service_name:
                    return 5
                
                # UPS services
                elif "next day air" in service_name:
                    return 1
                elif "2nd day air" in service_name or "second day air" in service_name:
                    return 2
                elif "3 day select" in service_name:
                    return 3
                elif "ground" in service_name:
                    return 5
                
                # Default for unknown services
                return None
            return int(dt.split()[0])
        except:
            return None

    # Mark cheapest and fastest options
    if results:
        min_price = min(c["price"] for c in results)
        
        # Only consider services with actual delivery time data for fastest
        services_with_delivery = [c for c in results if delivery_days(c) is not None]
        min_days = min(delivery_days(c) for c in services_with_delivery) if services_with_delivery else None

        for c in results:
            c["is_cheapest"] = (c["price"] == min_price)
            # Only mark as fastest if we have delivery time data and it's the minimum
            c["is_fastest"] = (delivery_days(c) is not None and delivery_days(c) == min_days) if min_days else False

    return jsonify({
        "status": "success",
        "package_details": data,
        "results": results
    })


if __name__ == "__main__":
    app.run(debug=True)
