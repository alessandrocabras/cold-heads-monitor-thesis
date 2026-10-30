from pathlib import Path

from PyQt5.QtCore import pyqtSignal, QObject
from cold_heads_monitor import *
import cold_head_status_model
import joblib
import numpy as np

HEALTH_MODEL_CHANNEL_INDEX = 1


class Plotter(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self,coldHeadsMonitor):
        super().__init__()
        self.coldHeadsMonitor = coldHeadsMonitor
        self.running = False

        model_dir = Path(__file__).resolve().parent
        model_candidates = [
            model_dir / 'cold_head_status_model.pkl',
            model_dir / 'random_forest_model_candidate.pkl',
            model_dir / 'random_forest_model.pkl',
        ]
        model_path = next((path for path in model_candidates if path.exists()), None)
        if model_path is None:
            raise FileNotFoundError(
                'No health model found. Expected one of: '
                + ', '.join(path.name for path in model_candidates)
            )

        with open(model_path, 'rb') as model_file:
            self.loaded_model = joblib.load(model_file)

    def getHealthStatus(self,adc_values):
        elem = np.asarray(adc_values[HEALTH_MODEL_CHANNEL_INDEX]).reshape(1, -1)
        y_pred = int(self.loaded_model.predict(elem)[0])

        if y_pred == 2:
            return 'Compressor Down'
        elif y_pred == 3:
            return 'Unknown Anomaly'
        elif y_pred == 0:
            return 'Maintenance'

        return 'Normal'

    def stop(self):
        self.running = False

    def run(self):
        self.running = True

        try:
            while self.running:
                rx = self.coldHeadsMonitor.acquire()
                if not self.running:
                    break

                if rx and rx == 'OK':
                    for adc_ch in range(3):
                        adc_values = self.coldHeadsMonitor.getadc(adc_ch)
                        self.coldHeadsMonitor.adcValues[adc_ch] = adc_values
                        self.coldHeadsMonitor.adcPpValues[adc_ch] = self.coldHeadsMonitor.calculatePpValue(adc_ch, adc_values)

                    shift_codes = [21, 31, 32]
                    for i, shift_code in enumerate(shift_codes):
                        self.coldHeadsMonitor.shiftValues[i] = self.coldHeadsMonitor.getshift(shift_code)

                    self.coldHeadsMonitor.healthStatus = self.getHealthStatus(self.coldHeadsMonitor.adcValues)
                    self.progress.emit()
        except Exception as exc:
            if self.running:
                self.error.emit(str(exc))
        finally:
            self.running = False
            self.finished.emit()
