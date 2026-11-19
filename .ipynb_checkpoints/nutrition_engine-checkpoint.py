import os
import json
import re
import requests
from pypdf import PdfReader

DATA_FILE = "children_registry.json"

# Complete 28 States + 8 UTs Indigenous Crop & Staple Mapping
STATE_STAPLES = {
    "Karnataka": "Ragi (Finger Millet), Jowar & Drumstick Leaves",
    "Tamil Nadu": "Kambu (Pearl Millet), Parboiled Rice & Moringa",
    "Kerala": "Red/Parboiled Rice, Coconut & Banana/Jackfruit",
    "Andhra Pradesh": "Jowar, Rice & Gongura/Drumstick Leaves",
    "Telangana": "Jowar, Bajra & Red Gram Dal",
    "Puducherry": "Rice, Ragi & Local Greens",
    "Andaman and Nicobar Islands": "Rice, Coconut & Pulses",
    "Lakshadweep": "Rice, Coconut & Local Pulses",
    "Punjab": "Whole Wheat, Makki (Corn) & Mustard Greens",
    "Haryana": "Bajra, Whole Wheat & Chana Dal",
    "Himachal Pradesh": "Maize, Red Rice, Rajma & Buckwheat",
    "Uttarakhand": "Mandua (Ragi), Jhangora & Bhatt Dal",
    "Jammu and Kashmir": "Rice, Maize, Rajma & Haak Greens",
    "Ladakh": "Barley (Tsampa), Wheat & Dried Apricot/Peas",
    "Uttar Pradesh": "Wheat, Bajra, Sattu & Arhar Dal",
    "Delhi": "Wheat, Sattu & Seasonal Greens",
    "Chandigarh": "Whole Wheat, Sattu & Dal",
    "Rajasthan": "Bajra, Moth Dal, Guar & Sattu",
    "Gujarat": "Bajra, Jowar, Moong & Methi",
    "Maharashtra": "Jowar, Bajra, Groundnut & Matki",
    "Goa": "Parboiled Rice, Ragi & Coconut",
    "Madhya Pradesh": "Wheat, Jowar, Chana & Kodo Millet",
    "Chhattisgarh": "Rice, Kodo-Kutki Millet & Bhaji Greens",
    "West Bengal": "Parboiled Rice, Masoor Dal & Pumpkin/Greens",
    "Bihar": "Sattu (Roasted Gram), Rice, Wheat & Masoor Dal",
    "Jharkhand": "Ragi (Marua), Rice & Horse Gram",
    "Odisha": "Parboiled Rice, Mandia (Ragi) & Drumstick",
    "Assam": "Joha/Parboiled Rice, Black Gram & Greens",
    "Arunachal Pradesh": "Rice, Maize, Millet & Local Greens",
    "Manipur": "Rice, Black/Red Dal & Local Greens",
    "Meghalaya": "Red Rice, Maize & Soybeans",
    "Mizoram": "Rice, Maize & Pumpkin/Mustard Leaves",
    "Nagaland": "Rice, Millet, Soybeans & Local Greens",
    "Sikkim": "Finger Millet (Kodo), Buckwheat & Soybeans",
    "Tripura": "Rice, Moong Dal & Seasonal Vegetables"
}

