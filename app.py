import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv

from db import jobs_collection, upsert_jobs
from scraper.job_sources import fetch_all
from scraper.ai_classifier import annotate_job

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    q = request.args.get("q", "").strip().lower()
    role = request.args.get("role", "")
    skill = request.args.get("skill", "")
    col = jobs_collection()
    query = {}
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"company": {"$regex": q, "$options": "i"}},
            {"location": {"$regex": q, "$options": "i"}},
        ]
    if role:
        query["ai_class"] = role
    if skill:
        query["tags"] = {"$in": [skill]}
    docs = list(col.find(query).sort("published_at", -1))
    roles = sorted({d.get("ai_class","Other") for d in col.find() if d.get("ai_class")})
    all_skills = set()
    for d in col.find():
        for t in d.get("tags", []):
            all_skills.add(t)
    skills = sorted(all_skills)
    return render_template("index.html", jobs=docs, roles=roles, skills=skills, q=q, role=role, skill=skill)

@app.route("/job/<source>/<source_id>")
def job_detail(source, source_id):
    doc = jobs_collection().find_one({"source": source, "source_id": source_id})
    if not doc:
        return "Job not found", 404
    return render_template("job_detail.html", job=doc)

@app.route("/refresh", methods=["POST"])
def refresh():
    raw = fetch_all(limit_per_source=50)
    now_iso = datetime.now(timezone.utc).isoformat()
    enriched = []
    for j in raw:
        j["ingested_at"] = now_iso
        annotate_job(j)
        enriched.append(j)
    count = upsert_jobs(enriched)
    return redirect(url_for("index"))

@app.route("/api/skills")
def skills_api():
    # Returns distribution of skills for charting
    from collections import Counter
    c = Counter()
    for d in jobs_collection().find():
        for t in d.get("tags", []):
            c[t] += 1
    data = [{"skill": k, "count": v} for k, v in sorted(c.items(), key=lambda x: x[1], reverse=True)]
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV","development")=="development")