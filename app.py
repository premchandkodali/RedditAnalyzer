from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.persona_generator import generate_persona_api
from utils.persona_generator import extract_username, fetch_user_activity, call_gemini
import os

app = Flask(__name__)
CORS(app)


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        link = data.get('link')
        if not link:
            return jsonify({'error': 'No link provided'}), 400
        persona = generate_persona_api(link)
        if isinstance(persona, dict) and persona.get('error'):
            return jsonify(persona), 200
        return jsonify(persona)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Error during analysis: {e}\n{tb}")
        return jsonify({'error': f'Internal server error: {str(e)}', 'traceback': tb}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
