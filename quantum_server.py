from flask import Flask, jsonify
import cirq
import random

app = Flask(__name__)


@app.route('/run-cirq', methods=['GET'])
def run_quantum():
    # Квантовая схема с одним кубитом
    qubit = cirq.GridQubit(0, 0)
    circuit = cirq.Circuit()

    # Применим Hadamard — создаем суперпозицию
    circuit.append(cirq.H(qubit))
    circuit.append(cirq.measure(qubit, key='m'))

    # Запускаем симулятор
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=1)

    measured = int(result.measurements['m'][0])
    return jsonify({
        "message": "Квантовый результат",
        "result": measured
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
