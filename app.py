from dataclasses import asdict
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from flask import Flask, Response, jsonify, redirect, render_template, request, send_file, session, url_for

from feature_engine import (
    build_feature_pack,
    build_ics,
    build_second_life_plan,
    create_text_pdf,
    mentor_reply,
)
from models import UserProfile
from recommender import LifeCompassRecommender, SubmissionStore

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
RESULTS_DIR = STATIC_DIR / "results"

app = Flask(__name__)
app.secret_key = "lifecompass-dev-secret"

recommender = LifeCompassRecommender(DATA_DIR / "careers.csv")
submission_store = SubmissionStore(DATA_DIR / "submissions.csv")

DOMAINS = ("technology", "science", "creative", "sports", "business")

CAREER_QUESTION_SCORES = {
    "q_curiosity": {
        "build_app": {"technology": 3, "business": 1},
        "run_experiment": {"science": 3, "technology": 1},
        "make_song": {"creative": 3},
        "train_match": {"sports": 3},
        "launch_idea": {"business": 3, "creative": 1},
    },
    "q_problem": {
        "logic": {"technology": 2, "science": 2},
        "people": {"business": 2, "creative": 1},
        "expression": {"creative": 3},
        "performance": {"sports": 2, "creative": 1},
        "systems": {"technology": 2, "business": 2},
    },
    "q_workday": {
        "laptop": {"technology": 3},
        "lab": {"science": 3},
        "studio": {"creative": 3},
        "ground": {"sports": 3},
        "market": {"business": 3},
    },
    "q_success": {
        "useful_tool": {"technology": 3, "business": 1},
        "new_discovery": {"science": 3},
        "moving_people": {"creative": 3},
        "championship": {"sports": 3},
        "independent_venture": {"business": 3},
    },
    "q_learning": {
        "coding_ai": {"technology": 3},
        "bio_health": {"science": 3},
        "editing_music": {"creative": 3},
        "fitness_drills": {"sports": 3},
        "money_marketing": {"business": 3},
    },
}

BALANCE_QUESTION_SCORES = {
    "q_missed_activity": {
        "making_things": {"creative": 2, "technology": 1},
        "movement": {"sports": 3},
        "learning": {"science": 2, "technology": 1},
        "building_income": {"business": 3},
        "sharing_voice": {"creative": 2, "business": 1},
    },
    "q_small_step": {
        "twenty_code": {"technology": 3},
        "read_research": {"science": 3},
        "record_create": {"creative": 3},
        "train_body": {"sports": 3},
        "sell_idea": {"business": 3},
    },
    "q_restore": {
        "quiet_learning": {"science": 1, "technology": 1},
        "creative_play": {"creative": 3},
        "physical_reset": {"sports": 3},
        "talking_people": {"business": 2, "creative": 1},
        "structured_plan": {"technology": 1, "business": 1, "science": 1},
    },
}

BALANCE_STATE = {
    "exhausted": {"stress_level": 5, "energy_level": 1, "available_time": "low"},
    "stretched": {"stress_level": 4, "energy_level": 2, "available_time": "low"},
    "flat": {"stress_level": 3, "energy_level": 2, "available_time": "medium"},
    "restless": {"stress_level": 3, "energy_level": 4, "available_time": "medium"},
    "ready": {"stress_level": 2, "energy_level": 5, "available_time": "high"},
}

ANSWER_TO_HOBBIES = {
    "build_app": ["coding"],
    "run_experiment": ["biology research"],
    "make_song": ["music"],
    "train_match": ["cricket", "fitness"],
    "launch_idea": ["startup ideas"],
    "expression": ["writing", "music"],
    "performance": ["cricket", "music"],
    "studio": ["music", "photography"],
    "ground": ["cricket", "fitness"],
    "moving_people": ["writing", "music"],
    "championship": ["cricket"],
    "editing_music": ["music"],
    "fitness_drills": ["fitness"],
    "making_things": ["writing", "music"],
    "movement": ["fitness"],
    "record_create": ["music"],
    "train_body": ["fitness"],
    "creative_play": ["music", "writing"],
    "physical_reset": ["fitness"],
}

ANSWER_TO_SKILLS = {
    "build_app": ["python"],
    "coding_ai": ["python"],
    "logic": ["maths"],
    "systems": ["leadership"],
    "people": ["communication"],
    "market": ["communication", "leadership"],
    "money_marketing": ["communication"],
    "sell_idea": ["communication", "leadership"],
    "editing_music": ["editing"],
    "record_create": ["editing"],
    "performance": ["teamwork"],
    "train_match": ["teamwork"],
    "fitness_drills": ["teamwork"],
    "bio_health": ["maths"],
}

ANSWER_TO_PERSONALITY = {
    "logic": ["analytical"],
    "systems": ["analytical", "independent"],
    "run_experiment": ["curious"],
    "new_discovery": ["curious"],
    "make_song": ["creative"],
    "expression": ["creative"],
    "moving_people": ["creative", "social"],
    "train_match": ["disciplined"],
    "championship": ["disciplined"],
    "launch_idea": ["independent"],
    "independent_venture": ["independent"],
    "people": ["social"],
    "talking_people": ["social"],
    "structured_plan": ["disciplined"],
    "quiet_learning": ["curious"],
}


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def unique(values):
    seen = set()
    cleaned = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            cleaned.append(value)
    return cleaned


