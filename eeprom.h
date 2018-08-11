/*
 * BMSBattery S series motor controllers firmware
 *
 * Copyright (C) Casainho, 2017.
 *
 * Released under the GPL License, Version 3
 */

#ifndef _EEPROM_H_
#define _EEPROM_H_

#include "main.h"

#define KEY 0xca

#define EEPROM_BASE_ADDRESS 			0x4000
#define ADDRESS_KEY 				EEPROM_BASE_ADDRESS



void eeprom_write (uint8_t adress_offset, uint8_t value);
uint8_t eeprom_read(uint8_t address_offset);

#endif /* _EEPROM_H_ */
