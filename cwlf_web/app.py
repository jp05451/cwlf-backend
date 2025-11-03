from flask import Flask
from app import create_app
from config import Config
import argparse

app = create_app()

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Flask web application.")
    parser.add_argument(
        "--host",
        type=str,
        default=Config.HOST,
        help="Host address to run the Flask app (default: %(default)s)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=Config.PORT,
        help="Port number to run the Flask app (default: %(default)s)",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    app.run(host=args.host, port=args.port, debug=Config.DEBUG)