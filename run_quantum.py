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
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath} \usepackage{amsfonts} \usepackage{amssymb}'


def get_russian_font(size=40):
    try:
        font_path = "arial.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(font_path, size)
    except:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default(size)


def debug_save_image(image, filename="debug.png"):
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)
    image.save(debug_dir / filename)


def debug_save_all_formulas():
    test_dir = Path("test_formulas")
    test_dir.mkdir(exist_ok=True)

    formula_types = [
        "basis_states", "x_gate", "strategy",
        "superposition", "probability", "measurement", "intro"
    ]

    for formula_type in formula_types:
        img_data = generate_formula_image(formula_type)
        with open(test_dir / f"{formula_type}.png", "wb") as f:
            f.write(img_data.getbuffer())

    print(f"Тестовые изображения сохранены в {test_dir.absolute()}")


def render_latex_to_image(latex_str, dpi=300, fontsize=20):
    fig = plt.figure(figsize=(6, 2))
    fig.patch.set_facecolor((0.5, 0.5, 0.5))
    plt.axis('off')
    plt.text(0.5, 0.5, f"${latex_str}$", fontsize=fontsize,
             ha='center', va='center', color='black')

    canvas = FigureCanvas(fig)
    buf = BytesIO()
    canvas.print_png(buf)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf)
    return img


def generate_formula_image(formula_type: str) -> BytesIO:
    width, height = 640, 317
    image = Image.new('RGB', (width, height), (127, 127, 127))
    draw = ImageDraw.Draw(image)

    latex_formulas = {
        "basis_states": {
            "latex": r"|X\rangle = \begin{bmatrix} 1 \\ 0 \end{bmatrix}, \quad |O\rangle = \begin{bmatrix} 0 \\ 1 \end{bmatrix}",
            "description": ""
        },
        "x_gate": {
            "latex": r"X = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}",
            "description": ""
        },
        "strategy": {
            "latex": r"\theta = \pi \cdot \text{power}",
            "description": ""
        },
        "superposition": {
            "latex": r"|\psi\rangle = \alpha|X\rangle + \beta|O\rangle",
            "description": ""
        },
        "probability": {
            "latex": r"P(X) = \sin^2\left(\frac{\theta}{2}\right), \quad P(O) = \cos^2\left(\frac{\theta}{2}\right)",
            "description": ""
        },
        "measurement": {
            "latex": r"|\psi\rangle \rightarrow |X\rangle \text{ or } |O\rangle",
            "description": ""
        },
        "intro": {
            "latex": r"\mathbb{I} = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}",
            "description": ""
        }
    }

    formula_data = latex_formulas.get(formula_type, {})
    if not formula_data:
        draw.text((10, 10), "Неизвестный тип формулы", fill="red")
    else:
        try:
            latex_img = render_latex_to_image(formula_data["latex"], fontsize=24)
            image.paste(latex_img, (width // 2 - latex_img.width // 2, height // 2 - latex_img.height // 2 - 20))

            font = get_russian_font(24)
            desc = formula_data["description"]
            bbox = draw.textbbox((0, 0), desc, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text(
                ((width - text_width) // 2, height - 50),
                desc,
                font=font,
                fill="black"
            )
        except Exception as e:
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


def create_figure():
    fig = plt.figure(figsize=(10, 10), dpi=100, facecolor=(0.5, 0.5, 0.5))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor((0.5, 0.5, 0.5))
    ax.view_init(elev=20, azim=45)
    lim = 1.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.dist = 5
    return fig, ax

def draw_axes(ax, arrow_scale=2.5, text_scale=2.5, font_size=40):
    ax.quiver(0, 0, 0, arrow_scale, 0, 0, color='k', arrow_length_ratio=0.1, linewidth=1.5)
    ax.quiver(0, 0, 0, 0, arrow_scale, 0, color='k', arrow_length_ratio=0.1, linewidth=1.5)
    ax.quiver(0, 0, 0, 0, 0, arrow_scale, color='k', arrow_length_ratio=0.1, linewidth=1.5)
    ax.text(text_scale, 0, 0, "X", fontsize=font_size)
    ax.text(0, text_scale, 0, "Y", fontsize=font_size)
    ax.text(0, 0, text_scale, "Z", fontsize=font_size)

def draw_sphere(ax):
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    lim = 2.0
    x = lim * np.outer(np.cos(u), np.sin(v))
    y = lim * np.outer(np.sin(u), np.sin(v))
    z = lim * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='w', alpha=0.2)

def draw_state(ax, state, font_size=40):
    ratio = 0.15
    linewidth = 6
    zorder = 5
    if state == 'superposition':
        ax.quiver(0, 0, 0, 1.4, 0, 0, color='r', arrow_length_ratio=ratio, linewidth=linewidth, zorder=zorder)
        ax.quiver(0, 0, 0, 0, 0, 1.4, color='r', arrow_length_ratio=ratio, linewidth=linewidth, zorder=zorder)
        ax.text(0.6, 0, 0.6, r"$|\psi\rangle$", fontsize=font_size + 10, color='r', zorder=10)
    elif state == 'x':
        ax.quiver(0, 0, 0, 1.2, 0, 0, color='r', arrow_length_ratio=ratio, linewidth=linewidth, zorder=zorder)
        ax.text(0.6, 0, 0, r"$|X\rangle$", fontsize=font_size + 4, color='r', zorder=10)
    elif state == 'o':
        ax.quiver(0, 0, 0, 0, 0, 1.2, color='r', arrow_length_ratio=ratio, linewidth=linewidth, zorder=zorder)
        ax.text(0, 0, 0.6, r"$|O\rangle$", fontsize=font_size + 4, color='r', zorder=10)
    elif state == 'measurement':
        ax.quiver(0, 0, 0, 0.85, 0, 0.85, color='r', arrow_length_ratio=ratio, linewidth=linewidth, zorder=zorder)
        ax.text(0.5, 0, 0.5, "Measurement", fontsize=font_size + 2, color='r', zorder=10)

def plot_bloch_sphere(state, title):
    output_dir = "bloch_sphere_images"
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = create_figure()
    draw_sphere(ax)
    draw_axes(ax)
    draw_state(ax, state)
    ax.set_title(title, fontsize=30)
    ax.set_axis_off()
    plt.tight_layout(pad=0.5)

    filename = f"{state}_{title.replace(' ', '_')}.png"
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())

    plt.close(fig)
    print(f"Saved: {filepath}")

    canvas = FigureCanvas(fig)
    buf = BytesIO()
    canvas.print_png(buf)
    plt.close(fig)
    buf.seek(0)
    return buf


@app.route('/bloch_sphere/<state>')
def get_bloch_sphere(state):
    titles = {
        'superposition': 'Superposition',
        'x': 'State X',
        'o': 'State O',
        'measurement': 'measurement'
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
    debug_save_all_formulas()
    app.run(port=8000)