import numpy as np
import matplotlib

# ПЕРЕКЛЮЧАЕМ БЭКЕНД ПЕРЕД ИМПОРТОМ PYPLOT
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def generate_mandelbrot(center_x, center_y, zoom, width, height, max_iter):
    """Vectorized calculation of the Mandelbrot set."""
    x = np.linspace(center_x - 1.5 / zoom, center_x + 1.5 / zoom, width)
    y = np.linspace(center_y - 1.0 / zoom, center_y + 1.0 / zoom, height)
    X, Y = np.meshgrid(x, y)

    c = X + 1j * Y
    z = np.zeros_like(c)
    fractal_map = np.zeros(c.shape, dtype=int)
    mask = np.full(c.shape, True, dtype=bool)

    for i in range(max_iter):
        z[mask] = z[mask] ** 2 + c[mask]
        escaped = np.abs(z) > 2
        fractal_map[escaped & mask] = i
        mask[escaped] = False

    return fractal_map


# Settings
RES_X, RES_Y = 1000, 1000
MAX_ITER = 100

# Visualization and Export
plt.figure(figsize=(10, 10))
# Zooming into a specific interesting area (Seahorse Valley)
mandel_data = generate_mandelbrot(center_x=-0.7436, center_y=0.1318, zoom=50,
                                  width=RES_X, height=RES_Y, max_iter=MAX_ITER)

plt.imshow(mandel_data, cmap='magma', extent=[-2, 1, -1.5, 1.5])
plt.axis('off')
plt.title("Vectorized Mandelbrot Set", fontsize=14, color='white')
plt.gcf().set_facecolor('#1a1a1a')

# СОХРАНЯЕМ В ФАЙЛ ВМЕСТО plt.show()
output_file = "mandelbrot_fractal.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Success! Fractal image saved to: {output_file}")