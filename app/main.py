from flask import Flask, render_template, request, Response, abort, jsonify
import os, time, json, hashlib
from . import db, responses

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

# 1️⃣ Kick‑off
@app.post("/start")
def start():
    q = request.json["query"]
    run = responses.start_research(
        q,
        f"{request.url_root}webhook?token={os.environ['WEBHOOK_TOKEN']}"
    )
    db.current.create_item({"id": run.id, "status": "running"})
    return {"run_id": run.id}, 202

# 2️⃣ Webhook
@app.post("/webhook")
def webhook():
    if request.args.get("token") != os.environ["WEBHOOK_TOKEN"]:
        abort(403)
    payload = request.get_json()
    run_id = payload["response"]["id"]
    text = payload["response"]["choices"][0]["message"]["content"]
    now = time.time()

    db.current.upsert_item({"id": run_id, "status": "done", "report": text})
    db.history.create_item({"run_id": run_id, "ts": now, "report": text})
    return "", 200

# 3️⃣ SSE stream
@app.get("/stream/<run_id>")
def stream(run_id):
    def gen():
        last = None
        while True:
            doc = db.current.read_item(run_id, run_id)
            if doc.get("report") != last:
                last = doc.get("report")
                yield f"data: {json.dumps({'report': last})}\n\n"
            if doc["status"] != "running":
                break
            time.sleep(2)
    return Response(gen(), mimetype="text/event-stream")

# 4️⃣ Edit selected text
@app.post("/edit")
def edit():
    data = request.json
    edited = responses.edit_snippet(data["original"], data["instruction"])
    doc = db.current.read_item(data["run_id"], data["run_id"])
    new_report = doc["report"].replace(data["original"], edited)
    now = time.time()
    db.current.upsert_item({"id": data["run_id"], "status": "done", "report": new_report})
    db.history.create_item({"run_id": data["run_id"], "ts": now, "report": new_report})
    return {"report": new_report}

# 5️⃣ Rollback
@app.post("/rollback")
def rollback():
    data = request.json
    query = f"SELECT * FROM c WHERE c.run_id=@rid AND c.ts=@ts"
    items = list(db.history.query_items(query,
                parameters=[{"name":"@rid","value":data["run_id"]},
                            {"name":"@ts","value":data["ts"]}],
                enable_cross_partition_query=True))
    if not items:
        abort(404)
    db.current.upsert_item({"id": data["run_id"], "status": "rolled", "report": items[0]["report"]})
    return {"report": items[0]["report"]}