# Pre-populated Multi-State Anganwadi Child Registry (18 Records across India)
INITIAL_CHILDREN = [
    {"id": 101, "name": "Rohan M.", "age": 14, "gender": "Male", "height": 75.0, "weight": 6.7, "city": "Bikaner", "state": "Rajasthan", "status": "SAM", "zScore": -3.4, "cost": "₹7.20", "condition": "Severe Wasting & Heat Dehydration"},
    {"id": 102, "name": "Chotu K.", "age": 11, "gender": "Male", "height": 71.0, "weight": 6.1, "city": "Gaya", "state": "Bihar", "status": "SAM", "zScore": -3.2, "cost": "₹7.50", "condition": "Post-Diarrheal Recovery"},
    {"id": 103, "name": "Tenzin D.", "age": 22, "gender": "Female", "height": 81.0, "weight": 8.0, "city": "Leh", "state": "Ladakh", "status": "SAM", "zScore": -3.1, "cost": "₹9.00", "condition": "Cold-Climate Calorie Deficit"},
    {"id": 104, "name": "Diya S.", "age": 19, "gender": "Female", "height": 79.5, "weight": 8.3, "city": "Belagavi", "state": "Karnataka", "status": "MAM", "zScore": -2.3, "cost": "₹7.80", "condition": "Iron Deficiency / Anemia Watch"},
    {"id": 105, "name": "Ananya P.", "age": 30, "gender": "Female", "height": 87.0, "weight": 9.8, "city": "Cuttack", "state": "Odisha", "status": "MAM", "zScore": -2.5, "cost": "₹8.20", "condition": "Picky Appetite & Low Protein"},
    {"id": 106, "name": "Vihaan T.", "age": 16, "gender": "Male", "height": 77.0, "weight": 7.9, "city": "Indore", "state": "Madhya Pradesh", "status": "MAM", "zScore": -2.2, "cost": "₹8.00", "condition": "Moderate Underweight"},
    {"id": 107, "name": "Mehnaz B.", "age": 26, "gender": "Female", "height": 84.0, "weight": 9.2, "city": "Baramulla", "state": "Jammu and Kashmir", "status": "MAM", "zScore": -2.4, "cost": "₹8.90", "condition": "Winter Micronutrient Deficit"},
    {"id": 108, "name": "Aarav K.", "age": 28, "gender": "Male", "height": 89.0, "weight": 12.6, "city": "Mysuru", "state": "Karnataka", "status": "Normal", "zScore": 0.1, "cost": "₹8.50", "condition": "Healthy Growth Trajectory"},
    {"id": 109, "name": "Meera N.", "age": 36, "gender": "Female", "height": 95.0, "weight": 14.1, "city": "Thrissur", "state": "Kerala", "status": "Normal", "zScore": -0.2, "cost": "₹8.50", "condition": "Healthy / Active Poshan Vatika"},
    {"id": 110, "name": "Karthik R.", "age": 42, "gender": "Male", "height": 99.0, "weight": 15.2, "city": "Madurai", "state": "Tamil Nadu", "status": "Normal", "zScore": -0.3, "cost": "₹8.20", "condition": "Healthy Growth"},
    {"id": 111, "name": "Gurpreet S.", "age": 48, "gender": "Male", "height": 103.0, "weight": 16.5, "city": "Ludhiana", "state": "Punjab", "status": "Normal", "zScore": -0.2, "cost": "₹9.20", "condition": "Healthy Growth"},
    {"id": 112, "name": "Suhani D.", "age": 24, "gender": "Female", "height": 84.5, "weight": 11.2, "city": "Guwahati", "state": "Assam", "status": "Normal", "zScore": -0.1, "cost": "₹8.40", "condition": "Healthy Growth"},
    {"id": 113, "name": "Pranav G.", "age": 54, "gender": "Male", "height": 106.0, "weight": 17.0, "city": "Pune", "state": "Maharashtra", "status": "Normal", "zScore": -0.6, "cost": "₹8.60", "condition": "Healthy Growth"},
    {"id": 114, "name": "Zoya F.", "age": 20, "gender": "Female", "height": 80.0, "weight": 8.4, "city": "Lucknow", "state": "Uttar Pradesh", "status": "MAM", "zScore": -2.3, "cost": "₹7.90", "condition": "Weaning Transition Support"},
    {"id": 115, "name": "Devansh J.", "age": 34, "gender": "Male", "height": 92.0, "weight": 13.3, "city": "Ahmedabad", "state": "Gujarat", "status": "Normal", "zScore": -0.1, "cost": "₹8.30", "condition": "Healthy Growth"},
    {"id": 116, "name": "Riya M.", "age": 15, "gender": "Female", "height": 76.0, "weight": 7.6, "city": "Howrah", "state": "West Bengal", "status": "MAM", "zScore": -2.3, "cost": "₹8.00", "condition": "Low Hemoglobin Watch"},
    {"id": 117, "name": "Sai Charan", "age": 38, "gender": "Male", "height": 96.0, "weight": 14.5, "city": "Warangal", "state": "Telangana", "status": "Normal", "zScore": -0.1, "cost": "₹8.40", "condition": "Healthy Growth"},
    {"id": 118, "name": "Lobsang T.", "age": 45, "gender": "Male", "height": 100.0, "weight": 15.6, "city": "Gangtok", "state": "Sikkim", "status": "Normal", "zScore": -0.2, "cost": "₹9.10", "condition": "Healthy Growth"}
]

