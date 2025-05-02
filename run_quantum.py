from flask import Flask, request, jsonify, send_file
import cirq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import matplotlib
from sympy import symbols, Eq, latex
from PIL import Image, ImageDraw, ImageFont
import textwrap

app = Flask(__name__)
matplotlib.use('Agg')


def generate_formula_image(formula_type: str) -> BytesIO:
    width, height = 1000, 300
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        try:
            font_large = ImageFont.truetype("arial.ttf", 50)
            font_small = ImageFont.truetype("arial.ttf", 50)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        if formula_type == "superposition":
            formula_text = "ψ = αX + βO"
            explanation = "Состояние квантовой клетки в суперпозиции"
        elif formula_type == "probability":
            formula_text = "P(X) = sin²(θ/2)    P(O) = cos²(θ/2)"
            explanation = "Вероятности измерения состояний"
        elif formula_type == "measurement":
            formula_text = "ψ → X или O"
            explanation = "Коллапс волновой функции при измерении"
        elif formula_type == "x_gate":
            formula_text = "X = [[0, 1], [1, 0]]"
            explanation = "Матрица квантового ворота X"
        else:  # default/intro
            formula_text = "X = [1, 0]    O = [0, 1]"
            explanation = "Базисные состояния клетки"

        text_width = draw.textlength(formula_text, font=font_large)
        draw.text(((width - text_width) / 2, 100), formula_text, font=font_large, fill="black")

        text_width = draw.textlength(explanation, font=font_small)
        draw.text(((width - text_width) / 2, 150), explanation, font=font_small, fill="black")

    except Exception as e:
        print(f"Ошибка при генерации формулы: {e}")
        draw.text((10, 10), f"Ошибка: {str(e)}", fill="red")

    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf


@app.route('/formula/<formula_type>')
def get_formula(formula_type: str):
    valid_types = ["superposition", "probability", "measurement", "x_gate", "intro"]
    if formula_type not in valid_types:
        return "Invalid formula type", 404

    buf = generate_formula_image(formula_type)
    return send_file(buf, mimetype='image/png')


def plot_bloch_sphere(state, title):
    fig = plt.figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=20, azim=45)

    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))

    ax.plot_surface(x, y, z, color='b', alpha=0.1)

    ax.quiver(0, 0, 0, 1.5, 0, 0, color='k', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 1.5, 0, color='k', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 0, 1.5, color='k', arrow_length_ratio=0.1)

    ax.text(1.6, 0, 0, "X", fontsize=14)
    ax.text(0, 1.6, 0, "Y", fontsize=14)
    ax.text(0, 0, 1.6, "Z", fontsize=14)

    if state == 'superposition':
        ax.quiver(0, 0, 0, 1, 0, 0, color='r', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 0, 1, color='r', arrow_length_ratio=0.1)
        ax.text(0.5, 0, 0.5, "|ψ⟩", fontsize=16, color='r')
    elif state == 'x':
        ax.quiver(0, 0, 0, 1, 0, 0, color='r', arrow_length_ratio=0.1)
        ax.text(0.5, 0, 0, "|X⟩", fontsize=16, color='r')
    elif state == 'o':
        ax.quiver(0, 0, 0, 0, 0, 1, color='r', arrow_length_ratio=0.1)
        ax.text(0, 0, 0.5, "|O⟩", fontsize=16, color='r')
    elif state == 'measurement':
        ax.quiver(0, 0, 0, 0.7, 0, 0.7, color='r', arrow_length_ratio=0.1)
        ax.text(0.4, 0, 0.4, "Измерение", fontsize=12, color='r')

    ax.set_title(title, fontsize=14)
    ax.set_axis_off()
    plt.tight_layout(pad=0)

    canvas = FigureCanvas(fig)
    buf = BytesIO()
    canvas.print_png(buf)
    plt.close(fig)
    buf.seek(0)
    return buf


@app.route('/bloch_sphere/<state>')
def get_bloch_sphere(state):
    titles = {
        'superposition': 'Суперпозиция состояний',
        'x': 'Состояние X',
        'o': 'Состояние O',
        'measurement': 'Процесс измерения'
    }

    if state not in titles:
        return "Invalid state", 404

    buf = plot_bloch_sphere(state, titles[state])
    return send_file(buf, mimetype='image/png')


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