import tkinter as tk
from tkinter import ttk
from typing import List

class BatteryTopologyView(tk.Frame):
    def __init__(self, parent, num_cells: int = 16):
        super().__init__(parent, bd=2, relief=tk.GROOVE)
        self.num_cells = num_cells
        self.cell_rects = []
        self.cell_labels = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        title_label = tk.Label(self, text="电池组拓扑图 (16S)", font=("Arial", 12, "bold"))
        title_label.pack(pady=5)
        
        legend_frame = tk.Frame(self)
        legend_frame.pack(pady=5)
        
        tk.Label(legend_frame, bg="#4CAF50", width=3, height=1).grid(row=0, column=0, padx=2)
        tk.Label(legend_frame, text="正常 3.2-3.6V").grid(row=0, column=1, padx=(0, 10))
        
        tk.Label(legend_frame, bg="#FFC107", width=3, height=1).grid(row=0, column=2, padx=2)
        tk.Label(legend_frame, text="偏低 3.0-3.2V").grid(row=0, column=3, padx=(0, 10))
        
        tk.Label(legend_frame, bg="#F44336", width=3, height=1).grid(row=0, column=4, padx=2)
        tk.Label(legend_frame, text="异常 <3.0/>3.65V").grid(row=0, column=5)
        
        self.canvas = tk.Canvas(self, width=300, height=450, bg="#f0f0f0")
        self.canvas.pack(pady=10, padx=10)
        
        self._draw_cells()
        
    def _draw_cells(self):
        cols = 4
        rows = 4
        cell_width = 50
        cell_height = 60
        start_x = 40
        start_y = 30
        gap_x = 60
        gap_y = 70
        
        for i in range(self.num_cells):
            row = i // cols
            col = i % cols
            
            x1 = start_x + col * gap_x
            y1 = start_y + row * gap_y
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#4CAF50",
                outline="#333",
                width=2
            )
            
            label = self.canvas.create_text(
                (x1 + x2) // 2,
                (y1 + y2) // 2,
                text=f"Cell{i+1}\n3.300V",
                font=("Arial", 8),
                fill="#333"
            )
            
            self.cell_rects.append(rect)
            self.cell_labels.append(label)
            
            if col < cols - 1:
                mid_y = (y1 + y2) // 2
                self.canvas.create_line(x2, mid_y, x2 + 10, mid_y, fill="#666", width=2)
                
    def _get_voltage_color(self, voltage: float) -> str:
        if 3.2 <= voltage <= 3.6:
            return "#4CAF50"
        elif 3.0 <= voltage < 3.2:
            return "#FFC107"
        else:
            return "#F44336"
            
    def update_voltages(self, cell_voltages: List[float]):
        for i, voltage in enumerate(cell_voltages):
            if i < len(self.cell_rects):
                color = self._get_voltage_color(voltage)
                self.canvas.itemconfig(self.cell_rects[i], fill=color)
                self.canvas.itemconfig(
                    self.cell_labels[i],
                    text=f"Cell{i+1}\n{voltage:.3f}V"
                )
