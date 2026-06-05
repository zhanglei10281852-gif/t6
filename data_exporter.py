import csv
import os
from datetime import datetime
from typing import List, Dict
from tkinter import filedialog, messagebox

class DataExporter:
    def __init__(self):
        self.history: List[Dict] = []
        
    def add_record(self, timestamp: float, total_voltage: float, total_current: float,
                   cell_voltages: List[float], soc: float, temperatures: List[float] = None):
        record = {
            'timestamp': timestamp,
            'total_voltage': total_voltage,
            'total_current': total_current,
            'cell_voltages': cell_voltages.copy(),
            'soc': soc,
            'temperatures': temperatures.copy() if temperatures else []
        }
        self.history.append(record)
        
    def export_to_csv(self, parent=None) -> bool:
        if not self.history:
            messagebox.showwarning("警告", "没有数据可导出！")
            return False
            
        default_filename = f"bms_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            parent=parent,
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return False
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                headers = ['时间', '总电压(V)', '总电流(A)', 'SOC(%)']
                num_cells = len(self.history[0]['cell_voltages'])
                for i in range(num_cells):
                    headers.append(f'电芯{i+1}电压(V)')
                    
                num_temps = len(self.history[0].get('temperatures', []))
                for i in range(num_temps):
                    headers.append(f'温度{i+1}(℃)')
                    
                writer.writerow(headers)
                
                for record in self.history:
                    dt = datetime.fromtimestamp(record['timestamp'])
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    
                    row = [
                        time_str,
                        f"{record['total_voltage']:.3f}",
                        f"{record['total_current']:.2f}",
                        f"{record['soc']:.1f}"
                    ]
                    
                    for v in record['cell_voltages']:
                        row.append(f"{v:.3f}")
                        
                    for t in record.get('temperatures', []):
                        row.append(f"{t:.1f}")
                        
                    writer.writerow(row)
                    
            messagebox.showinfo("成功", f"数据已导出到:\n{file_path}\n共 {len(self.history)} 条记录")
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
            return False
            
    def clear_history(self):
        self.history.clear()
        
    def get_history_count(self) -> int:
        return len(self.history)
