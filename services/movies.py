from services import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound
import json
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

with open("{}/database/movies.json".format(root_dir()), "r") as f:
    movies = json.load(f)


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "movies": "/movies",
            "movie": "/movies/<id>"
        }
    })

@app.route("/movies/<movieid>", methods=['GET'])
@limiter.limit("60 per minute")
def movie_info(movieid):
    """Get information about a specific movie"""
    if movieid not in movies:
        raise NotFound

    result = movies[movieid]
    result["uri"] = "/movies/{}".format(movieid)

    # Structured audit logging
    logger.info("Audit log", extra={
        "action": "movie.info.retrieved",
        "resource": "movie",
        "resource_id": movieid,
        "result": "success"
    })
    return nice_json(result)


@app.route("/movies", methods=['GET'])
@limiter.limit("60 per minute")
def movie_record():
    """Get all movies in the catalog"""
    logger.info("Audit log", extra={
        "action": "movies.catalog.accessed",
        "resource": "movie_catalog",
        "result": "success"
    })
    return nice_json(movies)


if __name__ == "__main__":
    app.run(port=5001, debug=False)
