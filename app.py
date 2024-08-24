# flask_app/app.py
from flask import Flask, request, jsonify
from utils import process_query
import logging

app = Flask(__name__)

@app.route('/get-response', methods=['POST'])
def get_response():
    data = request.get_json()
    query = data['query']
    try:
        response_text = process_query(query)
        return jsonify({'response': response_text})
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return jsonify({'response': 'Sorry, an error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)