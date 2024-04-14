from flask import Flask, request, jsonify
from predict import predict_solution

app: Flask = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data: dict[str, str] = request.get_json()
        error_message: str = data['errorMessage']
        prediction, confidence = predict_solution(error_message)
        return jsonify({'prediction': prediction, 'confidence': str(confidence)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)