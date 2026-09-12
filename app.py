from flask import Flask, request, jsonify, send_from_directory, session
import re
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)

app.secret_key = "cyberguard_secret_key_2026"

# =========================================
# TEMPORARY USER STORAGE
# =========================================

users = []

# History storage
history = []


# =========================================
# SERVE HTML FILES
# =========================================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def serve_files(filename):
    return send_from_directory(".", filename)


# =========================================
# HELPER: SAVE ANALYSIS HISTORY
# =========================================

def save_history(analysis_type, content, risk_score, risk_level):

    if "user_email" not in session:
        return

    new_history = {
        "user_email": session["user_email"],
        "type": analysis_type,
        "content": content,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }

    history.append(new_history)


# =========================================
# USER REGISTRATION
# =========================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Please fill in all fields."
        })

    for user in users:
        if user["email"] == email:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            })

    users.append({
        "name": name,
        "email": email,
        "password": password
    })

    return jsonify({
        "success": True,
        "message": "Registration successful!"
    })


# =========================================
# USER LOGIN
# =========================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Please enter email and password."
        })

    for user in users:

        if (
            user["email"] == email
            and user["password"] == password
        ):

            session["user_email"] = user["email"]

            return jsonify({
                "success": True,
                "message": "Login successful!",
                "name": user["name"],
                "email": user["email"]
            })

    return jsonify({
        "success": False,
        "message": "Invalid email or password."
    })


# =========================================
# GET USER PROFILE
# =========================================

@app.route("/api/profile", methods=["GET"])
def get_profile():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        })

    user_email = session["user_email"]

    for user in users:

        if user["email"] == user_email:

            return jsonify({
                "success": True,
                "name": user["name"],
                "email": user["email"]
            })

    return jsonify({
        "success": False,
        "message": "User not found."
    })


# =========================================
# UPDATE USER PROFILE
# =========================================

@app.route("/api/update-profile", methods=["POST"])
def update_profile():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        })

    data = request.get_json()

    name = data.get("name", "").strip()
    new_password = data.get("password", "")

    if not name:
        return jsonify({
            "success": False,
            "message": "Name cannot be empty."
        })

    user_email = session["user_email"]

    for user in users:

        if user["email"] == user_email:

            user["name"] = name

            if new_password:
                user["password"] = new_password

            return jsonify({
                "success": True,
                "message": "Profile updated successfully!",
                "name": user["name"]
            })

    return jsonify({
        "success": False,
        "message": "User not found."
    })


# =========================================
# USER LOGOUT
# =========================================

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully!"
    })


# =========================================
# GET USER HISTORY
# =========================================

@app.route("/api/history", methods=["GET"])
def get_history():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        })

    user_email = session["user_email"]

    user_history = []

    for item in reversed(history):

        if item["user_email"] == user_email:
            user_history.append(item)

    return jsonify({
        "success": True,
        "history": user_history
    })


# =========================================
# CLEAR USER HISTORY
# =========================================

@app.route("/api/clear-history", methods=["POST"])
def clear_history():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        })

    user_email = session["user_email"]

    global history

    history = [
        item for item in history
        if item["user_email"] != user_email
    ]

    return jsonify({
        "success": True,
        "message": "History cleared successfully!"
    })


# =========================================
# URL SECURITY CHECKER
# =========================================

