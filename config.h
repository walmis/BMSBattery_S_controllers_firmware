/*
 * config.h
 *
 *  Automatically created by OSEC Parameter Configurator
 *  Author: stancecoke
 */

#ifndef CONFIG_H_
#define CONFIG_H_

#define NUMBER_OF_PAS_MAGS 12
#define limit 25
#define timeout 3125
#define wheel_circumference 2200L
#define limit_without_pas 6
#define ADC_THROTTLE_MIN_VALUE 43
#define ADC_THROTTLE_MAX_VALUE 182
#define BATTERY_VOLTAGE_MIN_VALUE 111
#define BATTERY_CURRENT_MAX_VALUE 100L
#define PHASE_CURRENT_MAX_VALUE 150L
#define REGEN_CURRENT_MAX_VALUE 50L
#define MOTOR_ROTOR_DELTA_PHASE_ANGLE_RIGHT 26
#define current_cal_a 100
#define TEMP_CAL_A 1.6
#define TEMP_CAL_B -110.4
#define LEVEL_1 20
#define LEVEL_2 40
#define LEVEL_3 60
#define LEVEL_4 80
#define LEVEL_5 100
#define MORSE_TIME_1 50
#define MORSE_TIME_2 50
#define MORSE_TIME_3 50
#define RAMP_END 1500
#define P_FACTOR 0.5
#define I_FACTOR 0.2
#define GEAR_RATIO 11L
#define BATTERY_LI_ION_CELLS_NUMBER 10
#define PAS_THRESHOLD 1.7
#define RAMP_START 64000
#define limit_with_throttle_override 25
#define CORRECTION_AT_ANGLE 127
#define PWM_CYCLES_SECOND 15625L
#define SPEEDSENSOR_INTERNAL
#define ANGLE_4_0 1
#define ANGLE_6_60 43
#define ANGLE_2_120 86
#define ANGLE_3_180 128
#define BLUOSEC
#define ANGLE_1_240 171
#define ANGLE_5_300 213
#define TQS_CALIB 0.0
#define ACA 4760
#define EEPROM_NOINIT // eeprom will not be cleared
#define EEPROM_INIT_MAGIC_BYTE 142 // makes sure (chance of fail 1/255) eeprom is invalidated after flashing new config
#define ADC_BATTERY_VOLTAGE_K 70
#define ACA_EXPERIMENTAL 128

#endif /* CONFIG_H_ */