RECIPES = [
    {
        "id": "r1",
        "name": "Ragi & Moringa Iron-Boost Porridge (Hittu)",
        "region": "South India (Karnataka / TN / Odisha)",
        "climate": "Monsoon",
        "goal": "Anemia",
        "cost": 6.50,
        "kcal": 380,
        "protein": 12.5,
        "prepMins": 15,
        "ingredients": [
            {"item": "Sprouted Ragi (Finger Millet) Flour", "qty": 35, "unit": "g"},
            {"item": "Fresh Drumstick (Moringa) Leaves", "qty": 20, "unit": "g"},
            {"item": "Crushed Palm/Cane Jaggery", "qty": 15, "unit": "g"},
            {"item": "Roasted Groundnut Powder", "qty": 10, "unit": "g"},
            {"item": "Ghee or Fortified Oil", "qty": 5, "unit": "ml"}
        ],
        "steps": [
            "Whisk sprouted ragi flour in 150 ml water without lumps.",
            "Cook on medium flame for 6–7 minutes while stirring continuously until glossy.",
            "Stir in finely chopped blanched moringa leaves, jaggery, and groundnut powder.",
            "Finish with 1 tsp ghee/oil and serve warm."
        ]
    },
    {
        "id": "r2",
        "name": "Chilled Sattu & Buttermilk Hydration Cooler",
        "region": "North & East India (Bihar / UP / Rajasthan)",
        "climate": "Summer",
        "goal": "Maintenance",
        "cost": 5.80,
        "kcal": 310,
        "protein": 13.0,
        "prepMins": 8,
        "ingredients": [
            {"item": "Roasted Bengal Gram Flour (Chana Sattu)", "qty": 30, "unit": "g"},
            {"item": "Fresh Curd / Buttermilk (Chaas)", "qty": 100, "unit": "ml"},
            {"item": "Roasted Cumin (Jeera) Powder", "qty": 1, "unit": "g"},
            {"item": "Lemon Juice & Pinch of Iodized Salt", "qty": 5, "unit": "ml"}
        ],
        "steps": [
            "Whisk curd with 100 ml clean boiled-and-cooled water until smooth.",
            "Gradually blend in sattu flour so no lumps remain.",
            "Add roasted cumin, a pinch of iodized salt, and fresh lemon juice for iron absorption."
        ]
    },
    {
        "id": "r3",
        "name": "Energy-Dense THR Peanut-Jaggery Laddu",
        "region": "All-India ICDS Take-Home Ration",
        "climate": "Winter",
        "goal": "SAM",
        "cost": 7.20,
        "kcal": 465,
        "protein": 15.2,
        "prepMins": 12,
        "ingredients": [
            {"item": "ICDS Take-Home Ration (THR) Wheat-Soy Premix", "qty": 45, "unit": "g"},
            {"item": "Roasted Crushed Peanuts", "qty": 20, "unit": "g"},
            {"item": "Melted Jaggery Syrup", "qty": 20, "unit": "g"},
            {"item": "Sesame Seeds (Til) & Oil/Ghee", "qty": 8, "unit": "g"}
        ],
        "steps": [
            "Dry-roast THR premix and sesame seeds for 3 minutes until aromatic.",
            "Mix in crushed roasted peanuts.",
            "Bind together using warm melted jaggery and ghee, then roll into 2 soft bite-sized laddus."
        ]
    },
    {
        "id": "r4",
        "name": "Bajra & Moong Dal Warming Khichdi",
        "region": "West & North-West (Rajasthan / Gujarat / Haryana)",
        "climate": "Winter",
        "goal": "SAM",
        "cost": 8.40,
        "kcal": 440,
        "protein": 16.0,
        "prepMins": 20,
        "ingredients": [
            {"item": "Coarsely Crushed Pearl Millet (Bajra)", "qty": 35, "unit": "g"},
            {"item": "Split Yellow Moong Dal", "qty": 20, "unit": "g"},
            {"item": "Diced Carrot & Spinach", "qty": 30, "unit": "g"},
            {"item": "Ghee + Turmeric + Cumin", "qty": 7, "unit": "g"}
        ],
        "steps": [
            "Soak crushed bajra and moong dal for 20 minutes.",
            "Pressure cook with chopped carrots, spinach, turmeric, and 200 ml water for 4 whistles.",
            "Mash softly to a toddler-friendly consistency and top with warm ghee."
        ]
    },
    {
        "id": "r5",
        "name": "Curd Rice & Mashed Banana Gut-Recovery Bowl",
        "region": "South & Coastal India",
        "climate": "Summer",
        "goal": "SAM",
        "cost": 7.50,
        "kcal": 390,
        "protein": 11.2,
        "prepMins": 10,
        "ingredients": [
            {"item": "Soft Overcooked Parboiled Rice", "qty": 45, "unit": "g"},
            {"item": "Fresh Probiotic Curd", "qty": 80, "unit": "g"},
            {"item": "Ripe Elaichi / Robusta Banana", "qty": 40, "unit": "g"},
            {"item": "Grated Cucumber & Curry Leaves", "qty": 20, "unit": "g"}
        ],
        "steps": [
            "Mash warm cooked rice smoothly with fresh curd and 2 tbsp water.",
            "Fold in mashed ripe banana (rich in potassium for diarrhea/heat recovery) and grated cucumber."
        ]
    },
    {
        "id": "r6",
        "name": "Savory THR Vegetable & Sprout Upma",
        "region": "All-India Anganwadi Hot Cooked Meal",
        "climate": "Monsoon",
        "goal": "Maintenance",
        "cost": 7.90,
        "kcal": 375,
        "protein": 13.8,
        "prepMins": 15,
        "ingredients": [
            {"item": "Savory / Unsweetened THR Cereal Mix", "qty": 45, "unit": "g"},
            {"item": "Steamed Green Moong Sprouts", "qty": 20, "unit": "g"},
            {"item": "Finely Chopped Pumpkin & Tomato", "qty": 30, "unit": "g"},
            {"item": "Fortified Cooking Oil & Mustard Seeds", "qty": 5, "unit": "ml"}
        ],
        "steps": [
            "Temper mustard seeds in fortified oil, saute pumpkin and tomato until soft.",
            "Add steamed moong sprouts and 120 ml boiling water.",
            "Stir in THR cereal mix and cover on low heat for 4 minutes."
        ]
    }
]


