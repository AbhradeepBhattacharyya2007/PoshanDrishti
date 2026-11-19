from flask import Flask, render_template, request, jsonify
from nutrition_engine import (
    STATE_STAPLES,
    RECIPES,
    load_children,
    save_children,
    fetch_india_weather,
    evaluate_who_zscore,
    build_three_meal_plan,
    extract_card_from_file,
    generate_conversational_reply
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/bootstrap", methods=["GET"])
def api_bootstrap():
    records = load_children()
    normal_cnt = sum(1 for r in records if r["status"] == "Normal")
    mam_cnt = sum(1 for r in records if r["status"] == "MAM")
    sam_cnt = sum(1 for r in records if r["status"] == "SAM")
    states_covered = len(set(r["state"] for r in records))

    # Age cohort breakdown for Analytics Bar Chart
    cohorts = {"6m–1y": [0, 0, 0], "1y–3y": [0, 0, 0], "3y–5y": [0, 0, 0], "5y–6y": [0, 0, 0]}
    for r in records:
        age = r["age"]
        bucket = "6m–1y" if age <= 12 else "1y–3y" if age <= 36 else "3y–5y" if age <= 60 else "5y–6y"
        idx = 0 if r["status"] == "Normal" else 1 if r["status"] == "MAM" else 2
        cohorts[bucket][idx] += 1

    return jsonify({
        "children": records,
        "recipes": RECIPES,
        "stateStaples": STATE_STAPLES,
        "stats": {
            "total": len(records),
            "normal": normal_cnt,
            "mam": mam_cnt,
            "sam": sam_cnt,
            "statesCovered": states_covered,
            "cohorts": cohorts
        }
    })


@app.route("/api/assess", methods=["POST"])
def api_assess():
    data = request.json or {}
    name = data.get("name", "Beneficiary Child").strip()
    age = int(data.get("age", 24))
    gender = data.get("gender", "Female")
    height = float(data.get("height", 82.0))
    weight = float(data.get("weight", 9.5))
    city = data.get("city", "Mysuru").strip()
    condition = data.get("condition", "Routine Growth Check").strip() or "Routine Growth Check"

    weather = fetch_india_weather(city)
    if not weather:
        return jsonify({"error": f"Could not find '{city}' in India. Please try a nearby district or town name."}), 400

    triage = evaluate_who_zscore(age, height, weight)
    plan = build_three_meal_plan(triage["status"], weather)
    avg_cost = f"₹{plan['meals'][0]['cost']:.2f}"

    records = load_children()
    new_id = max([r.get("id", 100) for r in records] + [100]) + 1
    new_record = {
        "id": new_id,
        "name": name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "city": weather["city"],
        "state": weather["state"],
        "status": triage["status"],
        "zScore": triage["zScore"],
        "cost": avg_cost,
        "condition": condition
    }
    records.insert(0, new_record)
    save_children(records)

    return jsonify({
        "record": new_record,
        "weather": weather,
        "triage": triage,
        "plan": plan
    })


@app.route("/api/children/<int:child_id>", methods=["DELETE"])
def api_delete_child(child_id):
    records = [r for r in load_children() if r.get("id") != child_id]
    save_children(records)
    return jsonify({"deleted": child_id})


@app.route("/api/radar", methods=["POST"])
def api_radar():
    data = request.json or {}
    city = data.get("city", "Kalaburagi").strip()
    sam_rate = float(data.get("samRate", 14.5))
    water = data.get("water", "tap")

    weather = fetch_india_weather(city)
    if not weather:
        return jsonify({"error": f"Could not resolve '{city}' in India."}), 400

    heat_stress = max(0.0, (weather["temp"] - 30.0) * 3.5)
    water_risk = 22.0 if water == "open" else 10.0 if water == "tap" else 2.0
    risk_score = min(98.0, round(heat_stress + water_risk + sam_rate * 1.4, 1))

    if risk_score >= 65:
        level = "HIGH OUTBREAK RISK"
        badge = "SAM"
        directive = "🚨 Deploy ORS + Zinc corners immediately; switch to cooling Sattu/Buttermilk feeds & enforce boiled drinking water."
    elif risk_score >= 40:
        level = "MODERATE WATCH"
        badge = "MAM"
        directive = "⚠️ Increase Moringa/Vitamin-A fortification in Hot Cooked Meals and conduct bi-weekly MUAC screening."
    else:
        level = "LOW / STABLE"
        badge = "Normal"
        directive = "✅ Continue routine Poshan Vatika kitchen garden harvesting and monthly growth monitoring."

    return jsonify({
        "weather": weather,
        "riskScore": risk_score,
        "level": level,
        "badge": badge,
        "directive": directive
    })


@app.route("/api/parse-card", methods=["POST"])
def api_parse_card():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f = request.files["file"]
    profile = extract_card_from_file(f)
    return jsonify({"profile": profile})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    card_profile = data.get("cardProfile")
    api_key = data.get("apiKey")
    if not message:
        return jsonify({"reply": "Please type a question or describe a child's details!"})

    reply = generate_conversational_reply(message, card_profile=card_profile, api_key=api_key)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
