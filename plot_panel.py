import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
import time
from collections import deque
from typing import Deque

class PlotPanel(tk.Frame):
    def __init__(self, parent, max_points: int = 600):
        super().__init__(parent, bd=2, relief=tk.GROOVE)
        self.max_points = max_points
        self.timestamps: Deque[float] = deque(maxlen=max_points)
        self.voltages: Deque[float] = deque(maxlen=max_points)
        self.currents: Deque[float] = deque(maxlen=max_points)
        
        self._setup_ui()
        
    def _setup_ui(self):
        title_label = tk.Label(self, text="实时趋势曲线 (最近5分钟)", font=("Arial", 12, "bold"))
        title_label.pack(pady=5)
        
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        
        self.fig.tight_layout(pad=3.0)
        
        self.ax1.set_title("总电压")
        self.ax1.set_ylabel("电压 (V)")
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_title("总电流")
        self.ax2.set_ylabel("电流 (A)")
        self.ax2.set_xlabel("时间")
        self.ax2.grid(True, alpha=0.3)
        
        self.line1, = self.ax1.plot([], [], label="电压", color="#2196F3", linewidth=1.5)
        self.line2, = self.ax2.plot([], [], label="电流", color="#FF9800", linewidth=1.5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def add_data(self, timestamp: float, voltage: float, current: float):
        self.timestamps.append(timestamp)
        self.voltages.append(voltage)
        self.currents.append(current)
        
    def update_plot(self):
        if len(self.timestamps) < 2:
            return
            
        times = [datetime.fromtimestamp(t) for t in self.timestamps]
        
        self.line1.set_data(times, list(self.voltages))
        self.line2.set_data(times, list(self.currents))
        
        self.ax1.relim()
        self.ax1.autoscale_view()
        
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        self.fig.autofmt_xdate()
        self.canvas.draw_idle()
        
    def clear_data(self):
        self.timestamps.clear()
        self.voltages.clear()
        self.currents.clear()
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        self.canvas.draw_idle()
        
    def get_history_data(self):
        return {
            'timestamps': list(self.timestamps),
            'voltages': list(self.voltages),
            'currents': list(self.currents)
        }
