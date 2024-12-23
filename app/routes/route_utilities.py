from flask import abort, make_response
from app.db import db
import os, requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

def create_model(cls, model_data):
    try:
        model = cls.from_dict(model_data)

    except KeyError as error:
        response = {"details": f"Invalid data"}
        abort(make_response(response, 400))

    db.session.add(model)
    db.session.commit()

    return model.to_dict()


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)

    except ValueError:
        response = {"message": f"Invalid request: {cls.__name__} id {model_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)
    if model:
        return model
    
    response = {"message": f"Invalid request: {cls.__name__} {model_id} not found"}
    abort(make_response(response, 404))


def send_slack_message(task_title):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    request_body = {
        "channel": CHANNEL_ID,
        "text": f"Someone just completed the task {task_title}"
        }

    try:
        response = requests.post(url=url, headers=headers, json=request_body)
        response.raise_for_status()
        return response.json()
    
    except:
        abort(make_response({"message": "Unknkown request"}, 400))

    