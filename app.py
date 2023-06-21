from flask import Flask
import close_incident
import os

app = Flask(__name__)


# Production code:

@app.route("/", methods=['POST'])
def handle_webhook():
    print("Webhook received")
    print(os.getenv("API_USERNAME"))
    close_incident.match_incident_to_batch()
    return "Script is running"


# Developer code:
# @app.route("/", methods=["GET"])
# def developer_mode():
#     close_incident.match_incident_to_batch()
#     return "Script is running"
#

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5004)