def score_answers(form, question_scores):
    scores = {domain: 0 for domain in DOMAINS}
    answers = []

    for question, options in question_scores.items():
        answer = form.get(question, "")
        if not answer:
            continue
        answers.append(answer)
        for domain, value in options.get(answer, {}).items():
            scores[domain] += value

    return scores, answers


def infer_profile_signals(answers, extra_hobbies=None, extra_skills=None, extra_traits=None):
    hobbies = []
    skills = []
    personality = []

    for answer in answers:
        hobbies.extend(ANSWER_TO_HOBBIES.get(answer, []))
        skills.extend(ANSWER_TO_SKILLS.get(answer, []))
        personality.extend(ANSWER_TO_PERSONALITY.get(answer, []))

    hobbies.extend(extra_hobbies or [])
    skills.extend(extra_skills or [])
    personality.extend(extra_traits or [])
    return unique(hobbies), unique(skills), unique(personality)


def create_chart(scores):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"interest-chart-{uuid4().hex}.png"
    chart_path = RESULTS_DIR / filename

    labels = list(scores.keys())
    values = list(scores.values())
    colors = ["#6f5cff", "#20d6c7", "#ff4f9a", "#ff7a59", "#9fd94a"]

    fig, ax = plt.subplots(figsize=(8, 4.6))
    bars = ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_ylim(0, 110)
    ax.set_ylabel("Score")
    ax.set_title("Interest Distribution")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.22)
    ax.bar_label(bars, fmt="%.0f", padding=3)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=140)
    plt.close(fig)

    return f"results/{filename}"


def result_to_payload(result):
    return {
        "mode": result.mode,
        "headline": result.headline,
        "summary": result.summary,
        "scores": result.scores,
        "primary_paths": [asdict(item) for item in result.primary_paths],
        "secondary_paths": [asdict(item) for item in result.secondary_paths],
        "balance_plan": result.balance_plan,
        "side_skills": result.side_skills,
        "chart_filename": result.chart_filename,
    }


def profile_to_payload(profile):
    return {
        "name": profile.name,
        "mode": profile.mode,
        "interests": profile.interests,
        "hobbies": profile.hobbies,
        "skills": profile.skills,
        "personality": profile.personality,
        "current_field": profile.current_field,
        "stress_level": profile.stress_level,
        "energy_level": profile.energy_level,
        "available_time": profile.available_time,
        "support_preference": profile.support_preference,
    }


def current_context():
    result_data = session.get("result")
    profile_data = session.get("profile")
    if not result_data or not profile_data:
        return None, None, None
    features = build_feature_pack(result_data, profile_data)
    return result_data, profile_data, features


def ai_mentor_answer(message, result):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
            prompt = (
                "You are LifeCompass AI Mentor. Give honest, practical career advice with backup options. "
                f"Current recommendation data: {json.dumps(result)[:2500]}. User asks: {message}"
            )
            payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent"
                f"?key={gemini_key}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, TimeoutError, URLError, OSError, json.JSONDecodeError):
            pass

    try:
        prompt = (
            "You are LifeCompass AI Mentor. Be honest, practical, and include backup options. "
            f"Recommendation: {json.dumps(result)[:1800]}. User: {message}"
        )
        payload = json.dumps({"model": "llama3.2", "prompt": prompt, "stream": False}).encode("utf-8")
        req = Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("response") or mentor_reply(message, result)
    except (TimeoutError, URLError, OSError, json.JSONDecodeError):
        return mentor_reply(message, result)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/career-discovery", methods=["GET", "POST"])
def mode1():
    if request.method == "POST":
        interests, answers = score_answers(request.form, CAREER_QUESTION_SCORES)
        hobbies, skills, personality = infer_profile_signals(
            answers,
            request.form.getlist("hobbies"),
            request.form.getlist("skills"),
            request.form.getlist("personality"),
        )
        profile = UserProfile(
            name=request.form.get("name", "Friend").strip() or "Friend",
            mode="career",
            interests=interests,
            hobbies=hobbies,
            skills=skills,
            personality=personality,
        )
        result = recommender.recommend_careers(profile)
        result.chart_filename = create_chart(result.scores)
        submission_store.append(profile, result)
        session["result"] = result_to_payload(result)
        session["profile"] = profile_to_payload(profile)
        session["name"] = profile.name
        return redirect(url_for("result"))

    return render_template("mode1.html")


