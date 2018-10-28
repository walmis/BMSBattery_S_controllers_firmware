from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Converter:
    def from_raw(self, x):
        return x


class ADCValue(Converter):
    @staticmethod
    def from_raw(x):
        return x*(5.0/255)

    @staticmethod
    def from_raw_str(x):
        x = ADCValue.from_raw(x)
        return "%.2f" % x

class Time64us(Converter):
    @staticmethod
    def from_raw(x):
        return (x*64.0)/1000

    @staticmethod
    def from_raw_str( x): # return ms
        x = Time64us.from_raw(x)
        return "%.1f" % x

class CurrentConv(Converter):
    @staticmethod
    def from_raw(x): return (x/10.0)
    @staticmethod
    def from_raw_str( x): # return ms
        x = CurrentConv.from_raw(x)
        return "%.1f" % x

class DegreeConv(Converter):
    @staticmethod
    def from_raw(x): return (x*(360/255.0))
    @staticmethod
    def from_raw_str( x): # return ms
        x = DegreeConv.from_raw(x)
        return "%.1f" % x

class Param:
    def __init__(self, id, desc, default_val, unit=None, convert=None, doc="", min=0, max=255, bold=False):
        self.id = id
        self.desc = desc
        self.default_val = default_val
        self.unit = unit
        self.converter = convert

        self.label = QLabel(self.desc)
        if bold:
            self.label.setStyleSheet("font-weight: bold;")

        if type(default_val) == int:
            self.control = QSpinBox()
            self.control.setMinimum(min)
            self.control.setMaximum(max)
            self.control.setValue(default_val)
            self.control.valueChanged[int].connect(lambda v: self.onValueChanged(v))

        elif type(default_val) == float:
            self.control = QDoubleSpinBox()
            self.control.setMinimum(min)
            self.control.setMaximum(max)
            self.control.setValue(default_val)
            self.control.valueChanged.connect(self.onValueChanged)
        else:
            self.control = QLineEdit()

        self.lbl_conv_value = None
        if unit is not None:
            w= QWidget()
            h = QHBoxLayout()
            h.setContentsMargins(0,0,0,0)
            h.addWidget(self.control)
            if self.converter:
                self.lbl_conv_value = QLabel(str(convert.from_raw_str(default_val)))
                h.addWidget(self.lbl_conv_value)
            h.addWidget(QLabel(self.unit))
            w.setLayout(h)
            self.control = w
    def test(self, v):
        print(v)
    #@pyqtSlot(int)
    def onValueChanged(self, value):
        #print("ch", value)
        if self.converter:
            self.lbl_conv_value.setText(self.converter.from_raw_str(value))




QApplication.setStyle("Fusion")
class App(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)

        params = [
            [
                Param("NUMBER_OF_PAS_MAGS", "No. of PAS Magnets", 12, "", bold=True,
                      doc="Number of magnets in the PAS disk. Required for correct calculation of the cadence"),
                Param("wheel_circumference", "Wheel Circumference", 2230, "mm", max=65535, bold=True,
                      doc="Wheel circumference in millimetres, is required to calculate the speed. The setting in the display is ignored."),
                Param("timeout", "PAS Timeout", 3125, "ms", bold=True, convert=Time64us, max=65535,
                      doc="Time to stop motor after stopping pedalling. Value in 64µs for Motor Speed = Normal, 48µs for Motor Speed = High. Calculation example: 3125*0,000064s = 0,2s"),
                Param("ADC_THROTTLE_MIN_VALUE", "Throttle Min", 43, unit="V", convert=ADCValue),
                Param("ADC_THROTTLE_MAX_VALUE", "Throttle Max", 182, unit="V", convert=ADCValue),
                Param("timeout", "Battery Current Max", 150, unit="A", convert=CurrentConv),
                Param("timeout", "Phase Current Max", 300, unit="A", convert=CurrentConv, bold=True, max=1000),
                Param("timeout", "Regen Current Max", 50, unit="A", convert=CurrentConv),
                Param("timeout", "Undervoltage Limit", 148, "V", bold=True),
                Param("timeout", "Serial Cells", 13, "cells", max=20, bold=True),
                Param("timeout", "Battery Current Cal A", 46, ""),
                Param("timeout", "Temperature Cal A", 1.6, "", max=65535, bold=True),
                Param("timeout", "Temperature Cal B", -110.4, "", min=-32767, max=32768, bold=True),

                Param("timeout", "Gain P", 0.5, ""),
                Param("timeout", "Gain I", 0.2, ""),
                Param("timeout", "Gear Ratio", 24, "", bold=True),
                Param("timeout", "Battery Voltage Cal", 68, ""),
                Param("timeout", "PAS Threshold", 1.9, ""),
            ],
            [
                Param("timeout", "Assist Level 1", 12, "%", bold=True),
                Param("timeout", "Assist Level 2", 21, "%", bold=True),
                Param("timeout", "Assist Level 3", 30, "%", bold=True),
                Param("timeout", "Assist Level 4", 59, "%", bold=True),
                Param("timeout", "Assist Level 5", 100, "%", bold=True),

                Param("timeout", "Morse Time 1", 50, "", bold=True),
                Param("timeout", "Morse Time 2", 50, "", bold=True),
                Param("timeout", "Morse Time 3", 50, "", bold=True),
                10, #spacer
                Param("timeout", "TQ Calib", 0.0, ""),
                Param("timeout", "Ramp End", 1500, "", max=32768),
                Param("timeout", "Ramp Start", 64000, "", max=200000),
                10, #spacer
                Param("timeout", "Limit", 28, "km/h"),
                Param("timeout", " Without PAS", 6, "km/h"),
                Param("timeout", " Offroad", 35, "km/h"),
            ],
            [
                Param("timeout", "Hall Angle 4", 1, "deg", bold=True, convert=DegreeConv),
                Param("timeout", "Hall Angle 6", 38, "deg", bold=True, convert=DegreeConv),
                Param("timeout", "Hall Angle 2", 82, "deg", bold=True, convert=DegreeConv),
                Param("timeout", "Hall Angle 3", 128, "deg", bold=True, convert=DegreeConv),
                Param("timeout", "Hall Angle 1", 166, "deg", bold=True, convert=DegreeConv),
                Param("timeout", "Hall Angle 5", 210, "deg", bold=True, convert=DegreeConv),
                Param("timeout", "Correction Angle", 127, "deg", convert=DegreeConv),
                Param("timeout", "Motor Specific Angle", 0, "deg", convert=DegreeConv),
            ]
        ]



        hb = QHBoxLayout()
        self.window = QMainWindow()
        cols = [QFormLayout() for col in params]

        for col in cols:
            hb.addLayout(col)
            hb.addSpacing(12)

        hb.addStretch(1)

        f = QGroupBox("Build parameters")
        f.setLayout(hb)

        for i in range(0, len(params)):
            for param in params[i]:
                if type(param) == int:
                    cols[i].addWidget(QFrame())
                else:
                    cols[i].addRow(param.label, param.control)



        w = QWidget()
        #w.setLayout(f)
        self.window.setCentralWidget(f)
        self.window.show()

if __name__ == "__main__":
    a = App()
    a.exec_()