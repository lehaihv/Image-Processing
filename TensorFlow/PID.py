import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGridLayout
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PIDSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PID Controller Simulator")
        self.setGeometry(100, 100, 900, 600)

        self.kp = 2.0
        self.ki = 0.1
        self.kd = 1.0

        self.init_ui()
        self.plot_pid()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Matplotlib figure
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Sliders for PID
        grid = QGridLayout()

        self.kp_slider = self.create_slider(0, 100, self.kp * 10, self.update_kp)
        self.ki_slider = self.create_slider(0, 100, self.ki * 100, self.update_ki)
        self.kd_slider = self.create_slider(0, 100, self.kd * 10, self.update_kd)

        grid.addWidget(QLabel("Kp"), 0, 0)
        grid.addWidget(self.kp_slider, 0, 1)
        self.kp_label = QLabel(f"{self.kp:.2f}")
        grid.addWidget(self.kp_label, 0, 2)

        grid.addWidget(QLabel("Ki"), 1, 0)
        grid.addWidget(self.ki_slider, 1, 1)
        self.ki_label = QLabel(f"{self.ki:.2f}")
        grid.addWidget(self.ki_label, 1, 2)

        grid.addWidget(QLabel("Kd"), 2, 0)
        grid.addWidget(self.kd_slider, 2, 1)
        self.kd_label = QLabel(f"{self.kd:.2f}")
        grid.addWidget(self.kd_label, 2, 2)

        layout.addLayout(grid)

    def create_slider(self, min_val, max_val, init_val, callback):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(int(init_val))
        slider.setTickInterval(1)
        slider.setSingleStep(1)
        slider.valueChanged.connect(callback)
        return slider

    def update_kp(self, value):
        self.kp = value / 10.0
        self.kp_label.setText(f"{self.kp:.2f}")
        self.plot_pid()

    def update_ki(self, value):
        self.ki = value / 100.0
        self.ki_label.setText(f"{self.ki:.2f}")
        self.plot_pid()

    def update_kd(self, value):
        self.kd = value / 10.0
        self.kd_label.setText(f"{self.kd:.2f}")
        self.plot_pid()

    def simulate_pid(self, Kp, Ki, Kd, setpoint=75.0, time_end=60.0, dt=0.1):
        temp = 20.0
        ambient = 20.0
        integral = 0.0
        prev_error = 0.0

        time_data = []
        temp_data = []
        setpoint_data = []

        time = 0.0
        while time <= time_end:
            error = setpoint - temp
            integral += error * dt
            derivative = (error - prev_error) / dt
            prev_error = error

            power = Kp * error + Ki * integral + Kd * derivative
            power = max(0.0, min(power, 100.0))

            cooling = 0.1 * (temp - ambient)
            temp += (power - cooling) * dt

            time_data.append(time)
            temp_data.append(temp)
            setpoint_data.append(setpoint)
            time += dt

        return np.array(time_data), np.array(temp_data), np.array(setpoint_data)

    def plot_pid(self):
        t, temp, setpoint = self.simulate_pid(self.kp, self.ki, self.kd)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(t, temp, label="Temperature")
        ax.plot(t, setpoint, '--', label="Setpoint")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title("PID Control Response")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PIDSimulator()
    window.show()
    sys.exit(app.exec())
