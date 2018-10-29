"""
Copyright (C) 2018  Valmantas Paliksa <walmis@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import re
QApplication.setStyle("Fusion")

class Converter:
    def from_raw(self, x):
        return x
class ADCValue(Converter):
    @staticmethod
    def from_raw(x): return x*(5.0/255)
    @staticmethod
    def from_raw_str(x): return "%.2f" % ADCValue.from_raw(x)

class Time64us(Converter):
    @staticmethod
    def from_raw(x): return (x*64.0)/1000
    @staticmethod
    def from_raw_str( x): return "%.1f" % Time64us.from_raw(x)

class CurrentConv(Converter):
    @staticmethod
    def from_raw(x): return (x/10.0)
    @staticmethod
    def from_raw_str( x): return "%.1f" % CurrentConv.from_raw(x)

class Volts3p7Conv(Converter):
    @staticmethod
    def from_raw(x): return (x/3.7)
    @staticmethod
    def from_raw_str( x): return "%.1f" % Volts3p7Conv.from_raw(x)

class DegreeConv(Converter):
    @staticmethod
    def from_raw(x): return (x*(360/255.0))
    @staticmethod
    def from_raw_str( x): # return ms
        x = DegreeConv.from_raw(x)
        return "%.1f" % x

class ConfigHeader:
    def __init__(self, filename):
        self.data = open(filename).read()
        print(self.data)

    def setDefine(self, name, value):
        r = f"^(#define {name} )(.*)$"
        self.data = re.sub(r, "\g<1>"+str(value), self.data, flags=re.MULTILINE)

    def disableDefine(self, name):
        r = f"^(#define {name} )(.*)$"
        #print (re.sub(r, "\g<1>"+str(value), self.data, flags=re.MULTILINE))

class Param:
    def __init__(self, id, desc=None, default_val=None, unit=None, convert=None, doc="", min=0, max=255, bold=False):
        self.id = id
        self.desc = desc
        self.default_val = default_val
        self.unit = unit
        self.converter = convert

        self.label = QLabel(self.desc)

        if bold:
            self.label.setStyleSheet("font-weight: bold;")

        if type(default_val) == bool:
          self.control = QCheckBox(desc)
          if default_val:
              self.control.setChecked(1)
          self.control.toggled.connect(lambda v: self.onValueChanged(v))

        elif type(default_val) == list:
            self.control = QComboBox()
            for item in default_val:
                self.control.addItem(item)

        elif type(default_val) == int:
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

        self.control.setMinimumWidth(80)

        if doc:
            self.label.setToolTip(doc)
            self.control.setToolTip(doc)

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

class BooleanParam(Param):
    def __init__(self, *args, bitmask=None, variable=None, **kwargs):
        Param.__init__(self, *args, **kwargs)
        self.var = variable
        self.bitmask = bitmask

    def onValueChanged(self, value):
        if self.var is None: return

        if value:
            self.var.value |= self.bitmask
            self.var.flags.append(self.id)
        else:
            self.var.value &= ~self.bitmask
            self.var.flags.remove(self.id)
        print("|".join(self.var.flags))



class Var:
    value = 0
    flags = []

aca_flags = Var()


config_header = ConfigHeader("../config.h")
config_header.setDefine("ACA", 1000)
config_header.setDefine("PAS_THRESHOLD", 5.0)
config_header.setDefine("RAMP_START", 5.0)

class App(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        hall_doc = "Defines the rotor angle assigned to Hall pattern X. Usually does not need to be changed.\n"\
                   "This can be used to compensate for manufacturing inaccuracies in the Hall sensor positioning, which can manifest themselves,\n"\
                   "for example, in noisy running or vibrations. In the BluOsec App, the phase current display indicates in which direction\n"\
                   "the angle must be changed in order to achieve a smoother run. In the hall order diagram there are also suggestions\n"\
                   "on how to change the angles (left column) based on actual pwm cycyles in each phase (right column)"

        self.params = [
            [
                Param("NUMBER_OF_PAS_MAGS", "No. of PAS Magnets", 12, "", bold=True,
                      doc="Number of magnets in the PAS disk. Required for correct calculation of the cadence"),
                Param("wheel_circumference", "Wheel Circumference", 2230, "mm", max=65535, bold=True,
                      doc="Wheel circumference in millimetres, is required to calculate the speed. The setting in the display is ignored."),
                Param("timeout", "PAS Timeout", 3125, "ms", bold=True, convert=Time64us, max=65535,
                      doc="Time to stop motor after stopping pedalling. Value in 64µs for Motor Speed = Normal, 48µs for Motor Speed = High. Calculation example: 3125*0,000064s = 0,2s"),
                Param("ADC_THROTTLE_MIN_VALUE", "Throttle Min", 43, unit="V", convert=ADCValue, doc="Voltage at closed throttle or torque signal. Required for adapting the throttle signal to full 8bit resolution of the PWM value. Conversion: 0V corresponds to 0, 5V corresponds to 255 (8bit resolution of the AD converter)"),
                Param("ADC_THROTTLE_MAX_VALUE", "Throttle Max", 182, unit="V", convert=ADCValue, doc="Voltage at full throttle or full deflection of the torque signal, explanation analogous to Throttle min"),
                Param("BATTERY_CURRENT_MAX_VALUE", "Battery Current Max", 150, unit="A", convert=CurrentConv, doc="Maximum battery current. Calculation: Value = desired current in ampere multiplied by the value from field Battery Current cal a.\nExample with the default values for limiting to 15A: 15A *10 = 150"),
                Param("PHASE_CURRENT_MAX_VALUE", "Phase Current Max", 300, unit="A", convert=CurrentConv, bold=True, max=1000, doc="Maximum phase current. Calculation like Battery Current max.\nThe phase current is derived from the formula phase current = battery current / duty cycle internally."),
                Param("REGEN_CURRENT_MAX_VALUE", "Regen Current Max", 50, unit="A", convert=CurrentConv, doc="Maximum recuperation current. Calculation analogous to Battery Current calculate max. desired current as negative value."),
                Param("BATTERY_VOLTAGE_MIN_VALUE", "Undervoltage Limit", 148, "V", bold=True, convert=Volts3p7Conv, doc="Undervoltage cutoff value. Calculation: Value in volts times 3.7. example: 34.3V * 3.7 = 127"),
                Param("BATTERY_LI_ION_CELLS_NUMBER", "Serial Cells", 13, "cells", max=20, bold=True, doc="Number of battery cells connected in series. For 36V systems normally \"10\", for 24V systems \"7\",\nthis information is required for the correct display of the bars in the LCD3-display."),
                Param("current_cal_a", "Battery Current Cal A", 46, "gain", doc="Factor a in the calibration function. 1A = a/10 * ADC value. Required for internal calculation of the current from the 10bit ADC value.\nOnly needs to be changed if the calibration obviously does not fit with the preset values."),
                Param("TEMP_CAL_A", "Temperature Cal A", 1.6, "", max=65535, bold=True, doc="Factor a in the calibration function temperature in °C = a * ADC value + b.\nFor temperature calculation from external sensor connected to pad X4 and GND.\nTemperature is shown in the LCD3 but not processed to reduce power if temperature is getting to high actually."),
                Param("TEMP_CAL_B", "Temperature Cal B", -110.4, "", min=-32767, max=32768, bold=True, doc="Factor b in the calibration function temperature in °C = a * ADC value + b.\nDefault values are for a KTY84 sensor."),

                Param("P_FACTOR", "Gain P", 0.5, "", doc="Proportional factor of the PI controller.\nThe higher the value is selected, the higher the risk, that the control starts oscillating."),
                Param("I_FACTOR", "Gain I", 0.2, "", doc="Integral factor of the PI controller.\nThe smaller the value, the smoother the control runs into the setpoint. Both gain values must be written with a dot as a decimal separator."),
                Param("GEAR_RATIO", "Gear Ratio", 24, "", bold=True, doc="Ratio of electrical revolutions to wheel revolutions.\nThe value is half the value of P1 for Kunteng displays, since P1 uses the number of magnets and for Gear Ratio, we need the number of pole pairs.\nOnly needed if option Speed sensor = Internal."),
                Param("ADC_BATTERY_VOLTAGE_K", "Battery Voltage Cal", 68, "", doc="Used for internal calculation of the voltage from the 8bit ADC value.\nMust only be changed if the calibration with the preset values obviously does not fit."),
                Param("PAS_THRESHOLD", "PAS Threshold", 1.9, "", doc="Threshold for direction detection from the PAS signal.\nThe value should be the arithmetic mean of the reciprocal of the duty cycle of the PAS-signal during forward and reverse rotation.\nThe appropriate value can be determined by trial and error or by looking at the displayed values at turning the pedals forwards and backwards in \"Diagnostics\" mode.\nThe preset 1.7 was determined for a simple PAS with 8 magnets."),
            ],
            [
                Param("LEVEL_1", "Assist Level 1", 12, "%", bold=True, doc="Support factor level 1 in torque sensor and torque simulation mode. Calculated as a percentage with the assist factor / maximum battery current"),
                Param("LEVEL_2", "Assist Level 2", 21, "%", bold=True, doc="Support factor level 2 in torque sensor and torque simulation mode. Calculated as a percentage with the assist factor / maximum battery current"),
                Param("LEVEL_3", "Assist Level 3", 30, "%", bold=True, doc="Support factor level 3 in torque sensor and torque simulation mode. Calculated as a percentage with the assist factor / maximum battery current"),
                Param("LEVEL_4", "Assist Level 4", 59, "%", bold=True, doc="Support factor level 4 in torque sensor and torque simulation mode. Calculated as a percentage with the assist factor / maximum battery current"),
                Param("LEVEL_5", "Assist Level 5", 100, "%", bold=True, doc="Support factor level 5 in torque sensor and torque simulation mode. Calculated as a percentage with the assist factor / maximum battery current"),

                Param("MORSE_TIME_1", "Morse Time 1", 50, "", bold=True, doc="Is the first time of the morse code in 1/50s. The value 50 means one second.\nThe cheat works like this: Hold the brake lever for cheat time 1, then release it for the duration of cheat time 2,\nthen pull it again for cheat time 3, then release it again. For step 1 with a value of 50,\nthe release of the brake lever is recognized as valid for a period of 1 to 1.5 seconds after pulling and continues with step 2.\nIf the lever is released too early or too late, the whole procedure is reset and you have to start all over again.\nCurrently the user does not get any feedback on whether the cheat has been activated."),
                Param("MORSE_TIME_2", "Morse Time 2", 50, "", bold=True, doc="See morse 1"),
                Param("MORSE_TIME_3", "Morse Time 3", 50, "", bold=True, doc="See morse 1"),
                10, #spacer
                Param("TQS_CALIB", "TQ Calib", 0.0, "", doc="Factor for calculating the torque sensor support.\nCalibration factors of the measurement chain are summarized here.\nGreater value: More support with equal human performance. The value is internally offset with the percentage defined in the Assist level."),
                Param("RAMP_END", "Ramp End", 1500, "", max=32768, doc="Duration of time between two PAS pulses in 64µs (48µs for Motor speed = High),\nwhich belongs to the desired limit cadence in torque simulation mode.\nValue = 60/ ((Wish cadence in 1/min)Number of PAS magnets64µs). \nExample calculation for a limit cadence of 60/min: 60/ (60160,000064)=977"),
                Param("RAMP_START", "Ramp Start", 64000, "", max=200000, doc="Maximum time that is still fed into the calculation (this influences how fast the startup response is after a standstill)"),
                10, #spacer
                Param("limit", "Limit", 28, "km/h", doc="Speed limit"),
                Param("limit_without_pas", " Without PAS", 6, "km/h", doc="How fast you can drive without pedaling"),
                Param("limit_with_throttle_override", " Offroad", 35, "km/h", doc="How fast the throttle overrides your normal speedlimit (only works if offroading is enabled)"),
                10,
                Param("SPEEDSENSOR_", "Speed Sensor", ["Internal", "External"], doc="<b>Internal:</b> Speed is calculated from the motor commutation.\nNo speed is displayed here for motors with freewheel function when the motor is at standstill.<br> <b>External:</b> Speed is calculated from external sensor signal.\nThe speed is always correctly displayed here,\neven when the motor is at a standstill and in the case of middrive motors."),
                Param("PWM_CYCLES_SECOND", "PWM Frequency", ["Normal", "High"], doc="<b>Normal:</b> PWM frequency 15.625 kHZ, sufficient for direct drive and most hub and mid-engines.<br><b>High:</b> PWM frequency 20.833 kHz, for very fast rotating motors"),
                Param("DISPLAY_TYPE_", "Display Type", [ "BluOsec App", "None", "Kingmeter J-LCD", "KT-LCD3", "Diagnostics UART"], doc="<span><b>BluOsec:</b> Bluetooth module needed & Android App. see \"Supported Displays\" below.<br><b>None:</b> No display support.<br><b>Kingmeter J-LCD:</b> Support of the Kingmeter J-LCD and the Lishui Forerider-App. At present, only the normal operating mode works, the programming mode of the display and the app are not supported.<br><b>KT-LCD3:</b> Support of Kunteng LCD3, only the speed and wheel size are used. All other settings are currently without function.<br><b>Diagnostics:</b> If this option is activated, the display protocol is not sent via UART, but some selected internal variables. Connect Rx of the display connector to GND (yellow to black) if you don't want to sent any data to the controller, even if you use Tx for diagnostics. These five values are sent as default: duty cycle of the PWM (0... 255), ERPS, battery current (10bit AD converter value), battery voltage (10bit AD converter value), advance angle.</span>"),

            ],
            [
                Param("ANGLE_4_0", "Hall Angle 4", 1, "deg", bold=True, convert=DegreeConv, doc=hall_doc),
                Param("ANGLE_6_60", "Hall Angle 6", 38, "deg", bold=True, convert=DegreeConv, doc=hall_doc),
                Param("ANGLE_2_120", "Hall Angle 2", 82, "deg", bold=True, convert=DegreeConv, doc=hall_doc),
                Param("ANGLE_3_180", "Hall Angle 3", 128, "deg", bold=True, convert=DegreeConv, doc=hall_doc),
                Param("ANGLE_1_240", "Hall Angle 1", 166, "deg", bold=True, convert=DegreeConv, doc=hall_doc),
                Param("ANGLE_5_300", "Hall Angle 5", 210, "deg", bold=True, convert=DegreeConv, doc=hall_doc),
                10,
                Param("CORRECTION_AT_ANGLE", "Correction Angle", 127, "deg", convert=DegreeConv, doc="This is the angle at which the Advance Angle is automatically adjusted. In case of doubt set to 127!"),
                Param("MOTOR_ROTOR_DELTA_PHASE_ANGLE_RIGHT", "Motor Specific Angle", 0, "deg", convert=DegreeConv, doc="<b></b>With this value the timing of the motor control can be changed.\nAs a result, manufacturing inaccuracies of the Hall sensor positions in the motor can be compensated.\nOnly change if the motor starts badly. If unsure start with 0 <b>(this has changed recently from 213, default angle is no longer -60° but 0°)</b>"),
            ]
        ]

        hb = QHBoxLayout()
        cols = [QFormLayout() for col in self.params]

        for col in cols:
            hb.addLayout(col)
            hb.addSpacing(12)

        hb.addStretch(1)

        for i in range(0, len(self.params)):
            for param in self.params[i]:
                if type(param) == int:
                    cols[i].addWidget(QFrame())
                else:
                    cols[i].addRow(param.label, param.control)

        f = QGroupBox("Build parameters")
        f.setLayout(hb)

        vb = QVBoxLayout()
        vb.addLayout(hb)
        vb.addWidget(f)


        g = QGroupBox("Ride Options")
        hb = QHBoxLayout()
        hb.addWidget(g)
        vb.addLayout(hb)

        btns = QVBoxLayout()
        btns.addWidget(QPushButton("Load Defaults"))
        btns.addWidget(QPushButton("Load Config"))
        btns.addWidget(QPushButton("Save Config"))
        btns.addWidget(QPushButton("Save Config As"))
        btns.addWidget(QPushButton("Flash"))
        btns.addWidget(QPushButton("Initialize controller"))

        hb.addLayout(btns)




        self.ride_opts = [
            BooleanParam("BYPASS_LOW_SPEED_REGEN_PI_CONTROL","Bypass PI control regen @low speed", default_val=False, bitmask=256, variable=aca_flags,
                         doc="This improves the regeneration rate at low speeds, more or less the opposite to \"Speed influences Regen Rate\""),
            BooleanParam("TQ_SENSOR_MODE","Torque Sensor Enabled", default_val=False, bitmask=2048, variable=aca_flags),
            BooleanParam("ASSIST_LVL_AFFECTS_THROTTLE","Assist level affects throttle", default_val=False, bitmask=1, variable=aca_flags),
            BooleanParam("OFFROAD_ENABLED","Offroad enabled", default_val=False, bitmask=2, variable=aca_flags),
            BooleanParam("BRAKE_DISABLES_OFFROAD","Brake disables offroad", default_val=False, bitmask=4, variable=aca_flags),
            BooleanParam("DIGITAL_REGEN","Regen Digital (no x4 throttle)", default_val=False, bitmask=8, variable=aca_flags),
            BooleanParam("SPEED_INFLUENCES_REGEN","Speed influences regen rate", default_val=False, bitmask=16, variable=aca_flags),
            BooleanParam("SPEED_INFLUENCES_TORQUESENSOR","Speed influences torque sensor", default_val=False, bitmask=32, variable=aca_flags),
            BooleanParam("PAS_INVERTED","PAS inverted", default_val=False, bitmask=64, variable=aca_flags),
            BooleanParam("DYNAMIC_ASSIST_LEVEL","Dynamic assist level", default_val=False, bitmask=512, variable=aca_flags),
            BooleanParam("ANGLE_CORRECTION_ENABLED","Enable rotor angle correction", default_val=False, bitmask=4096, variable=aca_flags,
                         doc="The automatic adjustment of the advance angle is activated. If a ZVS type is used, the option must remain deactivated.\n"\
                              "The controller will then not run at optimum efficiency and generate unnecessary heat."),
            "<b>Experimental flags</b>",
            BooleanParam("PWM_AUTO_OFF","PWM off when coasting (experimental)", default_val=False),
            BooleanParam("DC_STATIC_ZERO","DC static zero (experimental)", default_val=False)
        ]

        opts = QGridLayout()
        row = 0
        col = 0
        for p in self.ride_opts:
            if type(p) == str:
                opts.addWidget(QLabel(p), row, col)
            else:
                opts.addWidget(p.control, row, col)
            row+=1
            if row > 6:
                col+=1
                row = 0

        g.setLayout(opts)


        w = QWidget()
        w.setLayout(vb)
        self.window = QMainWindow()
        self.window.setCentralWidget(w)
        self.window.show()

if __name__ == "__main__":
    a = App()
    a.exec_()