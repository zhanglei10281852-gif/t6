import time
from dataclasses import dataclass, field
from typing import List, Callable, Dict

@dataclass
class Alarm:
    id: str
    message: str
    level: str
    timestamp: float
    active: bool = True

@dataclass
class AlarmConfig:
    over_voltage_threshold: float = 3.65
    under_voltage_threshold: float = 3.0
    voltage_diff_threshold: float = 0.2
    over_temp_threshold: float = 45.0
    over_current_threshold: float = 30.0

class AlarmManager:
    def __init__(self, config: AlarmConfig = None):
        self.config = config or AlarmConfig()
        self._alarms: List[Alarm] = []
        self._active_alarms: Dict[str, Alarm] = {}
        self._callbacks: List[Callable[[List[Alarm], int], None]] = []
        self.alarm_count = 0

    def add_callback(self, callback: Callable[[List[Alarm], int], None]):
        self._callbacks.append(callback)

    def _add_alarm(self, alarm_id: str, message: str, level: str):
        if alarm_id not in self._active_alarms:
            alarm = Alarm(
                id=alarm_id,
                message=message,
                level=level,
                timestamp=time.time()
            )
            self._active_alarms[alarm_id] = alarm
            self._alarms.append(alarm)
            self.alarm_count += 1
            self._notify_callbacks()
            return True
        return False

    def _clear_alarm(self, alarm_id: str):
        if alarm_id in self._active_alarms:
            self._active_alarms[alarm_id].active = False
            del self._active_alarms[alarm_id]
            self._notify_callbacks()
            return True
        return False

    def _notify_callbacks(self):
        active_list = list(self._active_alarms.values())
        for callback in self._callbacks:
            callback(active_list, self.alarm_count)

    def check_alarms(self, cell_voltages: List[float], temperatures: List[float], current: float):
        max_voltage = max(cell_voltages)
        min_voltage = min(cell_voltages)
        max_temp = max(temperatures)
        voltage_diff = max_voltage - min_voltage

        for i, v in enumerate(cell_voltages):
            alarm_id = f"over_v_cell_{i}"
            if v > self.config.over_voltage_threshold:
                self._add_alarm(alarm_id, f"电芯{i+1}电压过高: {v:.3f}V", "error")
            else:
                self._clear_alarm(alarm_id)

        for i, v in enumerate(cell_voltages):
            alarm_id = f"under_v_cell_{i}"
            if v < self.config.under_voltage_threshold:
                self._add_alarm(alarm_id, f"电芯{i+1}电压过低: {v:.3f}V", "error")
            else:
                self._clear_alarm(alarm_id)

        if voltage_diff > self.config.voltage_diff_threshold:
            self._add_alarm("voltage_diff", f"电芯压差过大: {voltage_diff:.3f}V", "warning")
        else:
            self._clear_alarm("voltage_diff")

        if max_temp > self.config.over_temp_threshold:
            self._add_alarm("over_temp", f"温度过高: {max_temp:.1f}℃", "error")
        else:
            self._clear_alarm("over_temp")

        if abs(current) > self.config.over_current_threshold:
            self._add_alarm("over_current", f"电流过大: {current:.1f}A", "warning")
        else:
            self._clear_alarm("over_current")

    def get_active_alarms(self) -> List[Alarm]:
        return list(self._active_alarms.values())

    def get_alarm_count(self) -> int:
        return self.alarm_count

    def clear_all_alarms(self):
        for alarm_id in list(self._active_alarms.keys()):
            self._active_alarms[alarm_id].active = False
        self._active_alarms.clear()
        self._notify_callbacks()