def load_children():
    if not os.path.exists(DATA_FILE):
        save_children(INITIAL_CHILDREN)
        return list(INITIAL_CHILDREN)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return list(INITIAL_CHILDREN)


def save_children(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def fetch_india_weather(place_name):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(place_name)}&count=5&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=8).json()
        matches = [r for r in geo_res.get("results", []) if r.get("country_code") == "IN"]
        if not matches:
            return None

        loc = matches[0]
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current_weather=true"
        w_res = requests.get(w_url, timeout=8).json()
        temp = w_res["current_weather"]["temperature"]
        wind = w_res["current_weather"]["windspeed"]

        if temp >= 33:
            season = "Summer"
            climate_label = "☀️ Hot / Heatwave Climate"
        elif temp <= 19:
            season = "Winter"
            climate_label = "❄️ Cool / Winter Climate"
        else:
            season = "Monsoon"
            climate_label = "🌦️ Moderate / Pleasant Climate"

        state_name = loc.get("admin1") or "India"
        staples = STATE_STAPLES.get(state_name, "Rice, Wheat, Pulses & Seasonal Greens")

        return {
            "city": loc["name"],
            "state": state_name,
            "lat": round(loc["latitude"], 3),
            "lon": round(loc["longitude"], 3),
            "temp": temp,
            "wind": wind,
            "season": season,
            "climateLabel": climate_label,
            "staples": staples
        }
    except Exception:
        return None


