from flask import Flask, jsonify, request
from twilio.rest import Client
from os import environ

app = Flask(__name__)

# Load environment variables
app.config["TWILIO_ACCOUNT_SID"] = environ.get("TWILIO_ACCOUNT_SID")
app.config["TWILIO_AUTH_TOKEN"] = environ.get("TWILIO_AUTH_TOKEN")
app.config["TWILIO_CALLER_ID"] = environ.get("TWILIO_CALLER_ID")
app.config["PHONE_NUMBER"] = environ.get("PHONE_NUMBER")


# Voice Request URL
@app.route("/call", methods=["POST"])
def call():
    phone_number = app.config["PHONE_NUMBER"]

    try:
        twilio_client = Client(
            app.config["TWILIO_ACCOUNT_SID"], app.config["TWILIO_AUTH_TOKEN"]
        )
    except Exception as e:
        msg = "Missing configuration variable: {0}".format(e)
        return jsonify({"error": msg}), 400

    content = request.json
    msg = f"You have {len(content['alerts'])} alerts. {', '.join([str(alert['annotations']['summary']) for alert in content['alerts']])}"

    try:
        res = twilio_client.calls.create(
            from_=app.config["TWILIO_CALLER_ID"],
            to=phone_number,
            url="https://twimlets.com/message?Message[0]={0}".format(msg),
        )
    except Exception as e:
        app.logger.error(e)
        message = e.msg if hasattr(e, "msg") else str(e)
        return jsonify({"error": message}), 400

    return jsonify({"message": "Call incoming!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
