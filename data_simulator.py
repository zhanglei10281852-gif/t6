import time
import random
import threading
from dataclasses import dataclass, field
from typing import List, Callable

@dataclass
class BatteryData:
    timestamp: float = 0.0
    total_voltage: float = 0.0
    total_current: float = 0.0
    cell_voltages: List[float] = field(default_factory=lambda: [3.3] * 16)
    temperatures: List[float] = field(default_factory=lambda: [25.0] * 4)
    soc: float = 50.0
    mode: str = "rest"

class BatterySimulator:
    def __init__(self, num_cells: int = 16):
        self.num_cells = num_cells
        self.cell_capacities = [100.0 * random.uniform(0.95, 1.05) for _ in range(num_cells)]
        self.cell_voltages = [3.3 + random.uniform(-0.05, 0.05) for _ in range(num_cells)]
        self.base_voltage = 3.3
        self.current = 0.0
        self.mode = "rest"
        self.charge_current = 20.0
        self.discharge_current = -15.0
        self.cv_voltage = 3.65
        self.cutoff_voltage = 2.8
        self.temperatures = [25.0 + random.uniform(-2, 2) for _ in range(4)]
        self._callbacks = []
        self._running = False
        self._thread = None
        self.interval = 0.5

    def add_callback(self, callback: Callable[[BatteryData], None]):
        self._callbacks.append(callback)

    def set_mode(self, mode: str):
        self.mode = mode
        if mode == "charge":
            self.current = self.charge_current
        elif mode == "discharge":
            self.current = self.discharge_current
        else:
            self.current = 0.0

    def _update_voltages(self, dt: float):
        ah_change = (self.current / 3600.0) * dt
        for i in range(self.num_cells):
            capacity_ratio = 100.0 / self.cell_capacities[i]
            
            if self.mode == "charge":
                if self.cell_voltages[i] < self.cv_voltage:
                    dv = ah_change * 0.05 * capacity_ratio
                    self.cell_voltages[i] += dv
                else:
                    taper_factor = max(0.1, 1 - (self.cell_voltages[i] - self.cv_voltage) * 10)
                    dv = ah_change * 0.01 * taper_factor * capacity_ratio
                    self.cell_voltages[i] = min(self.cv_voltage + 0.02, self.cell_voltages[i] + dv)
                    
            elif self.mode == "discharge":
                dv = ah_change * 0.06 * capacity_ratio
                self.cell_voltages[i] += dv
                self.cell_voltages[i] = max(self.cutoff_voltage, self.cell_voltages[i])
                
            else:
                self.cell_voltages[i] += random.uniform(-0.002, 0.002)
                self.cell_voltages[i] = max(2.8, min(3.8, self.cell_voltages[i]))

    def _update_temperatures(self, dt: float):
        base_temp = 25.0
        load_factor = abs(self.current) / 20.0
        target_temp = base_temp + load_factor * 15.0 + random.uniform(-1, 1)
        
        for i in range(len(self.temperatures)):
            self.temperatures[i] += (target_temp - self.temperatures[i]) * 0.05
            self.temperatures[i] += random.uniform(-0.2, 0.2)

    def _generate_data(self) -> BatteryData:
        total_voltage = sum(self.cell_voltages)
        return BatteryData(
            timestamp=time.time(),
            total_voltage=total_voltage,
            total_current=self.current,
            cell_voltages=self.cell_voltages.copy(),
            temperatures=self.temperatures.copy(),
            mode=self.mode
        )

    def _run(self):
        last_time = time.time()
        while self._running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            self._update_voltages(dt)
            self._update_temperatures(dt)
            data = self._generate_data()
            
            for callback in self._callbacks:
                callback(data)
                
            time.sleep(self.interval)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