@app.route("/api/check-url", methods=["POST"])
def check_url():

    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "message": "Please enter a URL."
        })

    check_url_value = url

    if not check_url_value.startswith(("http://", "https://")):
        check_url_value = "http://" + check_url_value

    parsed_url = urlparse(check_url_value)

    risk_score = 0
    risks = []

    if parsed_url.scheme != "https":
        risk_score += 20
        risks.append("The URL does not use HTTPS.")

    suspicious_words = [
        "login",
        "verify",
        "bank",
        "secure",
        "update",
        "password",
        "account",
        "confirm",
        "wallet",
        "free",
        "prize",
        "gift",
        "bonus"
    ]

    url_lower = url.lower()

    found_words = []

    for word in suspicious_words:

        if word in url_lower:
            found_words.append(word)

    if found_words:

        risk_score += min(
            len(found_words) * 10,
            30
        )

        risks.append(
            "Suspicious keywords detected: " +
            ", ".join(found_words)
        )

    if re.search(r"\d{4,}", url):

        risk_score += 15

        risks.append(
            "Long number sequence detected."
        )

    if "@" in url:

        risk_score += 20

        risks.append(
            "Unusual @ symbol detected."
        )

    if url.count("-") >= 3:

        risk_score += 10

        risks.append(
            "Multiple hyphens detected."
        )

    if len(url) > 100:

        risk_score += 10

        risks.append(
            "The URL is unusually long."
        )

    suspicious_domains = [
        ".xyz",
        ".top",
        ".click",
        ".loan",
        ".win",
        ".gq",
        ".tk"
    ]

    for domain in suspicious_domains:

        if domain in url_lower:

            risk_score += 15

            risks.append(
                "Potentially suspicious domain ending detected."
            )

            break

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "HIGH RISK"

    elif risk_score >= 40:
        risk_level = "SUSPICIOUS"

    else:
        risk_level = "LOW RISK"

    if not risks:

        risks.append(
            "No major suspicious patterns detected."
        )

    recommendations = [
        "Verify the website before entering personal information.",
        "Avoid sharing passwords or banking details.",
        "Use official websites whenever possible."
    ]

    # SAVE HISTORY
    save_history(
        "URL Check",
        url,
        risk_score,
        risk_level
    )

    return jsonify({
        "success": True,
        "url": url,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risks": risks,
        "recommendations": recommendations
    })


# =========================================
# SCAM MESSAGE DETECTOR
# =========================================

@app.route("/api/check-message", methods=["POST"])
def check_message():

    data = request.get_json()

    message = data.get(
        "message",
        ""
    ).strip()

    if not message:

        return jsonify({
            "success": False,
            "message": "Please enter a message."
        })

    message_lower = message.lower()

    risk_score = 0
    risks = []

    urgent_words = [
        "urgent",
        "immediately",
        "act now",
        "today",
        "limited time",
        "hurry",
        "quickly"
    ]

    for word in urgent_words:

        if word in message_lower:

            risk_score += 15

            risks.append(
                "Urgent language detected."
            )

            break

    threat_words = [
        "blocked",
        "suspended",
        "closed",
        "restricted",
        "legal action"
    ]

    for word in threat_words:

        if word in message_lower:

            risk_score += 20

            risks.append(
                "Threatening language detected."
            )

            break

    sensitive_words = [
        "otp",
        "password",
        "pin",
        "cvv",
        "login details"
    ]

    for word in sensitive_words:

        if word in message_lower:

            risk_score += 25

            risks.append(
                "Sensitive information request detected."
            )

            break

    bank_words = [
        "bank",
        "account",
        "upi",
        "payment",
        "refund",
        "credit card",
        "debit card"
    ]

    for word in bank_words:

        if word in message_lower:

            risk_score += 15

            risks.append(
                "Financial content detected."
            )

            break

    if (
        "http://" in message_lower
        or "https://" in message_lower
        or "www." in message_lower
    ):

        risk_score += 20

        risks.append(
            "A link was detected."
        )

    if message.count("!") >= 2:

        risk_score += 10

        risks.append(
            "Excessive exclamation marks detected."
        )

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "HIGH RISK"

    elif risk_score >= 40:
        risk_level = "SUSPICIOUS"

    else:
        risk_level = "LOW RISK"

    if not risks:

        risks.append(
            "No major scam patterns detected."
        )

    recommendations = [
        "Verify the sender before responding.",
        "Do not share OTP or passwords.",
        "Be careful with unexpected links."
    ]

    # SAVE HISTORY
    save_history(
        "Message Check",
        message,
        risk_score,
        risk_level
    )

    return jsonify({
        "success": True,
        "message": message,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risks": risks,
        "recommendations": recommendations
    })


# =========================================
# EMAIL SECURITY CHECKER
# =========================================

