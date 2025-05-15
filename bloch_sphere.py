import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

def create_figure():
    fig = plt.figure(figsize=(10, 15), dpi=100, facecolor='#33305F')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#33305F')
    # Серый
    # fig = plt.figure(figsize=(10, 15), dpi=100, facecolor=(0.5, 0.5, 0.5))
    # ax = fig.add_subplot(111, projection='3d')
    # ax.set_facecolor((0.5, 0.5, 0.5))
    ax.view_init(elev=20, azim=45)
    lim = 2.0
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.set_box_aspect([1, 1, 0.9])
    ax.dist = 5
    ax.grid(False)
    ax.set_axis_off()
    return fig, ax

def draw_axes(ax, arrow_scale=2.5, text_scale=2.5, font_size=40):
    ax.quiver(0, 0, 0, arrow_scale+1, 0, 0, color='w', arrow_length_ratio=0.1, linewidth=1.5, zorder=1)
    ax.quiver(0, 0, 0, 0, arrow_scale+1, 0, color='w', arrow_length_ratio=0.1, linewidth=1.5, zorder=1)
    ax.quiver(0, 0, 0, 0, 0, arrow_scale, color='w', arrow_length_ratio=0.1, linewidth=1.5, zorder=1)
    ax.text(text_scale + 1.5, 0, 0, "X", fontsize=font_size, color='w')  # Добавлен color='w'
    ax.text(0, text_scale + 1, 0, "Y", fontsize=font_size, color='w')  # Добавлен color='w'
    ax.text(0, 0, text_scale, "Z", fontsize=font_size, color='w')

def draw_sphere(ax):
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    lim = 2.0
    x = lim * np.outer(np.cos(u), np.sin(v))
    y = lim * np.outer(np.sin(u), np.sin(v))
    z = lim * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='w', alpha=0.3, zorder=0)

def draw_state_vector(ax, vector, label, font_size=45, alpha=1.0):
    ratio = 0.15
    zorder = 100

    ax.quiver(0, 0, 0, vector[0], vector[1], vector[2],
              color='white', alpha=alpha, arrow_length_ratio=ratio,
              linewidth=6, zorder=zorder + 10)

    ax.text(*(np.array(vector)*0.6), label, fontsize=font_size,
            color='white', zorder=zorder + 11, fontweight='bold')

def draw_equator(ax, radius=2.0):
    theta = np.linspace(0, 2 * np.pi, 100)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = np.zeros_like(x)
    ax.plot(x, y, z, linestyle='--', color='w', linewidth=2)

def save_bloch_sphere(state_name, vector, label):
    fig, ax = create_figure()
    draw_axes(ax)
    draw_sphere(ax)
    draw_equator(ax)
    s= 3.1
    ax.text(0, 0, s, r'$|0\rangle$', fontsize=40, color='w', ha='center')
    ax.text(0, 0, -s, r'$|1\rangle$', fontsize=40, color='w', ha='center')

    draw_state_vector(ax, vector, label)

    output_dir = "bloch_sphere_images"
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(os.path.join(output_dir, f"{state_name}.png"), bbox_inches='tight', dpi=100)
    plt.close(fig)
    print(f"Saved: {state_name}.png")

# |0⟩ (по оси Z вверх)
save_bloch_sphere("state_0", [0, 0, 1.2], r"$|\psi\rangle = |0\rangle$")

# |1⟩ (по оси Z вниз)
save_bloch_sphere("state_1", [0, 0, -1.2], r"$|\psi\rangle = |1\rangle$")

# |+⟩ = (|0⟩ + |1⟩)/√2 (по оси X)
save_bloch_sphere("state_plus", [1.2, 0, 0], r"$|\psi\rangle = |+\rangle$")

# |−⟩ = (|0⟩ − |1⟩)/√2 (по оси -X)
save_bloch_sphere("state_minus", [-1.2, 0, 0], r"$|\psi\rangle = |-\rangle$")

