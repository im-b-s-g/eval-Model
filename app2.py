import os
import sys
import util as u
import subprocess
import numpy as np
from util import prints
from flask_cors import CORS
from pymongo import MongoClient
import predict as model_predict
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

GOOGLE_CLIENT_ID = "655578416897-i30oggeleaam926p0359t8ghhcvkn8kg.apps.googleusercontent.com"


@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json()
        responses = data.get("responses", {})

        if not responses:
            return jsonify({"error": "No responses received"}), 400

        # Example: Processing responses
        u.extract_traits(responses)
        avg_scores = u.calculate_average_values()
        print(avg_scores)
        personality_type = model_predict.calculate_type(avg_scores)
        result_summary = {
            "total_questions": len(responses),
            "average_score": avg_scores,
            "personality_type": personality_type,
            "analysis": "Preliminary analysis completed."
        }

        return jsonify(result_summary), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    try:
        # Run the Node.js script to generate the questions
        subprocess.run(["node", "generate.js"], check=True)

        return jsonify({"message": "Questions generated successfully!"}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to generate questions: {str(e)}"}), 500


try:
    MONGO_URI = "mongodb+srv://imbsg:qcOfVo8djlR37JLq@cluster0.ryte5cz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["neurogenix"]
    users_collection = db["credentials"]  # ← update collection name
    tests_collection = db["tests"]
    # Trigger connection to confirm
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully")

except Exception as e:
    print("❌ MongoDB connection failed:", e)
    sys.exit(1)


@app.route("/api/login", methods=["POST"])
def email_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Check if user exists
    user = users_collection.find_one({"email": email, "password": password})

    if user:
        return jsonify({
            "message": f"Welcome {user['name']}",
            "name": user["name"]
        })
    else:
        return jsonify({"message": "Invalid email or password"}), 401


@app.route("/api/tests", methods=["POST"])
def save_test():
    data = request.get_json()
    email = data.get("email")
    test_id = data.get("testId")
    created_at = data.get("createdAt")
    used = data.get("used", False)
    result = data.get("result", None)
    name = data.get("name")
    age = data.get("age")

    if not email or not test_id or not created_at:
        return jsonify({"message": "Missing required test data"}), 400

    tests_collection = db["tests"]  # new collection for tests

    try:
        # Save the test with doctor email
        tests_collection.insert_one({
            "email": email,
            "testId": test_id,
            "createdAt": created_at,
            "used": used,
            "result": result,
            "name": name,
            "age": age
        })
        return jsonify({"message": "Test saved successfully"})
    except Exception as e:
        return jsonify({"message": f"Failed to save test: {str(e)}"}), 500


@app.route("/api/tests", methods=["GET"])
def get_tests():
    email = request.args.get("email")
    tests_collection = db["tests"]

    if not email:
        return jsonify({"tests": []})

    tests_cursor = tests_collection.find({"email": email})
    tests = []

    for test in tests_cursor:
        # Convert ObjectId to str if needed, and pick only desired fields
        tests.append({
            "testId": test.get("testId"),  # normalize testId -> id
            "createdAt": test.get("createdAt"),
            "used": test.get("used"),
            "result": test.get("result"),
            "name": test.get("name"),
            "age": test.get("age"),
        })

    return jsonify({"tests": tests})


@app.route("/api/mark-used", methods=["PUT"])
def mark_test_as_used():
    data = request.get_json()
    test_id = data.get("testId")
    result_data = data.get("result")

    if not test_id:
        return jsonify({"message": "Test ID is required"}), 400

    tests_collection = db["tests"]

    try:
        existing_test = tests_collection.find_one({"testId": test_id})

        if not existing_test:
            return jsonify({"message": "Test ID not found"}), 404

        if existing_test.get("used"):
            return jsonify({"message": "Test has already been used"}), 403

        update_fields = {"used": True}
        if result_data:
            update_fields["result"] = result_data

        tests_collection.update_one(
            {"testId": test_id},
            {"$set": update_fields}
        )

        return jsonify({"message": "Test marked as used and result stored."}), 200

    except Exception as e:
        return jsonify({"message": f"Error updating test: {str(e)}"}), 500


# Remove COOP/COEP headers in dev mode


@app.route("/api/test-by-id", methods=["GET"])
def get_test_by_id():
    test_id = request.args.get("testId")
    if not test_id:
        return jsonify({"message": "Test ID is required"}), 400

    test = db["tests"].find_one({"testId": test_id})
    if not test:
        return jsonify({"message": "Test not found"}), 404

    return jsonify({
        "testId": test.get("testId"),
        "name": test.get("name"),
        "age": test.get("age"),
        "used": test.get("used"),
        "result": test.get("result"),
        "createdAt": test.get("createdAt"),
    })


@app.route("/api/verify-test-id", methods=["POST"])
def verify_test_id():
    data = request.get_json()
    test_id = data.get("testId")

    print("DEBUG: Incoming testId:", test_id)

    if not test_id:
        return jsonify({"message": "Test ID is required"}), 400

    existing = tests_collection.find_one({"testId": test_id})

    if not existing:
        print("DEBUG: Test ID NOT found.")
        return jsonify({
            "exists": False,
            "message": "❗Test ID not found. Please check your ID or contact your doctor."
        }), 200

    if existing.get("used", False):
        print("DEBUG: Test ID already used.")
        return jsonify({
            "exists": True,
            "used": True,
            "message": "⚠️ This Test ID has already been used. Please request a new one from your doctor."
        }), 200

    # Mark as used if it's unused
    # tests_collection.update_one(
    #     {"testId": test_id},
    #     {"$set": {"used": True}}
    # )

    print("DEBUG: Test ID verified and marked as used.")
    return jsonify({"exists": True, "used": False}), 200


@app.after_request
def remove_opener_policy(response):
    if os.environ.get("FLASK_ENV") == "development":
        response.headers.pop("Cross-Origin-Opener-Policy", None)
        response.headers.pop("Cross-Origin-Embedder-Policy", None)
    return response


if __name__ == '__main__':
    app.run(debug=True)
