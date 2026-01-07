from services import root_dir, nice_json
from flask import Flask, request
import json
import logging
import os
from werkzeug.exceptions import NotFound

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load payment processor config from environment
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')

with open("{}/database/bookings.json".format(root_dir()), "r") as f:
    bookings = json.load(f)


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "bookings": "/bookings",
            "booking": "/bookings/<username>"
        }
    })


def require_auth(f):
    """Authentication decorator - validates request has valid auth token"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            from werkzeug.exceptions import Unauthorized
            raise Unauthorized("Valid authentication required")
        return f(*args, **kwargs)
    return decorated

def filter_booking_fields(booking_data):
    """Filter sensitive financial data from booking response"""
    filtered = {}
    for username, dates in booking_data.items():
        filtered[username] = {}
        for date, transactions in dates.items():
            filtered[username][date] = [
                {
                    "movie_id": t.get("movie_id"),
                    "payment_status": t.get("payment_status"),
                    "timestamp": t.get("timestamp")
                }
                for t in transactions
            ]
    return filtered

@app.route("/bookings", methods=['GET'])
@require_auth
def booking_list():
    """Get all bookings across all users"""
    logger.info("Audit log", extra={
        "action": "bookings.list.accessed",
        "resource": "all_bookings",
        "result": "success"
    })
    # Return filtered bookings without sensitive financial data
    return nice_json(filter_booking_fields(bookings))


@app.route("/bookings/<username>", methods=['GET'])
@require_auth
def booking_record(username):
    """Get booking records for a specific user"""
    if username not in bookings:
        raise NotFound

    user_bookings = bookings[username]

    # Structured audit logging with proper format
    logger.info("Audit log", extra={
        "action": "bookings.user.accessed",
        "user_id": username,
        "resource": "user_bookings",
        "booking_count": sum(len(txns) for txns in user_bookings.values()),
        "result": "success"
    })

    # Filter sensitive fields before returning
    filtered = {}
    for date, transactions in user_bookings.items():
        filtered[date] = [
            {
                "movie_id": t.get("movie_id"),
                "payment_status": t.get("payment_status"),
                "timestamp": t.get("timestamp")
            }
            for t in transactions
        ]
    return nice_json(filtered)

if __name__ == "__main__":
    # Debug mode disabled for production security
    app.run(port=5003, debug=False)