@app.route("/balance-rediscovery", methods=["GET", "POST"])
def mode2():
    if request.method == "POST":
        interests, answers = score_answers(request.form, BALANCE_QUESTION_SCORES)
        state = BALANCE_STATE.get(request.form.get("q_state", ""), BALANCE_STATE["flat"])
        hobbies, skills, personality = infer_profile_signals(
            answers,
            request.form.getlist("hobbies"),
            ["communication"],
            request.form.getlist("personality"),
        )
        profile = UserProfile(
            name=request.form.get("name", "Friend").strip() or "Friend",
            mode="balance",
            interests=interests,
            hobbies=hobbies,
            skills=skills,
            personality=personality,
            current_field=request.form.get("current_field", "").strip(),
            stress_level=state["stress_level"],
            energy_level=state["energy_level"],
            available_time=state["available_time"],
            support_preference=request.form.get("support_preference", ""),
        )
        result = recommender.recommend_balance(profile)
        result.chart_filename = create_chart(result.scores)
        submission_store.append(profile, result)
        session["result"] = result_to_payload(result)
        session["profile"] = profile_to_payload(profile)
        session["name"] = profile.name
        return redirect(url_for("result"))

    return render_template("mode2.html")


@app.route("/result")
def result():
    result_data = session.get("result")
    if not result_data:
        return redirect(url_for("home"))
    return render_template("result.html", result=result_data, name=session.get("name", "Friend"))


@app.route("/dashboard")
def dashboard():
    result_data, profile_data, features = current_context()
    if not features:
        return redirect(url_for("home"))
    return render_template("dashboard.html", result=result_data, profile=profile_data, features=features)


@app.route("/mentor")
def mentor():
    result_data, _, features = current_context()
    if not features:
        return redirect(url_for("home"))
    return render_template("mentor.html", result=result_data, features=features)


@app.route("/api/mentor", methods=["POST"])
def mentor_api():
    result_data, _, _ = current_context()
    if not result_data:
        return jsonify({"reply": "Start with Career Discovery first so I can answer using your recommendation."})
    message = request.json.get("message", "") if request.is_json else request.form.get("message", "")
    return jsonify({"reply": ai_mentor_answer(message, result_data)})


@app.route("/burnout-tracker", methods=["GET", "POST"])
def burnout_tracker():
    _, profile_data, features = current_context()
    if not features:
        return redirect(url_for("mode2"))
    assessment = None
    if request.method == "POST":
        total = sum(safe_int(request.form.get(f"q{i}")) for i in range(1, 11))
        if total >= 38:
            level = "High burnout risk"
        elif total >= 24:
            level = "Moderate burnout risk"
        else:
            level = "Manageable load"
        assessment = {"score": total, "level": level}
    return render_template("burnout.html", profile=profile_data, burnout=features["burnout"], assessment=assessment)


@app.route("/second-life", methods=["GET", "POST"])
def second_life():
    _, _, features = current_context()
    plan = None
    if request.method == "POST":
        plan = build_second_life_plan(request.form)
    preview = features["second_life"] if features else None
    return render_template("second_life.html", preview=preview, plan=plan)


@app.route("/timeline.ics")
def timeline_ics():
    _, _, features = current_context()
    if not features:
        return redirect(url_for("home"))
    return Response(
        build_ics(features["timeline"]),
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=lifecompass-timeline.ics"},
    )


@app.route("/export/report.pdf")
def export_report_pdf():
    result_data, _, features = current_context()
    if not features:
        return redirect(url_for("home"))
    sections = [
        ("Recommendation", result_data["headline"]),
        ("Summary", result_data["summary"]),
        ("Skill Gap", [f"Missing: {', '.join(features['skill_gap']['missing'])}", features["skill_gap"]["transition_time"]]),
        ("Financial Reality", [f"{item['career']}: {item['salary']} | Demand: {item['demand']}" for item in features["financials"]]),
        ("7-Day Trial", [f"Day {item['day']}: {item['task']}" for item in features["trial"]]),
        ("India Links", [f"{item['name']}: {item['url']}" for item in features["india"]["schemes"]]),
    ]
    return send_file(create_text_pdf("LifeCompass Guidance Report", sections), download_name="lifecompass-report.pdf", as_attachment=True)


@app.route("/export/resume.pdf")
def export_resume_pdf():
    _, _, features = current_context()
    if not features:
        return redirect(url_for("home"))
    resume = features["resume"]
    sections = [
        ("Headline", resume["headline"]),
        ("Summary", resume["summary"]),
        ("Transferable Skills", resume["transferable_skills"]),
        ("Suggested Projects", resume["projects"]),
        ("Courses", resume["courses"]),
        ("Job Portal Keywords", resume["keywords"]),
    ]
    return send_file(create_text_pdf("LifeCompass Transferable Resume", sections), download_name="lifecompass-resume.pdf", as_attachment=True)


@app.route("/feedback/not-interested", methods=["POST"])
def not_interested():
    DATA_DIR.mkdir(exist_ok=True)
    row = {
        "career": request.form.get("career", ""),
        "reason": request.form.get("reason", ""),
        "timestamp": datetime.now().isoformat(),
    }
    feedback_path = DATA_DIR / "feedback.csv"
    header = not feedback_path.exists()
    with feedback_path.open("a", encoding="utf-8") as file:
        if header:
            file.write("career,reason,timestamp\n")
        file.write(f'"{row["career"]}","{row["reason"]}","{row["timestamp"]}"\n')
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
