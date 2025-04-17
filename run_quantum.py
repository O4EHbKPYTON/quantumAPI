from flask import Flask, request, jsonify
import cirq

app = Flask(__name__)


def bitstr(bits):
    for b in bits:
        return "X" if b else "O"


@app.route('/run-cirq', methods=['POST'])
def run_cirq():
    data = request.get_json()
    qubit_name = data.get('qubit_name', 'X')
    power = data.get('power', 1.0)
    cell_index = data.get('cell_index', -1)

    qubit = cirq.NamedQubit(qubit_name)
    circuit = cirq.Circuit()
    circuit.append(cirq.X(qubit) ** power)
    circuit.append(cirq.measure(qubit))

    simulator = cirq.Simulator()
    result = simulator.run(circuit)

    return jsonify({
        "result": bitstr(result.measurements.values()),
        "cell_index": cell_index
    })


if __name__ == '__main__':
    app.run(port=8000)