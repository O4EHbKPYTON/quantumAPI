from flask import Flask, request, jsonify, send_file
import cirq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

app = Flask(__name__)
plt.switch_backend('Agg')


def get_russian_font(size=40):
    try:
        font_path = "arial.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(font_path, size)
    except:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default(size)


def generate_formula_image(formula_type: str) -> BytesIO:
    width, height = 1400, 500
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        formulas = {
            "basis_states": ("X = [1 0]    O = [0 1]", "Базисные состояния"),
            "x_gate": ("X-Gate Матрица Паули: [[0 1][1 0]]", "Инвертирует X и O"),
            "strategy": ("θ = π * power", "Управление углом поворота"),
            "superposition": ("Состояние = αX + βO", "Суперпозиция состояний"),
            "probability": ("P(X) = sin²(θ/2)  P(O) = cos²(θ/2)", "Вероятности измерений"),
            "measurement": ("Состояние → X или O", "Коллапс волновой функции"),
            "intro": ("X = [1 0]    O = [0 1]", "Начальные состояния")
        }

        formula_text, explanation = formulas.get(formula_type, ("", ""))

        font_large = get_russian_font(65)
        font_small = get_russian_font(65)

        # Рисуем основную формулу
        bbox = draw.textbbox((0, 0), formula_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        draw.text(
            ((width - text_width) / 2, 100),
            formula_text,
            font=font_large,
            fill="black"
        )

        bbox = draw.textbbox((0, 0), explanation, font=font_small)
        text_width = bbox[2] - bbox[0]
        draw.text(
            ((width - text_width) / 2, 250),
            explanation,
            font=font_small,
            fill="#444444"
        )

    except Exception as e:
        print(f"Error: {e}")
        draw.text((10, 10), f"Ошибка: {str(e)}", fill="red")

    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf

@app.route('/formula/<formula_type>')
def get_formula(formula_type: str):
    valid_types = ["basis_states", "x_gate", "strategy", "superposition",
                  "probability", "measurement", "intro"]
    if formula_type not in valid_types:
        return "Invalid formula type", 404

    buf = generate_formula_image(formula_type)
    return send_file(buf, mimetype='image/png')


def plot_bloch_sphere(state, title):
    fig = plt.figure(figsize=(8, 8), dpi=100, facecolor=(0.5, 0.5, 0.5))
    ax = fig.add_subplot(111, projection='3d') #
    ax.view_init(elev=20, azim=45)

    ax.set_facecolor((0.5, 0.5, 0.5))

    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))

    ax.plot_surface(x, y, z, color='w', alpha=0.9)

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