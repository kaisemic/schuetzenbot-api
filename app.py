from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import time
import traceback

app = Flask(__name__)
CORS(app)

openai.api_key = "sk-..."  # API-Key hier
assistant_id = "asst_..."  # Assistant-ID hier

@app.route("/schuetzenbot", methods=["POST"])
def schuetzenbot():
    try:
        data = request.get_json()
        user_input = data.get("message", "")

        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(1)

        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        try:
            answer = messages.data[0].content[0].text.value
        except Exception as inner_e:
            traceback.print_exc()
            answer = "Fehler beim Lesen der Antwort: " + str(inner_e)

        return jsonify({"response": answer})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"response": f"Fehler: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
