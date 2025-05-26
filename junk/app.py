from flask import Flask, request, jsonify
from flask_cors import CORS
import util as u
from util import prints
import numpy as np
import predict as model_predict

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests


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
        type = model_predict.calculate_type(avg_scores)
        result_summary = {
            "total_questions": len(responses),
            "average_score": avg_scores,
            "personality type:": type,
            "analysis": "Preliminary analysis completed."
        }

        return jsonify(result_summary), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
