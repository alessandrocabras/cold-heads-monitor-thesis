import csv
import ipaddress
import json
import socket
import sys
from datetime import datetime
from pathlib import Path

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtCore import QFile, QSize, QTextStream, QThread, Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QIntValidator, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from cold_heads_monitor import ColdHeadsMonitor
from plotter import Plotter


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "cold_heads_monitor_config.json"
SOCKET_TIMEOUT_SECONDS = 100
DEFAULT_CONFIG = {
    "ip_address": "192.168.150.94",
    "port": "1666",
}


class MainWindow(QMainWindow):
    STATUS_COLORS = {
        "Disconnected": "#76797c",
        "Connected": "#3daee9",
        "Acquiring": "#27ae60",
        "Error": "#e74c3c",
        "Normal": "#27ae60",
        "Maintenance": "#f39c12",
        "Compressor Down": "#e74c3c",
        "Unknown Anomaly": "#9b59b6",
    }

    CHANNEL_COLORS = ("#3daee9", "#fdbc4b", "#e74c3c")
    PLOT_BACKGROUND = "#1f2329"
    PLOT_PANEL = "#242a31"
    PLOT_TEXT = "#eff0f1"
    PLOT_GRID = "#56606b"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cold Heads Monitor")
        self.resize(1100, 760)

        self.config = self.loadConfig()
        self.coldHeadsMonitor = None
        self.thread = None
        self.plotter = None
        self.isMonitorConnected = False
        self.isAcquiring = False
        self.lastUpdate = None
        self.yLimits = None

        self.createBody()
        self.setConnectionState(False)
        self.setAcquisitionState(False)
        self.setApplicationStatus("Disconnected")

    def loadConfig(self):
        if not CONFIG_PATH.exists():
            return DEFAULT_CONFIG.copy()

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
        except (OSError, json.JSONDecodeError):
            return DEFAULT_CONFIG.copy()

        return {**DEFAULT_CONFIG, **config}

    def saveConfig(self):
        config = {
            "ip_address": self.ipValue.text().strip(),
            "port": self.portValue.text().strip(),
        }

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as config_file:
                json.dump(config, config_file, indent=2)
        except OSError as exc:
            self.showError(f"Unable to save configuration: {exc}")

    def createBody(self):
        rootLayout = QVBoxLayout()
        rootLayout.setContentsMargins(14, 14, 14, 14)
        rootLayout.setSpacing(12)

        topLayout = QHBoxLayout()
        topLayout.setSpacing(12)

        statusLayout = QVBoxLayout()
        statusLayout.setSpacing(10)

        statusTopRow = QHBoxLayout()
        statusTopRow.setSpacing(12)
        statusTopRow.addWidget(self.createConnectionBox(), 1)
        statusTopRow.addWidget(self.createHealthBox(), 1)

        statusLayout.addLayout(statusTopRow)
        statusLayout.addWidget(self.createInfoBox())

        topLayout.addLayout(statusLayout, 1)
        topLayout.addWidget(self.createHeader())

        rootLayout.addLayout(topLayout)
        rootLayout.addWidget(self.createPlotBox(), 1)

        widget = QWidget()
        widget.setLayout(rootLayout)
        self.setCentralWidget(widget)

    def createHeader(self):
        panel = QWidget()
        panel.setMinimumWidth(330)
        panel.setMaximumWidth(390)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 6, 0, 6)
        layout.setSpacing(8)

        self.logo = QLabel()
        pixmap = QPixmap(str(APP_DIR / "logo.png"))
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap.scaledToWidth(145, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.titleLabel = QLabel("Cold Heads Monitor")
        titleFont = QFont()
        titleFont.setPointSize(16)
        titleFont.setBold(True)
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setAlignment(Qt.AlignRight)

        self.applicationStatusValue = QLabel()
        self.applicationStatusValue.setMinimumWidth(210)
        self.applicationStatusValue.setMaximumWidth(265)
        self.applicationStatusValue.setAlignment(Qt.AlignCenter)

        self.lastUpdateValue = QLabel("Last update: ---")
        self.lastUpdateValue.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addStretch()
        layout.addWidget(self.logo, 0, Qt.AlignRight)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.applicationStatusValue, 0, Qt.AlignRight)
        layout.addWidget(self.lastUpdateValue)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def createConnectionBox(self):
        groupBox = QGroupBox("Connection")

        self.ipValue = QLineEdit()
        self.ipValue.setText(self.config["ip_address"])
        self.ipValue.setPlaceholderText("192.168.150.94")

        self.portValue = QLineEdit()
        self.portValue.setText(self.config["port"])
        self.portValue.setValidator(QIntValidator(1, 65535, self))
        self.portValue.setPlaceholderText("1666")

        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.connect)

        self.startButton = QPushButton("Start acquisition")
        self.startButton.clicked.connect(self.toggleAcquisition)

        formLayout = QFormLayout()
        formLayout.addRow("Arduino IP address", self.ipValue)
        formLayout.addRow("Arduino port", self.portValue)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.connectButton)
        buttonLayout.addWidget(self.startButton)

        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addLayout(buttonLayout)
        groupBox.setLayout(layout)

        return groupBox

    def createHealthBox(self):
        groupBox = QGroupBox("Health")

        self.healthStatusValue = QLabel("---")
        self.healthStatusValue.setAlignment(Qt.AlignCenter)
        self.healthStatusValue.setMinimumHeight(36)

        self.shift21Value = self.createValueLabel()
        self.shift31Value = self.createValueLabel()
        self.shift32Value = self.createValueLabel()

        formLayout = QFormLayout()
        formLayout.addRow("Health status", self.healthStatusValue)
        formLayout.addRow("CH1-CH2 shift", self.shift21Value)
        formLayout.addRow("CH1-CH3 shift", self.shift31Value)
        formLayout.addRow("CH2-CH3 shift", self.shift32Value)

        groupBox.setLayout(formLayout)
        return groupBox

    def createInfoBox(self):
        groupBox = QGroupBox("Live metrics")

        self.l1GainValue = self.createValueLabel("1/3x")
        self.l2GainValue = self.createValueLabel("2/3x")
        self.l3GainValue = self.createValueLabel("2/3x")
        self.l1AdcValue = self.createValueLabel()
        self.l2AdcValue = self.createValueLabel()
        self.l3AdcValue = self.createValueLabel()

        layout = QGridLayout()
        layout.setHorizontalSpacing(24)
        layout.addWidget(QLabel("CH 1 gain"), 0, 0)
        layout.addWidget(self.l1GainValue, 0, 1)
        layout.addWidget(QLabel("CH 1 Vpp / current"), 0, 2)
        layout.addWidget(self.l1AdcValue, 0, 3)

        layout.addWidget(QLabel("CH 2 gain"), 1, 0)
        layout.addWidget(self.l2GainValue, 1, 1)
        layout.addWidget(QLabel("CH 2 Vpp / current"), 1, 2)
        layout.addWidget(self.l2AdcValue, 1, 3)

        layout.addWidget(QLabel("CH 3 gain"), 2, 0)
        layout.addWidget(self.l3GainValue, 2, 1)
        layout.addWidget(QLabel("CH 3 Vpp / current"), 2, 2)
        layout.addWidget(self.l3AdcValue, 2, 3)

        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        groupBox.setLayout(layout)

        return groupBox

    def createPlotBox(self):
        self.plotGroupBox = QGroupBox("Waveform")

        self.figure = Figure(figsize=(8, 4), tight_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(390)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.navigationToolbar = NavigationToolbar(self.canvas, self)
        self.configureNavigationToolbar()

        self.channelChecks = []
        channelLayout = QHBoxLayout()
        channelLayout.setSpacing(10)
        channelLayout.setContentsMargins(0, 0, 0, 0)
        for channel in range(3):
            checkbox = QCheckBox(f"CH {channel + 1}")
            checkbox.setChecked(True)
            checkbox.setMinimumWidth(54)
            checkbox.stateChanged.connect(lambda _state: self.plotAdcValues())
            self.channelChecks.append(checkbox)
            channelLayout.addWidget(checkbox)

        self.smoothingMode = QComboBox()
        self.smoothingMode.addItems(["Raw", "Smoothed"])
        self.smoothingMode.setFixedWidth(106)
        self.smoothingMode.currentIndexChanged.connect(lambda _index: self.plotAdcValues())

        self.thresholdCheck = QCheckBox("Thresholds")
        self.thresholdCheck.stateChanged.connect(lambda _state: self.onThresholdModeChanged())

        thresholdValidator = QDoubleValidator(self)
        thresholdValidator.setNotation(QDoubleValidator.StandardNotation)

        self.lowerThresholdValue = QLineEdit()
        self.lowerThresholdValue.setPlaceholderText("Min")
        self.lowerThresholdValue.setValidator(thresholdValidator)
        self.lowerThresholdValue.setFixedWidth(78)
        self.lowerThresholdValue.textChanged.connect(lambda _text: self.plotAdcValues())

        self.upperThresholdValue = QLineEdit()
        self.upperThresholdValue.setPlaceholderText("Max")
        self.upperThresholdValue.setValidator(thresholdValidator)
        self.upperThresholdValue.setFixedWidth(78)
        self.upperThresholdValue.textChanged.connect(lambda _text: self.plotAdcValues())
        self.lowerThresholdValue.setEnabled(False)
        self.upperThresholdValue.setEnabled(False)

        self.savePlotButton = QPushButton("Save snapshot")
        self.savePlotButton.setMinimumWidth(104)
        self.savePlotButton.clicked.connect(self.saveSnapshot)

        self.channelStatsLabels = []
        statsLayout = QHBoxLayout()
        statsLayout.setSpacing(8)
        statsLayout.setContentsMargins(0, 0, 0, 0)
        for channel in range(3):
            label = self.createValueLabel(f"CH {channel + 1}: ---")
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumHeight(28)
            label.setMaximumHeight(34)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            statsFont = QFont("Consolas")
            statsFont.setStyleHint(QFont.Monospace)
            statsFont.setPointSize(10)
            statsFont.setBold(True)
            label.setFont(statsFont)
            label.setStyleSheet(
                f"color: {self.CHANNEL_COLORS[channel]};"
                "background-color: #242a31;"
                "border: 1px solid #56606b;"
                "border-radius: 4px;"
                "padding: 2px 8px;"
            )
            self.channelStatsLabels.append(label)
            statsLayout.addWidget(label)

        self.lines = []
        self.thresholdLines = []
        self.plotStatusLabel = None
        self.legend = None
        self.configurePlot()

        plotControlsLayout = QHBoxLayout()
        plotControlsLayout.setSpacing(10)
        plotControlsLayout.setContentsMargins(0, 0, 0, 0)
        plotControlsLayout.addLayout(channelLayout)
        plotControlsLayout.addSpacing(16)
        plotControlsLayout.addWidget(QLabel("Mode"))
        plotControlsLayout.addWidget(self.smoothingMode)
        plotControlsLayout.addSpacing(16)
        plotControlsLayout.addWidget(self.thresholdCheck)
        plotControlsLayout.addWidget(self.lowerThresholdValue)
        plotControlsLayout.addWidget(self.upperThresholdValue)
        plotControlsLayout.addStretch()

        topBarLayout = QHBoxLayout()
        topBarLayout.setSpacing(8)
        topBarLayout.setContentsMargins(0, 0, 0, 0)
        topBarLayout.addWidget(self.navigationToolbar)
        topBarLayout.addStretch()
        topBarLayout.addWidget(self.savePlotButton)

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 12, 10, 8)
        layout.addLayout(topBarLayout)
        layout.addLayout(plotControlsLayout)
        layout.addWidget(self.canvas, 1)
        layout.addLayout(statsLayout)
        self.plotGroupBox.setLayout(layout)

        return self.plotGroupBox

    def configureNavigationToolbar(self):
        usefulActions = {"Home", "Back", "Forward", "Pan", "Zoom", "Save"}

        for action in list(self.navigationToolbar.actions()):
            text = action.text().replace("&", "").strip()
            tooltip = action.toolTip().replace("&", "").strip()
            if action.isSeparator():
                continue
            if text not in usefulActions and tooltip not in usefulActions:
                self.navigationToolbar.removeAction(action)

        self.navigationToolbar.setMovable(False)
        self.navigationToolbar.setIconSize(QSize(20, 20))
        self.navigationToolbar.setMinimumWidth(320)
        self.navigationToolbar.setMaximumWidth(350)
        self.navigationToolbar.setMinimumHeight(40)
        self.navigationToolbar.setMaximumHeight(44)
        self.navigationToolbar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.navigationToolbar.setStyleSheet(
            """
            QToolBar {
                background-color: #5f6872;
                border: 1px solid #76797c;
                border-radius: 4px;
                spacing: 2px;
                padding: 4px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                min-width: 28px;
                min-height: 28px;
                padding: 2px;
            }
            QToolButton:hover {
                background-color: #727b84;
            }
            QToolButton:pressed {
                background-color: #454d55;
            }
            QToolBar::separator {
                background-color: #3f464e;
                width: 1px;
                margin: 4px 4px;
            }
            """
        )

    def createValueLabel(self, text="---"):
        label = QLabel(text)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setMinimumWidth(120)

        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        label.setFont(font)

        return label

    def configurePlot(self):
        self.figure.patch.set_facecolor(self.PLOT_BACKGROUND)
        self.ax.set_facecolor(self.PLOT_PANEL)
        self.ax.set_title("")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("ADC value")
        self.ax.grid(True, color=self.PLOT_GRID, alpha=0.18, linewidth=0.7)

        self.ax.title.set_color(self.PLOT_TEXT)
        self.ax.xaxis.label.set_color(self.PLOT_TEXT)
        self.ax.yaxis.label.set_color(self.PLOT_TEXT)
        self.ax.tick_params(colors=self.PLOT_TEXT)

        for spine in self.ax.spines.values():
            spine.set_color("#76797c")

        self.lines = []
        for channel, color in enumerate(self.CHANNEL_COLORS):
            line, = self.ax.plot(
                [],
                [],
                label=f"CH {channel + 1}",
                color=color,
                linewidth=1.9,
                alpha=0.95,
                solid_capstyle="round",
                zorder=3,
            )
            self.lines.append(line)

        self.thresholdLines = [
            self.ax.axhline(0, color="#c9d1d9", linestyle="--", linewidth=1.0, alpha=0.45, visible=False),
            self.ax.axhline(0, color="#c9d1d9", linestyle="--", linewidth=1.0, alpha=0.45, visible=False),
        ]
        self.plotStatusLabel = self.ax.text(
            0.985,
            0.965,
            "No data",
            transform=self.ax.transAxes,
            ha="right",
            va="top",
            color="#eff0f1",
            fontsize=9,
            bbox={"facecolor": "#76797c", "edgecolor": "#76797c", "alpha": 0.95, "pad": 4},
        )

        self.updateLegend()
        self.canvas.draw_idle()

    def onThresholdModeChanged(self):
        enabled = self.thresholdCheck.isChecked()
        self.lowerThresholdValue.setEnabled(enabled)
        self.upperThresholdValue.setEnabled(enabled)
        self.plotAdcValues()

    def validateConnectionInputs(self):
        ip_address = self.ipValue.text().strip()
        port_text = self.portValue.text().strip()

        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            self.showError("Invalid IP address.")
            return None

        if not port_text:
            self.showError("Invalid Arduino port.")
            return None

        port = int(port_text)
        if not 1 <= port <= 65535:
            self.showError("Arduino port must be between 1 and 65535.")
            return None

        return ip_address, port

    def connect(self):
        if self.isMonitorConnected:
            self.disconnectMonitor()
            return

        connectionData = self.validateConnectionInputs()
        if connectionData is None:
            return

        ipAddress, port = connectionData

        try:
            self.coldHeadsMonitor = ColdHeadsMonitor()
            self.coldHeadsMonitor.settimeout(SOCKET_TIMEOUT_SECONDS)
            self.coldHeadsMonitor.connect((ipAddress, port))
        except socket.error as exc:
            self.coldHeadsMonitor = None
            self.setApplicationStatus("Error")
            self.showError(f"Socket error: {exc}")
            return

        self.saveConfig()
        self.setConnectionState(True)
        self.setApplicationStatus("Connected")
        self.updateGainValues()

    def disconnectMonitor(self):
        self.stopAcquisition()

        if self.coldHeadsMonitor is not None:
            try:
                self.coldHeadsMonitor.close()
            except socket.error:
                pass

        self.coldHeadsMonitor = None
        self.setConnectionState(False)
        self.setAcquisitionState(False)
        self.setApplicationStatus("Disconnected")
        self.resetLiveValues()

    def toggleAcquisition(self):
        if self.isAcquiring:
            self.stopAcquisition()
        else:
            self.startAcquisition()

    def startAcquisition(self):
        if not self.isMonitorConnected or self.coldHeadsMonitor is None:
            self.showError("Connect to the Arduino before starting acquisition.")
            return

        if self.thread is not None and self.thread.isRunning():
            return

        self.thread = QThread()
        self.plotter = Plotter(self.coldHeadsMonitor)
        self.plotter.moveToThread(self.thread)

        self.thread.started.connect(self.plotter.run)
        self.plotter.progress.connect(self.updateLiveData)
        self.plotter.error.connect(self.handleAcquisitionError)
        self.plotter.finished.connect(self.thread.quit)
        self.plotter.finished.connect(self.plotter.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.handleAcquisitionFinished)

        self.setAcquisitionState(True)
        self.setApplicationStatus("Acquiring")
        self.thread.start()

    def stopAcquisition(self):
        if self.plotter is not None:
            self.plotter.stop()

        if self.isAcquiring:
            self.startButton.setText("Stopping...")
            self.startButton.setEnabled(False)

    def handleAcquisitionFinished(self):
        self.thread = None
        self.plotter = None
        self.setAcquisitionState(False)

        if self.isMonitorConnected:
            self.setApplicationStatus("Connected")

    def handleAcquisitionError(self, message):
        self.setApplicationStatus("Error")
        self.showError(f"Acquisition error: {message}")

    def setConnectionState(self, connected):
        self.isMonitorConnected = connected
        self.connectButton.setText("Disconnect" if connected else "Connect")
        self.connectButton.setStyleSheet(
            "background-color: #27ae60;" if connected else "background-color: #8e2727;"
        )
        self.ipValue.setEnabled(not connected)
        self.portValue.setEnabled(not connected)
        self.startButton.setEnabled(connected)
        self.savePlotButton.setEnabled(connected)

    def setAcquisitionState(self, acquiring):
        self.isAcquiring = acquiring
        self.startButton.setText("Stop acquisition" if acquiring else "Start acquisition")
        self.startButton.setEnabled(self.isMonitorConnected)
        self.updatePlotStatus(self.hasVisiblePlotData())

    def setApplicationStatus(self, status):
        color = self.STATUS_COLORS.get(status, "#76797c")
        self.applicationStatusValue.setText(status)
        self.applicationStatusValue.setStyleSheet(
            f"background-color: {color}; color: white; padding: 6px 12px; border-radius: 4px;"
        )

    def setHealthStatus(self, healthStatus):
        text = healthStatus or "---"
        color = self.STATUS_COLORS.get(text, "#76797c")
        self.healthStatusValue.setText(text)
        self.healthStatusValue.setStyleSheet(
            f"background-color: {color}; color: white; padding: 6px 12px; border-radius: 4px;"
        )

    def updateGainValues(self):
        if self.coldHeadsMonitor is None:
            return

        self.l1GainValue.setText(str(self.coldHeadsMonitor.adcGains[0]))
        self.l2GainValue.setText(str(self.coldHeadsMonitor.adcGains[1]))
        self.l3GainValue.setText(str(self.coldHeadsMonitor.adcGains[2]))

    def updateLiveData(self):
        self.updatePpValues()
        self.updateShiftValues()
        self.updateHealthStatus()
        self.plotAdcValues()
        self.updateLastUpdate()

    def updateShiftValues(self):
        self.shift21Value.setText(self.formatValue(self.coldHeadsMonitor.shiftValues[0]))
        self.shift31Value.setText(self.formatValue(self.coldHeadsMonitor.shiftValues[1]))
        self.shift32Value.setText(self.formatValue(self.coldHeadsMonitor.shiftValues[2]))

    def updatePpValues(self):
        self.l1AdcValue.setText(self.formatValue(self.coldHeadsMonitor.adcPpValues[0]))
        self.l2AdcValue.setText(self.formatValue(self.coldHeadsMonitor.adcPpValues[1]))
        self.l3AdcValue.setText(self.formatValue(self.coldHeadsMonitor.adcPpValues[2]))

    def updateHealthStatus(self):
        self.setHealthStatus(self.coldHeadsMonitor.healthStatus)

    def updateLastUpdate(self):
        self.lastUpdate = datetime.now()
        self.lastUpdateValue.setText(f"Last update: {self.lastUpdate:%Y-%m-%d %H:%M:%S}")

    def plotAdcValues(self):
        if self.coldHeadsMonitor is None:
            self.updatePlotStatus(False)
            return

        hasVisibleData = False
        visibleData = []
        for channel, line in enumerate(self.lines):
            data = self.preparePlotData(self.coldHeadsMonitor.adcValues[channel])
            isVisible = self.channelChecks[channel].isChecked()
            line.set_visible(isVisible)

            if data is not None and isVisible:
                line.set_data(range(len(data)), data)
                hasVisibleData = True
                visibleData.extend(data)
            else:
                line.set_data([], [])

        self.updateThresholdLines()
        self.updateChannelStats()
        self.updatePlotStatus(hasVisibleData)

        if hasVisibleData:
            self.applyStableYAxis(visibleData)
            self.ax.set_xlim(0, max(len(line.get_xdata()) for line in self.lines) - 1)

        self.updateLegend()
        self.canvas.draw_idle()

    def preparePlotData(self, data):
        if data is None:
            return None

        values = [float(value) for value in data]
        if self.smoothingMode.currentText() != "Smoothed" or len(values) < 7:
            return values

        windowSize = 7
        halfWindow = windowSize // 2
        smoothed = []
        for index in range(len(values)):
            start = max(0, index - halfWindow)
            end = min(len(values), index + halfWindow + 1)
            smoothed.append(sum(values[start:end]) / (end - start))

        return smoothed

    def applyStableYAxis(self, visibleData):
        if not visibleData:
            return

        lower = min(visibleData)
        upper = max(visibleData)

        thresholds = self.getThresholdValues()
        if thresholds[0] is not None:
            lower = min(lower, thresholds[0])
        if thresholds[1] is not None:
            upper = max(upper, thresholds[1])

        span = upper - lower
        if span == 0:
            span = max(abs(upper), 1.0)

        margin = span * 0.12
        targetLimits = (lower - margin, upper + margin)

        if self.yLimits is None:
            self.yLimits = targetLimits
        else:
            currentLower, currentUpper = self.yLimits
            targetLower, targetUpper = targetLimits
            # Expand immediately, contract gently so the graph does not jump at every frame.
            nextLower = targetLower if targetLower < currentLower else currentLower * 0.85 + targetLower * 0.15
            nextUpper = targetUpper if targetUpper > currentUpper else currentUpper * 0.85 + targetUpper * 0.15
            self.yLimits = (nextLower, nextUpper)

        self.ax.set_ylim(*self.yLimits)

    def updateLegend(self):
        if self.legend is not None:
            self.legend.remove()
            self.legend = None

        visibleLines = [line for line in self.lines if line.get_visible()]
        if not visibleLines:
            return

        self.legend = self.ax.legend(
            handles=visibleLines,
            loc="upper center",
            bbox_to_anchor=(0.5, 1.02),
            ncol=len(visibleLines),
            frameon=True,
            facecolor=self.PLOT_BACKGROUND,
            edgecolor="#56606b",
            framealpha=0.85,
        )

        for text in self.legend.get_texts():
            text.set_color(self.PLOT_TEXT)

    def updatePlotStatus(self, hasVisibleData):
        if self.plotStatusLabel is None:
            return

        if not hasVisibleData:
            text = "No data"
        elif self.isAcquiring:
            text = "Live"
        else:
            text = "Paused"

        badgeColor = {
            "Live": "#27ae60",
            "Paused": "#f39c12",
            "No data": "#76797c",
        }[text]

        self.plotStatusLabel.set_text(text)
        self.plotStatusLabel.set_bbox(
            {"facecolor": badgeColor, "edgecolor": badgeColor, "alpha": 0.95, "pad": 4}
        )

    def getThresholdValues(self):
        if not self.thresholdCheck.isChecked():
            return None, None

        return self.parseFloat(self.lowerThresholdValue.text()), self.parseFloat(self.upperThresholdValue.text())

    def updateThresholdLines(self):
        lower, upper = self.getThresholdValues()
        for line, value in zip(self.thresholdLines, (lower, upper)):
            if value is None:
                line.set_visible(False)
            else:
                line.set_ydata([value, value])
                line.set_visible(True)

    def updateChannelStats(self):
        if self.coldHeadsMonitor is None:
            return

        for channel, label in enumerate(self.channelStatsLabels):
            data = self.preparePlotData(self.coldHeadsMonitor.adcValues[channel])
            if not data:
                label.setText(f"CH {channel + 1}: ---")
                continue

            minimum = min(data)
            maximum = max(data)
            mean = sum(data) / len(data)
            vpp = maximum - minimum
            label.setText(f"CH {channel + 1}: min {minimum:.3f} | max {maximum:.3f} | mean {mean:.3f} | Vpp {vpp:.3f}")

    def parseFloat(self, value):
        value = value.strip()
        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    def saveSnapshot(self):
        if self.coldHeadsMonitor is None:
            self.showError("No acquisition data available to export.")
            return

        values = self.coldHeadsMonitor.adcValues
        hasSnapshotData = any(channelValues is not None and len(channelValues) > 0 for channelValues in values)
        if not hasSnapshotData:
            self.showError("No acquisition data available to export.")
            return

        defaultName = f"cold_heads_snapshot_{datetime.now():%Y%m%d_%H%M%S}.csv"
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save snapshot",
            str(APP_DIR / defaultName),
            "CSV files (*.csv)",
        )

        if not filePath:
            return

        maxLength = max(len(channelValues) if channelValues is not None else 0 for channelValues in values)

        try:
            with open(filePath, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["sample", "ch1", "ch2", "ch3"])
                for sampleIndex in range(maxLength):
                    row = [sampleIndex]
                    for channelValues in values:
                        row.append(channelValues[sampleIndex] if channelValues and sampleIndex < len(channelValues) else "")
                    writer.writerow(row)
        except OSError as exc:
            self.showError(f"Unable to save snapshot: {exc}")

    def resetLiveValues(self):
        for label in (
            self.shift21Value,
            self.shift31Value,
            self.shift32Value,
            self.l1AdcValue,
            self.l2AdcValue,
            self.l3AdcValue,
        ):
            label.setText("---")

        self.setHealthStatus("---")
        self.lastUpdateValue.setText("Last update: ---")
        self.yLimits = None

        for line in self.lines:
            line.set_data([], [])

        for label, channel in zip(self.channelStatsLabels, range(3)):
            label.setText(f"CH {channel + 1}: ---")

        self.updateThresholdLines()
        self.updatePlotStatus(False)
        self.canvas.draw_idle()

    def hasVisiblePlotData(self):
        if self.coldHeadsMonitor is None:
            return False

        for channel, checkbox in enumerate(self.channelChecks):
            data = self.coldHeadsMonitor.adcValues[channel]
            if checkbox.isChecked() and data is not None and len(data) > 0:
                return True

        return False

    def formatValue(self, value):
        if value is None or value == "":
            return "---"

        if isinstance(value, float):
            return f"{value:.3f}"

        return str(value)

    def showError(self, message):
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        self.disconnectMonitor()
        super().closeEvent(event)


def applyStylesheet(app):
    stylesheetPath = APP_DIR / "dark" / "stylesheet.qss"
    if not stylesheetPath.exists():
        return

    file = QFile(str(stylesheetPath))
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        darkAssetsPath = (APP_DIR / "dark").as_posix()
        stylesheet = stylesheet.replace("url(:/dark/", f"url({darkAssetsPath}/")
        app.setStyleSheet(stylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    applyStylesheet(app)

    window = MainWindow()
    window.show()
    app.exec_()
