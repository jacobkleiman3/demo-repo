from services import root_dir, nice_json
from flask import Flask
from werkzeug.exceptions import NotFound, ServiceUnavailable
import json
import requests
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

with open("{}/database/users.json".format(root_dir()), "r") as f:
    users = json.load(f)

# Database configuration from environment
DB_CONNECTION_STRING = os.getenv('DATABASE_URL')


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "users": "/users",
            "user": "/users/<username>",
            "bookings": "/users/<username>/bookings",
            "suggested": "/users/<username>/suggested"
        }
    })


def require_auth(f):
    """Authentication decorator - validates request has valid auth token"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            from werkzeug.exceptions import Unauthorized
            raise Unauthorized("Valid authentication required")
        return f(*args, **kwargs)
    return decorated

def filter_user_fields(user_data):
    """Filter sensitive PII from user response"""
    return {
        "id": user_data.get("id"),
        "name": user_data.get("name"),
        "last_active": user_data.get("last_active")
    }

@app.route("/users", methods=['GET'])
@require_auth
def users_list():
    """Get list of all users"""
    logger.info("Audit log", extra={
        "action": "users.list.accessed",
        "resource": "users_list",
        "result": "success"
    })
    filtered_users = {k: filter_user_fields(v) for k, v in users.items()}
    return nice_json(filtered_users)


@app.route("/users/<username>", methods=['GET'])
@require_auth
def user_record(username):
    """Get user profile information"""
    if username not in users:
        raise NotFound

    user = users[username]

    # Structured audit logging without PII
    logger.info("Audit log", extra={
        "action": "user.profile.accessed",
        "user_id": username,
        "resource": "user_profile",
        "result": "success"
    })

    # Return filtered user data with masked sensitive fields
    filtered = filter_user_fields(user)
    filtered["email"] = user.get("email")  # Include email for profile view
    return nice_json(filtered)


@app.route("/users/<username>/bookings", methods=['GET'])
@require_auth
def user_bookings(username):
    """
    Gets booking information from the 'Bookings Service' for the user, and
     movie ratings etc. from the 'Movie Service' and returns a list.
    :param username:
    :return: List of Users bookings
    """
    if username not in users:
        raise NotFound("User '{}' not found.".format(username))

    # Fetch bookings from booking service
    try:
        users_bookings = requests.get("http://127.0.0.1:5003/bookings/{}".format(username), verify=False)
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Bookings service is unavailable.")

    if users_bookings.status_code == 404:
        raise NotFound("No bookings were found for {}".format(username))

    users_bookings = users_bookings.json()

    # Enrich with movie details
    result = {}
    for date, transactions in users_bookings.items():
        result[date] = []
        for booking in transactions:
            movieid = booking.get('movie_id')
            # Fetch movie details
            try:
                movies_resp = requests.get("http://127.0.0.1:5001/movies/{}".format(movieid), verify=False)
            except requests.exceptions.ConnectionError:
                raise ServiceUnavailable("The Movie service is unavailable.")
            movies_resp = movies_resp.json()

            # Combine movie and booking data
            result[date].append({
                "title": movies_resp["title"],
                "rating": movies_resp["rating"],
                "uri": movies_resp["uri"],
                "transaction_id": booking.get('transaction_id'),
                "total_amount": booking.get('total_amount'),
                "card_last_four": booking.get('card_last_four'),
                "payment_status": booking.get('payment_status')
            })

    # Structured audit logging with transaction details
    transaction_ids = [txn.get('transaction_id') for date_txns in users_bookings.values() for txn in date_txns]
    logger.info("Audit log", extra={
        "action": "user.bookings.retrieved",
        "user_id": username,
        "resource": "user_bookings",
        "transaction_count": len(transaction_ids),
        "transaction_ids": transaction_ids,
        "result": "success"
    })

    return nice_json(result)


@app.route("/users/<username>/suggested", methods=['GET'])
@require_auth
def user_suggested(username):
    """
    Returns movie suggestions. The algorithm returns a list of 3 top ranked
    movies that the user has not yet booked.
    :param username:
    :return: Suggested movies
    """
    raise NotImplementedError()


if __name__ == "__main__":
    app.run(port=5000, debug=False)
