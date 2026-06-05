import time
from dataclasses import dataclass
from typing import List

@dataclass
class SOCState:
    soc: float
    ah_integrated: float
    last_update: float

class SOCEstimator:
    def __init__(self, nominal_capacity: float = 100.0, initial_soc: float = 50.0):
        self.nominal_capacity = nominal_capacity
        self.initial_soc = initial_soc
        self.current_soc = initial_soc
        self.charge_efficiency = 0.98
        self.discharge_efficiency = 1.0
        self.full_voltage = 3.65
        self.empty_voltage = 2.8
        self.cell_full_threshold = 3.60
        self.cell_empty_threshold = 3.0
        self._last_time = None
        self._ah_charge = 0.0
        self._ah_discharge = 0.0

    def reset(self, initial_soc: float = None):
        if initial_soc is not None:
            self.current_soc = initial_soc
        else:
            self.current_soc = self.initial_soc
        self._last_time = None
        self._ah_charge = 0.0
        self._ah_discharge = 0.0

    def _check_calibration(self, cell_voltages: List[float]) -> bool:
        max_voltage = max(cell_voltages)
        min_voltage = min(cell_voltages)
        
        if max_voltage >= self.cell_full_threshold:
            self.current_soc = 100.0
            return True
            
        if min_voltage <= self.cell_empty_threshold:
            self.current_soc = 0.0
            return True
            
        return False

    def update(self, current: float, cell_voltages: List[float], current_time: float = None) -> float:
        if current_time is None:
            current_time = time.time()
            
        if self._check_calibration(cell_voltages):
            self._last_time = current_time
            return self.current_soc
            
        if self._last_time is None:
            self._last_time = current_time
            return self.current_soc
            
        dt_hours = (current_time - self._last_time) / 3600.0
        self._last_time = current_time
        
        ah_change = current * dt_hours
        
        if ah_change > 0:
            effective_ah = ah_change * self.charge_efficiency
            self._ah_charge += effective_ah
        else:
            effective_ah = ah_change * self.discharge_efficiency
            self._ah_discharge += abs(effective_ah)
            
        soc_change = (effective_ah / self.nominal_capacity) * 100.0
        self.current_soc += soc_change
        
        self.current_soc = max(0.0, min(100.0, self.current_soc))
        
        return self.current_soc

    def get_soc(self) -> float:
        return self.current_soc

    def get_ah_charge(self) -> float:
        return self._ah_charge

    def get_ah_discharge(self) -> float:
        return self._ah_discharge