@app.route("/api/check-email", methods=["POST"])
def check_email():

    data = request.get_json()

    sender = data.get(
        "sender",
        ""
    ).strip()

    subject = data.get(
        "subject",
        ""
    ).strip()

    content = data.get(
        "content",
        ""
    ).strip()

    if not sender and not subject and not content:

        return jsonify({
            "success": False,
            "message": "Please enter email details."
        })

    combined_text = (
        sender + " " +
        subject + " " +
        content
    ).lower()

    risk_score = 0
    risks = []

    urgency_words = [
        "urgent",
        "immediately",
        "act now",
        "expire"
    ]

    for word in urgency_words:

        if word in combined_text:

            risk_score += 15

            risks.append(
                "Urgent language detected."
            )

            break

    threat_words = [
        "blocked",
        "suspended",
        "closed",
        "restricted"
    ]

    for word in threat_words:

        if word in combined_text:

            risk_score += 20

            risks.append(
                "Account warning detected."
            )

            break

    sensitive_words = [
        "password",
        "otp",
        "pin",
        "cvv",
        "login"
    ]

    for word in sensitive_words:

        if word in combined_text:

            risk_score += 20

            risks.append(
                "Sensitive information request detected."
            )

            break

    if (
        "http://" in combined_text
        or "https://" in combined_text
        or "www." in combined_text
    ):

        risk_score += 15

        risks.append(
            "Link detected in email."
        )

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "HIGH RISK"

    elif risk_score >= 40:
        risk_level = "SUSPICIOUS"

    else:
        risk_level = "LOW RISK"

    if not risks:

        risks.append(
            "No major suspicious email patterns detected."
        )

    recommendations = [
        "Verify the sender carefully.",
        "Do not share OTP or passwords.",
        "Avoid suspicious links and attachments."
    ]

    # SAVE HISTORY
    save_history(
        "Email Check",
        content,
        risk_score,
        risk_level
    )

    return jsonify({
        "success": True,
        "sender": sender,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risks": risks,
        "recommendations": recommendations
    })


# =========================================
# PAYMENT SCAM CHECKER
# =========================================

@app.route("/api/check-payment", methods=["POST"])
def check_payment():

    data = request.get_json()

    payment = data.get(
        "payment",
        ""
    ).strip()

    if not payment:

        return jsonify({
            "success": False,
            "message": "Please enter payment details."
        })

    payment_lower = payment.lower()

    risk_score = 0
    risks = []

    urgent_words = [
        "urgent",
        "immediately",
        "now",
        "quick"
    ]

    for word in urgent_words:

        if word in payment_lower:

            risk_score += 15

            risks.append(
                "Urgent payment request detected."
            )

            break

    sensitive_words = [
        "otp",
        "pin",
        "cvv",
        "password",
        "card number"
    ]

    for word in sensitive_words:

        if word in payment_lower:

            risk_score += 30

            risks.append(
                "Sensitive financial information requested."
            )

            break

    scam_words = [
        "refund",
        "prize",
        "winner",
        "reward",
        "fee",
        "gift"
    ]

    for word in scam_words:

        if word in payment_lower:

            risk_score += 15

            risks.append(
                "Possible scam language detected."
            )

            break

    if (
        "upi" in payment_lower
        or "http://" in payment_lower
        or "https://" in payment_lower
    ):

        risk_score += 15

        risks.append(
            "Payment method or external link detected."
        )

    threat_words = [
        "blocked",
        "legal action",
        "penalty",
        "fine",
        "suspended"
    ]

    for word in threat_words:

        if word in payment_lower:

            risk_score += 20

            risks.append(
                "Threatening language detected."
            )

            break

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "HIGH RISK"

    elif risk_score >= 40:
        risk_level = "SUSPICIOUS"

    else:
        risk_level = "LOW RISK"

    if not risks:

        risks.append(
            "No major payment scam patterns detected."
        )

    recommendations = [
        "Verify the payment request independently.",
        "Never share OTP, PIN, or CVV.",
        "Confirm the recipient before sending money."
    ]

    # SAVE HISTORY
    save_history(
        "Payment Check",
        payment,
        risk_score,
        risk_level
    )

    return jsonify({
        "success": True,
        "payment": payment,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risks": risks,
        "recommendations": recommendations
    })


# =========================================
# RUN FLASK APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )