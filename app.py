"""
app.py — Growth GPT: Digital Twin Marketing Simulator
Flask application entrypoint.
"""
import os
import re
from functools import wraps
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

import db
import gemini_service
import reports_export

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
# Keep users signed in across requests/tabs instead of the session silently
# expiring, which is the most common reason sign-in "doesn't work".
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)

db.init_db()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to continue.", "error")
            return redirect(url_for("auth", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    user = None
    if session.get("user_id"):
        user = db.get_user_by_id(session["user_id"])
    return {"current_user": user}


@app.route("/")
def index():
    recent = db.list_campaigns(limit=6)
    return render_template("index.html", recent=recent)


@app.route("/simulate", methods=["GET"])
@login_required
def simulate_form():
    return render_template("simulate.html")


@app.route("/simulate", methods=["POST"])
@login_required
def simulate_run():
    data = {
        "campaign_name": request.form.get("campaign_name", "").strip(),
        "product_name": request.form.get("product_name", "").strip(),
        "objective": request.form.get("objective", "Engagement"),
        "category": request.form.get("category", "").strip(),
        "product_description": request.form.get("product_description", "").strip(),
        "price": request.form.get("price", "").strip(),
        "target_audience": request.form.get("target_audience", "").strip(),
        "age": request.form.get("age", "").strip(),
        "gender": request.form.get("gender", "Any"),
        "income": request.form.get("income", "").strip(),
        "occupation": request.form.get("occupation", "").strip(),
        "location": request.form.get("location", "").strip(),
        "interests": request.form.get("interests", "").strip(),
        "marketing_platform": request.form.get("marketing_platform", "").strip(),
        "headline": request.form.get("headline", "").strip(),
        "campaign_message": request.form.get("campaign_description", "").strip(),
        "campaign_description": request.form.get("campaign_description", "").strip(),
        "cta": request.form.get("cta", "").strip(),
        "offer": request.form.get("offer", "").strip(),
        "competitor_names": request.form.get("competitor_names", "").strip(),
        "budget": request.form.get("budget", "").strip(),
        "campaign_duration": request.form.get("campaign_duration", "").strip(),
    }

    if not data["campaign_name"] or not data["product_name"]:
        flash("Campaign Name and Product Name are required to run a simulation.", "error")
        return redirect(url_for("simulate_form"))

    # Optional: handle uploaded file
    ad_image = request.files.get("advertisement_image")
    image_bytes = None
    image_mime_type = None
    if ad_image and ad_image.filename:
        image_bytes = ad_image.read()
        image_mime_type = ad_image.mimetype
        data["advertisement_image"] = ad_image.filename
    else:
        data["advertisement_image"] = ""

    result = gemini_service.run_simulation(data, image_bytes, image_mime_type)
    campaign_id = db.save_campaign(data, result)

    return redirect(url_for("results", campaign_id=campaign_id))


@app.route("/api/simulate_scenario", methods=["POST"])
@login_required
def simulate_scenario():
    req_data = request.json or {}
    campaign_id = req_data.get("campaign_id")
    if not campaign_id:
        return jsonify({"error": "Campaign ID required"}), 400
        
    record = db.get_campaign(campaign_id)
    if not record:
        return jsonify({"error": "Campaign not found"}), 404
        
    result_json = record.get("result", {})
    overview = result_json.get("campaign_overview", {})
    
    # Reconstruct original input data
    original_data = {
        "campaign_name": overview.get("campaign_name") or record.get("product_name"),
        "product_name": record.get("product_name"),
        "product_description": record.get("product_description"),
        "target_audience": record.get("target_audience"),
        "campaign_message": record.get("campaign_message"),
        "campaign_description": record.get("campaign_message"),
        "objective": record.get("objective"),
        "budget": record.get("budget"),
    }
    
    updates = {
        "price": req_data.get("price"),
        "offer": req_data.get("offer"),
        "cta": req_data.get("cta"),
        "target_audience": req_data.get("target_audience"),
        "marketing_platform": req_data.get("marketing_platform"),
    }
    
    new_result = gemini_service.run_scenario_simulation(original_data, updates)
    
    def get_val(pred, key):
        node = pred.get(key, {})
        if isinstance(node, dict):
            return node.get("value")
        return node

    before = {
        "overall_score": result_json.get("campaign_overview", {}).get("overall_score") or record.get("engagement_score"),
        "engagement_score": get_val(result_json.get("predictions", {}), "engagement_score") or record.get("engagement_score"),
        "conversion_probability": get_val(result_json.get("predictions", {}), "conversion_probability") or record.get("conversion_probability"),
        "readiness_score": result_json.get("readiness", {}).get("readiness_score") or record.get("engagement_score"),
        "risk_level": result_json.get("readiness", {}).get("risk_level") or record.get("growth_potential")
    }
    
    after = {
        "overall_score": new_result.get("campaign_overview", {}).get("overall_score"),
        "engagement_score": get_val(new_result.get("predictions", {}), "engagement_score"),
        "conversion_probability": get_val(new_result.get("predictions", {}), "conversion_probability"),
        "readiness_score": new_result.get("readiness", {}).get("readiness_score"),
        "risk_level": new_result.get("readiness", {}).get("risk_level")
    }
    
    return jsonify({
        "before": before,
        "after": after
    })


@app.route("/results/<int:campaign_id>")
@login_required
def results(campaign_id):
    record = db.get_campaign(campaign_id)
    if not record:
        flash("Campaign not found.", "error")
        return redirect(url_for("index"))
    return render_template("results.html", campaign=record, result=record["result"])


@app.route("/dashboard")
@login_required
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


@app.route("/history")
@login_required
def history():
    campaigns = db.list_campaigns(limit=100)
    return render_template("history.html", campaigns=campaigns)


@app.route("/reports")
@login_required
def reports():
    campaigns = db.list_campaigns(limit=200)
    return render_template("reports.html", campaigns=campaigns)


@app.route("/reports/<int:campaign_id>")
@login_required
def report_detail(campaign_id):
    record = db.get_campaign(campaign_id)
    if not record:
        flash("Campaign not found.", "error")
        return redirect(url_for("reports"))
    return render_template("report_detail.html", campaign=record, result=record["result"])


@app.route("/launch-analysis/<int:campaign_id>")
@login_required
def launch_analysis(campaign_id):
    record = db.get_campaign(campaign_id)
    if not record:
        flash("Campaign not found.", "error")
        return redirect(url_for("history"))
        
    # Retrieve conversion probability and engagement score safely from database columns or prediction objects
    conv = record.get("conversion_probability")
    eng = record.get("engagement_score")

    if conv is None or eng is None:
        preds = record.get("result", {}).get("predictions", {})
        if isinstance(preds, dict):
            conv_val = preds.get("conversion_probability", {})
            eng_val = preds.get("engagement_score", {})
            if isinstance(conv_val, dict):
                conv = conv_val.get("value", 0)
            else:
                conv = conv_val
            if isinstance(eng_val, dict):
                eng = eng_val.get("value", 0)
            else:
                eng = eng_val
        
        # Fallback to growth_prediction
        if conv is None or eng is None:
            gp = record.get("result", {}).get("growth_prediction", {}) or {}
            conv = gp.get("conversion_probability", 0)
            eng = gp.get("engagement_score", 0)

    conv = int(conv) if conv is not None else 0
    eng = int(eng) if eng is not None else 0
    
    if conv >= 75 and eng >= 70:
        decision = "GO - READY FOR LAUNCH"
        color = "sage"
        emoji = "🚀"
        reason = "Outstanding conversion and engagement probability. The product strongly resonates with the target audience."
    elif conv >= 50 or eng >= 50:
        decision = "MAYBE - NEEDS REFINEMENT"
        color = "amber"
        emoji = "⚠️"
        reason = "Mixed signals from the digital twins. Consider tweaking the campaign message or targeting before a full launch."
    else:
        decision = "NO - DO NOT LAUNCH"
        color = "coral"
        emoji = "🛑"
        reason = "Low conversion and engagement intent. The current offering or messaging does not resonate with the audience."

    return render_template(
        "launch_analysis.html", 
        campaign=record, 
        result=record["result"],
        decision=decision,
        color=color,
        emoji=emoji,
        reason=reason
    )


@app.route("/reports/<int:campaign_id>/export/<fmt>")
@login_required
def report_export(campaign_id, fmt):
    record = db.get_campaign(campaign_id)
    if not record:
        flash("Campaign not found.", "error")
        return redirect(url_for("reports"))

    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", record.get("product_name") or "campaign").strip("_") or "campaign"

    if fmt == "csv":
        data = reports_export.campaign_csv(record)
        return Response(data, mimetype="text/csv", headers={
            "Content-Disposition": f"attachment; filename={safe_name}_report.csv"
        })
    if fmt == "xlsx":
        data = reports_export.campaign_xlsx(record)
        return Response(data, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
            "Content-Disposition": f"attachment; filename={safe_name}_report.xlsx"
        })
    if fmt == "pdf":
        data = reports_export.campaign_pdf(record)
        return Response(data, mimetype="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={safe_name}_report.pdf"
        })

    flash("Unsupported export format.", "error")
    return redirect(url_for("report_detail", campaign_id=campaign_id))