# 2. Состояние с неопределённостью (двойной вектор)
def save_superposition_state():
    fig, ax = create_figure()
    draw_axes(ax)
    draw_sphere(ax)
    draw_equator(ax)

    draw_state_vector(ax, [0, 0, 1.5], "", alpha=1)
    draw_state_vector(ax, [0, 0, -1.5], "", alpha=1)
    ax.text(0, 0, 1.8, "", fontsize=40, color='r', ha='center')
    s = 3.1
    ax.text(0, 0, s, r'$|0\rangle$', fontsize=40, color='w', ha='center')
    ax.text(0, 0, -s, r'$|1\rangle$', fontsize=40, color='w', ha='center')

    output_dir = "bloch_sphere_images"
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(os.path.join(output_dir, "superposition_state.png"), bbox_inches='tight', dpi=100)
    plt.close(fig)
    print("Saved: superposition_state.png")

# Создаем изображение состояния с неопределённостью
save_bloch_sphere("superposition_state", [0, 0, 0], "superposition state")
save_superposition_state()

# 3. Изображение с коллапсом состояния (измерение)
def draw_measurement_collapse(ax):
    # Вектор перед коллапсом
    draw_state_vector(ax, [1.5, 0, 0], "No measurmnet", alpha=0.6)

    # Вектор после коллапса на |0⟩
    draw_state_vector(ax, [0, 0, 1.5], r"$|\psi\rangle = |0\rangle$", alpha=1.0)

    ax.text(0, 0, 2.2, "measurement collapse", fontsize=40, color='k', ha='center')

# Создаем изображение коллапса состояния
save_bloch_sphere("measurement_collapse_0", [0, 0, 1.5], r"$|\psi\rangle = |0\rangle$")
save_bloch_sphere("measurement_collapse_1", [0, 0, -1.5], r"$|\psi\rangle = |1\rangle$")

def theta_to_vector(theta, phi=0, r=1.2):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return [x, y, z]

# def save_interaction_states():
#     thetas = np.linspace(0.1, 1.0, 10)
#     output_dir = "bloch_interaction_images"
#     os.makedirs(output_dir, exist_ok=True)
#
#     for theta_x in thetas:
#         for theta_o in thetas:
#             fig = plt.figure(figsize=(20, 10), dpi=100, facecolor=(0.5, 0.5, 0.5))
#
#             # --- Левая сфера (X) ---
#             ax1 = fig.add_subplot(1, 2, 1, projection='3d')
#             ax1.set_title(f"Player X (θ={theta_x:.1f})", fontsize=20)
#             ax1.set_facecolor((0.5, 0.5, 0.5))
#             ax1.view_init(elev=20, azim=45)
#             ax1.set_axis_off()
#             ax1.set_box_aspect([1, 1, 0.9])
#             ax1.set_xlim(-2, 2)
#             ax1.set_ylim(-2, 2)
#             ax1.set_zlim(-2, 2)
#
#             draw_axes(ax1)
#             draw_sphere(ax1)
#             draw_equator(ax1)
#             vector_x = theta_to_vector(theta_x)
#             draw_state_vector(ax1, vector_x, "X")
#
#             # --- Правая сфера (O) ---
#             ax2 = fig.add_subplot(1, 2, 2, projection='3d')
#             ax2.set_title(f"Player O (θ={theta_o:.1f})", fontsize=20)
#             ax2.set_facecolor((0.5, 0.5, 0.5))
#             ax2.view_init(elev=20, azim=45)
#             ax2.set_axis_off()
#             ax2.set_box_aspect([1, 1, 0.9])
#             ax2.set_xlim(-2, 2)
#             ax2.set_ylim(-2, 2)
#             ax2.set_zlim(-2, 2)
#
#             draw_axes(ax2)
#             draw_sphere(ax2)
#             draw_equator(ax2)
#             vector_o = theta_to_vector(theta_o)
#             draw_state_vector(ax2, vector_o, "O")
#
#             filename = f"interaction_X_{theta_x:.1f}_O_{theta_o:.1f}.png"
#             fig.savefig(os.path.join(output_dir, filename), bbox_inches='tight', dpi=100)
#             plt.close(fig)
#             print(f"Saved: {filename}")
#
# save_interaction_states()