def evaluate_who_zscore(age_months, height_cm, weight_kg):
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    z_score = round((bmi - 15.8) / 1.15, 2)

    if z_score < -3.0:
        status = "SAM"
    elif z_score < -2.0:
        status = "MAM"
    else:
        status = "Normal"

    return {"status": status, "zScore": z_score, "bmi": round(bmi, 1)}


def build_three_meal_plan(status, weather):
    climate_recipe = next((r for r in RECIPES if r["climate"] == weather["season"]), RECIPES[1])
    thr_recipe = next((r for r in RECIPES if r["id"] == ("r3" if status == "SAM" else "r6")), RECIPES[2])
    hcm_recipe = next((r for r in RECIPES if r["id"] == ("r4" if weather["season"] == "Winter" else "r1")), RECIPES[0])

    if status == "SAM":
        booster = "🚨 SAM CRITICAL PROTOCOL: Stir 2 tsp Ghee/Oil + 15g crushed peanut-jaggery into every meal (target 175 kcal/kg/day) and refer to PHC/NRC if edema is present."
    elif status == "MAM":
        booster = "⚠️ MAM RECOVERY BOOSTER: Add 1 boiled egg or 20g roasted chana/sattu powder daily for catch-up weight gain."
    else:
        booster = "✅ HEALTHY GROWTH MAINTENANCE: Continue standard ICDS Hot Cooked Meal + 1 seasonal fruit and safe drinking water."

    return {"meals": [hcm_recipe, thr_recipe, climate_recipe], "boosterNote": booster}


def extract_card_from_file(file_storage):
    filename = file_storage.filename or "HealthCard.pdf"
    text = ""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(file_storage)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    else:
        text = file_storage.read().decode("utf-8", errors="ignore")

    name_m = re.search(r"Child Name:\s*([A-Za-z\s.]+?)(?=Age|Location|WHO|\n|$)", text, re.I)
    age_m = re.search(r"(\d+)\s*Months", text, re.I)
    status_m = re.search(r"\b(SAM|MAM|Normal)\b", text, re.I)
    z_m = re.search(r"Z-Score:\s*([+-]?\d+\.?\d*)", text, re.I)
    cost_m = re.search(r"₹\s*\d+(\.\d+)?", text)

    detected_state = "India"
    for st in STATE_STAPLES:
        if st.lower() in text.lower():
            detected_state = st
            break

    return {
        "name": name_m.group(1).strip() if name_m else os.path.splitext(filename)[0],
        "age": age_m.group(1) if age_m else "24",
        "status": status_m.group(1).upper() if status_m else "MAM",
        "zScore": z_m.group(1) if z_m else "-2.1",
        "cost": cost_m.group(0) if cost_m else "₹8.50",
        "state": detected_state,
        "rawPreview": text[:400]
    }