@app.route("/reports/export-all/<fmt>")
@login_required
def report_export_all(fmt):
    campaigns = db.list_campaigns(limit=1000)

    if fmt == "csv":
        data = reports_export.all_campaigns_csv(campaigns)
        return Response(data, mimetype="text/csv", headers={
            "Content-Disposition": "attachment; filename=growthgpt_all_campaigns.csv"
        })
    if fmt == "xlsx":
        data = reports_export.all_campaigns_xlsx(campaigns)
        return Response(data, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
            "Content-Disposition": "attachment; filename=growthgpt_all_campaigns.xlsx"
        })

    flash("Unsupported export format.", "error")
    return redirect(url_for("reports"))


@app.route("/history/<int:campaign_id>/delete", methods=["POST"])
@login_required
def delete_campaign(campaign_id):
    db.delete_campaign(campaign_id)
    flash("Campaign deleted.", "success")
    return redirect(url_for("history"))


@app.route("/api/campaign/<int:campaign_id>")
@login_required
def api_campaign(campaign_id):
    record = db.get_campaign(campaign_id)
    if not record:
        return jsonify({"error": "not found"}), 404
    return jsonify(record["result"])


@app.route("/auth", methods=["GET"])
def auth():
    if session.get("user_id"):
        return redirect(url_for("index"))
    active_tab = request.args.get("tab", "signin")
    next_url = request.args.get("next", "")
    return render_template("auth.html", active_tab=active_tab, next_url=next_url)


