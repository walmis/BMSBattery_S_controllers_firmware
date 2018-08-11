/*
 * BMSBattery S series motor controllers firmware
 *
 * Copyright (C) Casainho, 2017.
 *
 * Released under the GPL License, Version 3
 */

#include <stdint.h>
#include "stm8s.h"
#include "stm8s_flash.h"
#include "eeprom.h"


uint8_t eeprom_read(uint8_t address_offset);
void eeprom_write (uint8_t address_offset, uint8_t value );


uint8_t eeprom_read(uint8_t address_offset)
{
  return (FLASH_ReadByte (EEPROM_BASE_ADDRESS + address_offset));
}

void eeprom_write (uint8_t address_offset, uint8_t value )
{
  FLASH_SetProgrammingTime (FLASH_PROGRAMTIME_STANDARD);
    FLASH_Unlock (FLASH_MEMTYPE_DATA);
    while (!FLASH_GetFlagStatus (FLASH_FLAG_DUL)) ;
    FLASH_ProgramByte (EEPROM_BASE_ADDRESS + address_offset, value);
    while (!FLASH_GetFlagStatus (FLASH_FLAG_EOP)) ;

  FLASH_Lock (FLASH_MEMTYPE_DATA);

}


