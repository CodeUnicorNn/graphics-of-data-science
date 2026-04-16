import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Переключаемся в headless режим для стабильности в PyCharm
import matplotlib

matplotlib.use('Agg')


def replicator_dynamics(y, t, payoff_matrix):
    """
    Репликаторное уравнение: dx/dt = x * (f_x - average_fitness)
    y: доля стратегии 'Сотрудничество' (x)
    """
    x = y[0]
    # Доля второй стратегии (Агрессия)
    1 - x

    # Матрица выигрышей (Payoff Matrix)
    #            Cooperate | Defect
    # Cooperate [   3,        0   ]
    # Defect    [   5,        1   ]

    # Фитнес (выгода) каждой стратегии
    f_coop = payoff_matrix[0, 0] * x + payoff_matrix[0, 1] * (1 - x)
    f_defect = payoff_matrix[1, 0] * x + payoff_matrix[1, 1] * (1 - x)

    # Средний фитнес популяции
    avg_fitness = x * f_coop + (1 - x) * f_defect

    # Изменение доли сотрудничающих
    dxdt = x * (f_coop - avg_fitness)
    return [dxdt]


# 1. Настройка матрицы выигрышей (Типичная Дилемма Заключенного)
# Параметры: T (Temptation), R (Reward), P (Punishment), S (Sucker's payoff)
payoff = np.array([
    [3, 0],  # Награда за взаимное сотрудничество / Проигрыш обманутого
    [5, 1]  # Выигрыш обманщика / Наказание за взаимную агрессию
])

# 2. Построение фазового портрета
x_values = np.linspace(0, 1, 20)
y_values = np.zeros_like(x_values)  # В 1D системе y всегда 0 для визуализации вектора

# Вычисляем векторы скорости изменения
dx = [replicator_dynamics([xi], 0, payoff)[0] for xi in x_values]

plt.figure(figsize=(10, 4))
plt.quiver(x_values, y_values, dx, np.zeros_like(dx), color='#2c3e50', scale=15)
plt.axhline(0, color='black', lw=1)
plt.title("Evolutionary Dynamics: Path to Realism (Defection)")
plt.xlabel("Share of Cooperating States (x)")
plt.yticks([])  # Убираем ось Y для 1D графика
plt.grid(alpha=0.3)

# 3. Сохранение результата
plt.savefig("replicator_dynamics.png", dpi=300)
print("Phase portrait saved as replicator_dynamics.png")