def generate_conversational_reply(user_message, card_profile=None, api_key=None):
    records = load_children()

    # Optional Live Groq LLM call if user configured an API key
    if api_key:
        try:
            card_ctx = (
                f"Active Uploaded Card: Name={card_profile['name']}, Age={card_profile['age']}m, "
                f"State={card_profile['state']}, Status={card_profile['status']}, Z-Score={card_profile['zScore']}, Budget={card_profile['cost']}."
                if card_profile else "No health card uploaded right now."
            )
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are Poshan Sahayak, a warm, human, empathetic Indian Anganwadi child nutrition mentor "
                                "(for children 0–6 years under PoshanDrishti). Speak naturally like a supportive public health counselor—"
                                "never robotic. Give practical Indian meal advice using local crops and ICDS norms. " + card_ctx
                            )
                        },
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.65,
                    "max_tokens": 450
                },
                timeout=12
            )
            if res.ok:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    # Built-in Human-Like Clinical & Nutritional Inference Engine
    q = user_message.lower()
    age_m = re.search(r"(\d+)\s*(?:-|\s)?(?:month|mo|yr|year)", q)
    weight_m = re.search(r"(\d+(?:\.\d+)?)\s*kg", q)
    height_m = re.search(r"(\d+(?:\.\d+)?)\s*cm", q)
    budget_m = re.search(r"(?:₹|rs\.?|rupees?)\s*(\d+(?:\.\d+)?)", q)

    mentioned_state = card_profile["state"] if card_profile else None
    for st in STATE_STAPLES:
        if st.lower() in q:
            mentioned_state = st
            break

    matched_child = next((c for c in records if c["name"].split()[0].lower() in q), None)

    has_diarrhea = bool(re.search(r"loose motion|diarrhea|diarrhoea|watery stool|vomit|dehydrat", q))
    has_anemia = bool(re.search(r"anemia|anaemia|pale|tired|iron|hemoglobin|hb", q))
    has_edema = bool(re.search(r"swelling|edema|oedema|puffy feet", q))

    # 1. Free-text child measurements provided
    if weight_m and height_m:
        age = int(age_m.group(1)) * (12 if ("year" in q or "yr" in q) else 1) if age_m else 24
        weight = float(weight_m.group(1))
        height = float(height_m.group(1))
        triage = evaluate_who_zscore(age, height, weight)
        state_lbl = mentioned_state or "their region"
        staples = STATE_STAPLES.get(mentioned_state, "local millets, dal, and seasonal greens")

        reply = (
            f"Thank you for sharing those details. Looking at a {age}-month-old child weighing {weight} kg at {height} cm, "
            f"their approximate WHO Weight-for-Height Z-score comes out to {triage['zScore']}, placing them in the "
            f"{triage['status']} ({'Red — Severe Acute Malnutrition' if triage['status'] == 'SAM' else 'Yellow — Moderate Acute Malnutrition' if triage['status'] == 'MAM' else 'Green — Healthy'}) zone.\n\n"
        )
        if has_edema or triage["status"] == "SAM":
            reply += (
                "Because this falls into the critical SAM range, the safest first step is to have them checked at the nearest "
                "Primary Health Centre (PHC) or Nutrition Rehabilitation Centre (NRC) to rule out underlying infections.\n\n"
            )
        if has_diarrhea:
            reply += (
                "Since they also have loose motions, focus on gentle hydration first: offer small sips of WHO ORS after every "
                "loose stool, ask the health worker for a 14-day Zinc course, and stick to soothing foods like curd-rice with "
                "mashed ripe banana or thin moong dal khichdi.\n\n"
            )
        else:
            reply += (
                f"For daily feeding in {state_lbl}, you can lean on familiar, budget-friendly staples like {staples}. "
                "Instead of 3 large meals, try 5 to 6 smaller energy-dense feeds—such as porridge or khichdi enriched with "
                "1–2 teaspoons of ghee/oil and crushed roasted peanuts or jaggery.\n\n"
            )
        reply += "Would you like me to share an exact recipe with measurements, or check how you can log them into the registry?"
        return reply

    # 2. Specific clinical symptoms
    if has_diarrhea:
        return (
            "Loose motions can drain a young child's strength very quickly, so hydration comes first before pushing heavy solids.\n\n"
            "Give small, frequent sips of WHO ORS (even 2–3 spoonfuls every few minutes), continue breastfeeding if applicable, "
            "and check with the Anganwadi or ANM for Zinc tablets (10 mg/day under 6 months, 20 mg/day for toddlers for 14 days). "
            "For meals, stick to mashed ripe banana, curd rice, or thin rice-dal kanji. How old is the child, and are they keeping fluids down?"
        )

    if has_anemia:
        return (
            "Low iron or anemia is very common in toddlers, and it responds wonderfully to smart local food pairings.\n\n"
            "Whenever you serve iron-rich foods like Ragi (finger millet), drumstick (moringa) leaves, jaggery, or chana/sattu, "
            "pair them with a squeeze of fresh lemon, tomato, or amla—that natural Vitamin C boosts iron absorption nearly three times! "
            "Also avoid giving tea or excess milk right alongside iron-rich meals. Which state is the child in so I can suggest a local iron-rich dish?"
        )

    # 3. Uploaded Health Card context
    if card_profile and re.search(r"card|this child|diet|meal|plan|recover|critical", q):
        staples = STATE_STAPLES.get(card_profile["state"], "ragi, moong dal, and seasonal greens")
        return (
            f"Looking at {card_profile['name']}'s card ({card_profile['age']} months, {card_profile['status']} status, budget {card_profile['cost']}/day), "
            f"here is a practical daily rhythm using {staples}:\n\n"
            "• Morning: Warm sprouted millet or sattu porridge sweetened with crushed jaggery and roasted peanut powder.\n"
            "• Mid-Day (Anganwadi HCM): Soft dal-rice khichdi cooked with chopped moringa or spinach leaves and 1 tsp fortified oil/ghee.\n"
            "• Evening Snack: Bite-sized Take-Home Ration (THR) peanut-jaggery laddu with clean boiled water or buttermilk.\n\n"
            "Would you like the step-by-step cooking method for any of these three?"
        )

    # 4. Registered child lookup
    if matched_child:
        return (
            f"I pulled up {matched_child['name']}'s record from your center registry—they are {matched_child['age']} months old in "
            f"{matched_child['city']}, {matched_child['state']}, currently classified as {matched_child['status']} "
            f"(Z-score: {matched_child['zScore']}, note: {matched_child['condition']}).\n\n"
            f"{'They are thriving in the Normal zone! Keeping up their regular Anganwadi Hot Cooked Meals and seasonal fruits will keep them strong.' if matched_child['status'] == 'Normal' else 'Because they need catch-up growth, adding a daily protein booster like a boiled egg, Ksheera milk, or a THR peanut-jaggery laddu will help bring their Z-score back toward Normal.'}\n\n"
            f"Would you like to generate their printable A5 Health Card or build a weekly menu for {matched_child['name']}?"
        )

    # 5. State / Budget / Seasonal Meal Queries
    if mentioned_state or budget_m or re.search(r"summer|winter|monsoon|meal|recipe|thr|take-home|ration|picky", q):
        st = mentioned_state or "Karnataka"
        staples = STATE_STAPLES[st]
        b_txt = f"around ₹{budget_m.group(1)}" if budget_m else "within the standard ICDS ₹7–₹9 norm"
        if "summer" in q or "hot" in q:
            return (
                f"In warm weather, heavy dry foods often put kids off eating. A great {b_txt} combo in {st} is a chilled "
                f"Sattu or roasted gram buttermilk cooler mid-morning, followed by soft curd-rice mashed with ripe banana and "
                f"local greens ({staples.split('&')[0].strip()}). It keeps them hydrated while still packing ~13g of protein!\n\n"
                "Want the exact gram measurements for 1 child or a 25-child Anganwadi batch?"
            )
        return (
            f"Using {st}'s local staples ({staples}), you can put together a nourishing meal {b_txt}: try a soft millet-moong dal "
            "khichdi with chopped drumstick leaves for lunch, and turn the dry government Take-Home Ration (THR) packet into warm "
            "bite-sized peanut-jaggery laddus so toddlers can self-feed easily.\n\n"
            "Would you like the full cooking instructions or batch measurements?"
        )

    # 6. WHO Z-score explanation
    if re.search(r"z-score|z score|sam|mam|who|cutoff|muac", q):
        return (
            "Think of WHO Z-scores as a simple ruler showing how a child's weight compares to healthy children of the exact same height and age:\n\n"
            "• Normal (Green — above -2 SD): Growing steadily on track.\n"
            "• MAM (Yellow — between -2 SD and -3 SD): Moderate Acute Malnutrition. Needs a daily protein/calorie boost (eggs, milk, or roasted chana) before it worsens.\n"
            "• SAM (Red — below -3 SD, or MUAC under 11.5 cm): Severe Acute Malnutrition. Needs frequent energy-dense feeds (6 times a day) and a PHC/NRC health checkup.\n\n"
            "Do you have a child's height and weight handy that you'd like me to check for you?"
        )

    return (
        "I'd love to help with that! Could you share a little more context—like the child's age, approximate weight and height, "
        "which state they're in, or any symptoms like poor appetite or loose motions? You can also upload a PDF Health Card at the top anytime."
    )
