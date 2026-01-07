from services import root_dir, nice_json
from flask import Flask
from werkzeug.exceptions import NotFound
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

with open("{}/database/showtimes.json".format(root_dir()), "r") as f:
    showtimes = json.load(f)


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "showtimes": "/showtimes",
            "showtime": "/showtimes/<date>"
        }
    })


from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

@app.route("/showtimes", methods=['GET'])
@limiter.limit("60 per minute")
def showtimes_list():
    logger.info("Audit log", extra={
        "action": "showtimes.list.accessed",
        "resource": "showtimes_list",
        "result": "success"
    })
    return nice_json(showtimes)


@app.route("/showtimes/<date>", methods=['GET'])
@limiter.limit("60 per minute")
def showtimes_record(date):
    if date not in showtimes:
        raise NotFound

    logger.info("Audit log", extra={
        "action": "showtimes.date.accessed",
        "resource": "showtimes",
        "resource_id": date,
        "result": "success"
    })

    return nice_json(showtimes[date])

if __name__ == "__main__":
    # Debug mode disabled for production security
    app.run(port=5002, debug=False)