@app.route("/auth/signup", methods=["POST"])
def signup():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    next_url = request.form.get("next", "")

    errors = []
    if not full_name:
        errors.append("Please tell us your name.")
    if not email or not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    if email and db.get_user_by_email(email):
        errors.append("An account with this email already exists — sign in instead.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("auth", tab="signup", next=next_url))

    try:
        password_hash = generate_password_hash(password)
        user_id = db.create_user(full_name, email, password_hash)
    except Exception:
        flash("Something went wrong creating your account. Please try again.", "error")
        return redirect(url_for("auth", tab="signup", next=next_url))

    session.permanent = True
    session["user_id"] = user_id
    flash(f"Welcome to Growth GPT, {full_name.split(' ')[0]}! 🎉", "success")
    return redirect(next_url or url_for("index"))


@app.route("/auth/signin", methods=["POST"])
def signin():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    next_url = request.form.get("next", "")

    try:
        user = db.get_user_by_email(email)
    except Exception:
        flash("Something went wrong signing you in. Please try again.", "error")
        return redirect(url_for("auth", tab="signin", next=next_url))

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Incorrect email or password.", "error")
        return redirect(url_for("auth", tab="signin", next=next_url))

    session.permanent = True
    session["user_id"] = user["id"]
    flash(f"Welcome back, {user['full_name'].split(' ')[0]}! 👋", "success")
    return redirect(next_url or url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been signed out.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
