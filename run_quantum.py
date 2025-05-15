from flask import Flask, request, jsonify, send_file
import cirq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path
import os
import matplotlib as mpl

app = Flask(__name__)
plt.switch_backend('Agg')




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
        "result": "X" if list(result.measurements.values())[0][0] else "O",
        "cell_index": cell_index
    })


if __name__ == '__main__':
    app.run(port=8000)