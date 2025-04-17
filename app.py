from flask import Flask, jsonify
import qsharp
from QuantumExample import MeasureQubit  # Импортируем Q# операцию

app = Flask(__name__)

@app.route('/run-qsharp', methods=['GET'])
def run_qsharp():
    result = MeasureQubit.simulate()
    return jsonify({
        "message": "Q# Результат",
        "result": int(result)
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
