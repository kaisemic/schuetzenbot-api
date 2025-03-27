from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import time
import traceback
import logging
import os

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Umgebungsvariablen laden
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

openai.api_key = api_key

logging.info("OPENAI_API_KEY gesetzt: %s", bool(api_key))
logging.info("OPENAI_ASSISTANT_ID gesetzt: %s", bool(assistant_id))


@app.route("/schuetzenbot", methods=["POST"])
def schuetzenbot():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        thread_id = data.get("thread_id")

        # Wenn kein Thread vorhanden ist, einen neuen erstellen
        if not thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id

        # Nachricht hinzufügen
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # Assistant-Run starten
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Warten, bis der Run abgeschlossen ist
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(1)

        # Antwort abrufen
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        try:
            answer = messages.data[0].content[0].text.value
        except Exception as inner_e:
            traceback.print_exc()
            answer = "Fehler beim Lesen der Antwort: " + str(inner_e)

        return jsonify({
            "response": answer,
            "thread_id": thread_id
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "response": f"Fehler: {str(e)}",
            "thread_id": thread_id if 'thread_id' in locals() else None
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
