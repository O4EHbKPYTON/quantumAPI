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

plt.switch_backend('Agg')
mpl.rcParams.update({
    "text.usetex": True,
    "font.size": 60,  # Глобально большой шрифт
    "text.latex.preamble": r"\usepackage{amsmath} \usepackage{amssymb} \boldmath"
})


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


def render_latex_to_image(latex_str, dpi=400, fontsize=60):
    fig = plt.figure(figsize=(6, 1))
    fig.patch.set_facecolor((51 / 255, 48 / 255, 95 / 255))  # Фон #33305F
    plt.axis('off')
    plt.text(0.5, 0.5, r"$\boldmath{" + latex_str + "}$",
             fontsize=fontsize,
             ha='center', va='center',
             color='white')  # БЕЛЫЙ текст

    canvas = FigureCanvas(fig)
    buf = BytesIO()
    canvas.print_png(buf)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf)
    return img


def generate_formula_image(formula_type: str) -> BytesIO:
    width, height = 600, 100
    image = Image.new('RGB', (width, height), (51, 48, 95))
    draw = ImageDraw.Draw(image)

    latex_formulas = {
        "basis_states": {
            "latex": r"|\mathbf{X}\rangle = \begin{bmatrix} \mathbf{1} \\ \mathbf{0} \end{bmatrix}, \quad |\mathbf{O}\rangle = \begin{bmatrix} \mathbf{0} \\ \mathbf{1} \end{bmatrix}",
            "description": ""
        },
        "x_gate": {
            "latex": r"\mathbf{X} = \begin{bmatrix} \mathbf{0} & \mathbf{1} \\ \mathbf{1} & \mathbf{0} \end{bmatrix}",
            "description": ""
        },
        "strategy": {
            "latex": r"\boldsymbol{\theta} = \boldsymbol{\pi} \cdot \textbf{power}",
            "description": ""
        },
        "superposition": {
            "latex": r"|\boldsymbol{\psi}\rangle = \boldsymbol{\alpha}|\mathbf{X}\rangle + \boldsymbol{\beta}|\mathbf{O}\rangle",
            "description": ""
        },
        "probability": {
            "latex": r"\mathbf{P}(\mathbf{X}) = \sin^2\left(\frac{\boldsymbol{\theta}}{2}\right), \quad \mathbf{P}(\mathbf{O}) = \cos^2\left(\frac{\boldsymbol{\theta}}{2}\right)",
            "description": ""
        },
        "measurement": {
            "latex": r"|\boldsymbol{\psi}\rangle \rightarrow |\mathbf{X}\rangle \text{ or } |\mathbf{O}\rangle",
            "description": ""
        },
        "intro": {
            "latex": r"\mathbf{I} = \begin{bmatrix} \mathbf{1} & \mathbf{0} \\ \mathbf{0} & \mathbf{1} \end{bmatrix}",
            "description": ""
        }
    }

    formula_data = latex_formulas.get(formula_type, {})
    if not formula_data:
        draw.text((10, 10), "Неизвестный тип формулы", fill="red")
    else:
        try:
            latex_img = render_latex_to_image(formula_data["latex"], fontsize=24)
            image.paste(latex_img, (width // 2 - latex_img.width // 2, height // 2 - latex_img.height // 2 - 8))

            font = get_russian_font(24)
            desc = formula_data["description"]
            bbox = draw.textbbox((0, 0), desc, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text(
                ((width - text_width) // 2, height - 50),
                desc,
                font=font,
                fill="white"
            )
        except Exception as e:
            draw.text((10, 10), f"Ошибка: {str(e)}", fill="red")

    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf


debug_save_all_formulas()