import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons  # Для генерации нелинейных данных

# Настройка для стабильной визуализации без окон
import matplotlib

matplotlib.use('Agg')


class NeuralNetworkFromScratch:
    def __init__(self, input_dim, hidden_dim, output_dim, learning_rate=0.1):
        self.lr = learning_rate

        # 1. Инициализация весов (He initialization для ReLU)
        self.w1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2. / input_dim)
        self.b1 = np.zeros((1, hidden_dim))

        # Инициализация для выходного слоя (Xavier для Sigmoid)
        self.w2 = np.random.randn(hidden_dim, output_dim) * np.sqrt(1. / hidden_dim)
        self.b2 = np.zeros((1, output_dim))

        self.weight_history = []  # Для визуализации гистограмм

    # Функции активации и их производные
    def relu(self, x): return np.maximum(0, x)

    def relu_deriv(self, x): return (x > 0).astype(float)

    def sigmoid(self, x): return 1 / (1 + np.exp(-x))

    def sigmoid_deriv(self, x): return x * (1 - x)  # x здесь уже sigmoid(z)

    def forward(self, x):
        """Прямой проход (Forward Propagation)"""
        # Скрытый слой
        self.z1 = np.dot(x, self.w1) + self.b1
        self.a1 = self.relu(self.z1)

        # Выходной слой
        self.z2 = np.dot(self.a1, self.w2) + self.b2
        self.a2 = self.sigmoid(self.z2)  # Предсказанная вероятность
        return self.a2

    def backward(self, x, y, output):
        """Обратное распространение (Backpropagation)"""
        # 1. Ошибка выходного слоя (Cross-Entropy Loss derivative)
        # dL/dz2 = (a2 - y)
        error_output = output - y

        # Градиенты для весов выходного слоя
        # dL/dw2 = a1.T * dL/dz2
        dw2 = np.dot(self.a1.T, error_output)
        db2 = np.sum(error_output, axis=0, keepdims=True)

        # 2. Ошибка скрытого слоя
        # dL/da1 = dL/dz2 * w2.T
        # dL/dz1 = dL/da1 * ReLU_deriv(z1)
        error_hidden = np.dot(error_output, self.w2.T) * self.relu_deriv(self.a1)

        # Градиенты для весов скрытого слоя
        dw1 = np.dot(x.T, error_hidden)
        db1 = np.sum(error_hidden, axis=0, keepdims=True)

        # 3. Обновление весов (градиентный спуск)
        self.w2 -= self.lr * dw2
        self.b2 -= self.lr * db2
        self.w1 -= self.lr * dw1
        self.b1 -= self.lr * db1

        # Сохраняем историю весов для анализа
        self.weight_history.append(self.w1.copy().flatten())


# --- Подготовка данных (эмуляция макропоказателей) ---
# Испульзуем 'make_moons' для создания сложной нелинейной границы
X, y = make_moons(n_samples=500, noise=0.2, random_state=42)
y = y.reshape(-1, 1)  # Преобразуем в вектор-столбец

# --- Обучение модели ---
nn = NeuralNetworkFromScratch(input_dim=2, hidden_dim=10, output_dim=1, learning_rate=0.01)
epochs = 1000
losses = []

print("[*] Starting training from scratch...")
for epoch in range(epochs):
    # Прямой проход
    output = nn.forward(X)

    # Расчет ошибки (Binary Cross-Entropy)
    loss = -np.mean(y * np.log(output) + (1 - y) * np.log(1 - output))
    losses.append(loss)

    # Обратный проход
    nn.backward(X, y, output)

    if epoch % 200 == 0:
        print(f"Epoch {epoch}: Loss = {loss:.4f}")

print("[SUCCESS] Training complete.")


# --- Визуализация 1: граница принятия решений (decision boundary) ---
def plot_decision_boundary(X, y, model, filename):
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))

    Z = model.forward(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.figure(figsize=(10, 7))
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral, alpha=0.8)
    plt.scatter(X[:, 0], X[:, 1], c=y.flatten(), s=40, cmap=plt.cm.Spectral, edgecolors='black')
    plt.title("Decision Boundary: numPy neural network from scratch")
    plt.savefig(filename, dpi=300)
    plt.close()


plot_decision_boundary(X, y, nn, "decision_boundary_final.png")
print("[-] Decision boundary saved as: decision_boundary_final.png")

# --- Визуализация 2: гистограмма весов ---
plt.figure(figsize=(10, 6))
plt.hist(nn.w1.flatten(), bins=30, alpha=0.7, color='#2c3e50', edgecolor='black')
plt.title("Weight distribution (hidden layer w1) after training")
plt.grid(axis='y', alpha=0.5)
plt.savefig("weight_histogram.png")
print("[-] Weight histogram saved as: weight_histogram.png")
