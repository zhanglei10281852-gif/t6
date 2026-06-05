import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import queue
import threading
from datetime import datetime

from data_simulator import BatterySimulator, BatteryData
from soc_estimator import SOCEstimator
from alarm_manager import AlarmManager, Alarm
from battery_view import BatteryTopologyView
from data_panel import RealTimeDataPanel
from plot_panel import PlotPanel
from data_exporter import DataExporter

class BMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BMS 电池管理系统模拟器")
        self.root.geometry("1280x768")
        
        self.data_queue = queue.Queue()
        self.alarm_queue = queue.Queue()
        self.alarm_shown = set()
        
        self.simulator = BatterySimulator(num_cells=16)
        self.soc_estimator = SOCEstimator(nominal_capacity=100.0, initial_soc=50.0)
        self.alarm_manager = AlarmManager()
        self.data_exporter = DataExporter()
        
        self.simulator.add_callback(self._on_data_received)
        self.alarm_manager.add_callback(self._on_alarm_update)
        
        self._setup_ui()
        self._start_processing()
        
        self.simulator.start()
        
    def _setup_ui(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出CSV", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_closing)
        
        setup_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=setup_menu)
        setup_menu.add_command(label="设置初始SOC", command=self._set_initial_soc)
        setup_menu.add_command(label="重置SOC", command=self._reset_soc)
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        control_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(control_frame, text="工作模式:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.mode_var = tk.StringVar(value="rest")
        ttk.Radiobutton(control_frame, text="充电", variable=self.mode_var, 
                        value="charge", command=self._change_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(control_frame, text="放电", variable=self.mode_var, 
                        value="discharge", command=self._change_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(control_frame, text="静置", variable=self.mode_var, 
                        value="rest", command=self._change_mode).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="导出CSV", command=self._export_csv).pack(side=tk.RIGHT, padx=10)
        ttk.Button(control_frame, text="清除报警", command=self._clear_alarms).pack(side=tk.RIGHT, padx=5)
        
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.battery_view = BatteryTopologyView(content_frame, num_cells=16)
        self.battery_view.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.data_panel = RealTimeDataPanel(content_frame)
        self.data_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.plot_panel = PlotPanel(content_frame, max_points=600)
        self.plot_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.status_bar = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_bar, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.alarm_status_label = tk.Label(self.status_bar, text="报警: 0", 
                                           anchor=tk.E, fg="green")
        self.alarm_status_label.pack(side=tk.RIGHT, padx=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _change_mode(self):
        mode = self.mode_var.get()
        self.simulator.set_mode(mode)
        
    def _on_data_received(self, data: BatteryData):
        soc = self.soc_estimator.update(data.total_current, data.cell_voltages, data.timestamp)
        data.soc = soc
        
        self.alarm_manager.check_alarms(data.cell_voltages, data.temperatures, data.total_current)
        
        self.data_exporter.add_record(
            data.timestamp, data.total_voltage, data.total_current,
            data.cell_voltages, data.soc, data.temperatures
        )
        
        self.data_queue.put(data)
        
    def _on_alarm_update(self, active_alarms, total_count):
        self.alarm_queue.put((active_alarms, total_count))
        
    def _process_data(self):
        try:
            while True:
                data = self.data_queue.get_nowait()
                self._update_ui(data)
        except queue.Empty:
            pass
            
        try:
            while True:
                active_alarms, total_count = self.alarm_queue.get_nowait()
                self._update_alarm_status(active_alarms, total_count)
        except queue.Empty:
            pass
            
        self.plot_panel.update_plot()
        
        self.root.after(100, self._process_data)
        
    def _start_processing(self):
        self.root.after(100, self._process_data)
        
    def _update_ui(self, data: BatteryData):
        self.battery_view.update_voltages(data.cell_voltages)
        self.data_panel.update_data(
            data.total_voltage, data.total_current, data.soc,
            data.mode, data.temperatures, data.cell_voltages
        )
        self.plot_panel.add_data(data.timestamp, data.total_voltage, data.total_current)
        
        current_time = datetime.fromtimestamp(data.timestamp).strftime('%H:%M:%S')
        self.status_label.config(text=f"运行中 | 最后更新: {current_time} | 数据点: {self.data_exporter.get_history_count()}")
        
    def _update_alarm_status(self, active_alarms, total_count):
        if active_alarms:
            self.alarm_status_label.config(text=f"报警: {len(active_alarms)} 活跃 / {total_count} 总计", fg="red")
            
            for alarm in active_alarms:
                if alarm.id not in self.alarm_shown:
                    self.alarm_shown.add(alarm.id)
                    level = "错误" if alarm.level == "error" else "警告"
                    messagebox.showwarning(f"BMS {level}", alarm.message)
        else:
            self.alarm_status_label.config(text=f"报警: 0 活跃 / {total_count} 总计", fg="green")
            
    def _clear_alarms(self):
        self.alarm_shown.clear()
        self.alarm_manager.clear_all_alarms()
        
    def _export_csv(self):
        self.data_exporter.export_to_csv(self.root)
        
    def _set_initial_soc(self):
        value = simpledialog.askfloat("设置初始SOC", "请输入初始SOC (0-100):", 
                                      minvalue=0.0, maxvalue=100.0, initialvalue=50.0)
        if value is not None:
            self.soc_estimator.reset(value)
            
    def _reset_soc(self):
        if messagebox.askyesno("确认", "确定要重置SOC到初始值吗？"):
            self.soc_estimator.reset()
            self.data_exporter.clear_history()
            self.plot_panel.clear_data()
            self.alarm_shown.clear()
            self.alarm_manager.clear_all_alarms()
            
    def _on_closing(self):
        self.simulator.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BMSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
