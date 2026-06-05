import tkinter as tk
from tkinter import ttk
from typing import List

class RealTimeDataPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bd=2, relief=tk.GROOVE)
        self._setup_ui()
        
    def _setup_ui(self):
        title_label = tk.Label(self, text="实时数据面板", font=("Arial", 12, "bold"))
        title_label.pack(pady=5)
        
        main_container = tk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        summary_frame = tk.LabelFrame(main_container, text="电参数总览", padx=5, pady=5)
        summary_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(summary_frame, text="总电压:").grid(row=0, column=0, sticky=tk.W)
        self.total_voltage_label = tk.Label(summary_frame, text="52.800 V", font=("Arial", 10, "bold"), fg="#2196F3")
        self.total_voltage_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        tk.Label(summary_frame, text="总电流:").grid(row=0, column=2, sticky=tk.W)
        self.total_current_label = tk.Label(summary_frame, text="0.00 A", font=("Arial", 10, "bold"), fg="#FF9800")
        self.total_current_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 20))
        
        tk.Label(summary_frame, text="SOC:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.soc_label = tk.Label(summary_frame, text="50.0 %", font=("Arial", 10, "bold"), fg="#4CAF50")
        self.soc_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 20), pady=5)
        
        tk.Label(summary_frame, text="模式:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.mode_label = tk.Label(summary_frame, text="静置", font=("Arial", 10, "bold"), fg="#9E9E9E")
        self.mode_label.grid(row=1, column=3, sticky=tk.W, padx=(10, 20), pady=5)
        
        temp_frame = tk.LabelFrame(main_container, text="温度信息", padx=5, pady=5)
        temp_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(temp_frame, text="最高温度:").grid(row=0, column=0, sticky=tk.W)
        self.max_temp_label = tk.Label(temp_frame, text="25.0 ℃", font=("Arial", 10, "bold"), fg="#F44336")
        self.max_temp_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        tk.Label(temp_frame, text="最低温度:").grid(row=0, column=2, sticky=tk.W)
        self.min_temp_label = tk.Label(temp_frame, text="25.0 ℃", font=("Arial", 10, "bold"), fg="#2196F3")
        self.min_temp_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 20))
        
        cell_frame = tk.LabelFrame(main_container, text="电芯电压列表 (V)", padx=5, pady=5)
        cell_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.cell_tree = ttk.Treeview(cell_frame, columns=("idx", "v1", "v2", "v3", "v4"), show="headings", height=4)
        self.cell_tree.heading("idx", text="#")
        self.cell_tree.heading("v1", text="电压1")
        self.cell_tree.heading("v2", text="电压2")
        self.cell_tree.heading("v3", text="电压3")
        self.cell_tree.heading("v4", text="电压4")
        
        self.cell_tree.column("idx", width=30, anchor=tk.CENTER)
        self.cell_tree.column("v1", width=70, anchor=tk.CENTER)
        self.cell_tree.column("v2", width=70, anchor=tk.CENTER)
        self.cell_tree.column("v3", width=70, anchor=tk.CENTER)
        self.cell_tree.column("v4", width=70, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(cell_frame, orient=tk.VERTICAL, command=self.cell_tree.yview)
        self.cell_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cell_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_data(self, total_voltage: float, total_current: float, soc: float, 
                    mode: str, temperatures: List[float], cell_voltages: List[float]):
        self.total_voltage_label.config(text=f"{total_voltage:.3f} V")
        self.total_current_label.config(text=f"{total_current:.2f} A")
        self.soc_label.config(text=f"{soc:.1f} %")
        
        mode_text = {"charge": "充电", "discharge": "放电", "rest": "静置"}.get(mode, mode)
        self.mode_label.config(text=mode_text)
        
        max_temp = max(temperatures)
        min_temp = min(temperatures)
        self.max_temp_label.config(text=f"{max_temp:.1f} ℃")
        self.min_temp_label.config(text=f"{min_temp:.1f} ℃")
        
        for item in self.cell_tree.get_children():
            self.cell_tree.delete(item)
            
        for row in range(4):
            idx = row * 4 + 1
            voltages = []
            for col in range(4):
                cell_idx = row * 4 + col
                if cell_idx < len(cell_voltages):
                    voltages.append(f"{cell_voltages[cell_idx]:.3f}")
                else:
                    voltages.append("-")
            self.cell_tree.insert("", tk.END, values=(idx, voltages[0], voltages[1], voltages[2], voltages[3]))
