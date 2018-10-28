cmake_minimum_required(VERSION 3.10)


SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_C_COMPILER sdcc)
SET(CMAKE_SYSTEM_PROCESSOR stm8)

IF(WIN32)
	LIST(APPEND CMAKE_PROGRAM_PATH  "${CMAKE_SOURCE_DIR}/cygwin/bin/")
ENDIF()

find_program (CMAKE_OBJCOPY 
	stm8-objcopy
)

find_program (CMAKE_SIZE
	stm8-size
)

find_program (STM8FLASH
	stm8flash
)
	
project(OSEC_firmware C)

set(CMAKE_EXECUTABLE_SUFFIX ".elf")
SET(CMAKE_C_FLAGS "-mstm8 --std-c99 --nolospre")
SET(CMAKE_EXE_LINKER_FLAGS "--out-fmt-elf")
SET(ELF_SECTIONS_TO_REMOVE "-R DATA -R INITIALIZED -R SSEG -R .debug_line -R .debug_loc -R .debug_abbrev -R .debug_info -R .debug_pubnames -R .debug_frame")

SET(SDIR StdPeriphLib/src)

SET(SOURCES 
	${SDIR}/stm8s_itc.c 
	${SDIR}/stm8s_clk.c 
	${SDIR}/stm8s_iwdg.c 
	${SDIR}/stm8s_gpio.c 
	${SDIR}/stm8s_exti.c 
	${SDIR}/stm8s_uart2.c 
	${SDIR}/stm8s_tim1.c 
	${SDIR}/stm8s_tim2.c 
	${SDIR}/stm8s_adc1.c 
	${SDIR}/stm8s_flash.c 
	BOdisplay.c 
	ACAcontrollerState.c 
	ACAeeprom.c 
	ACAsetPoint.c
	ACAcommons.c 
	gpio.c 
	cruise_control.c 
	uart.c 
	adc.c 
	brake.c 
	timers.c 
	pwm.c 
	motor.c 
	PAS.c 
	SPEED.c 
	display.c
	display_kingmeter.c
	main.c
)

include_directories(
	StdPeriphLib/inc
	${CMAKE_SOURCE_DIR}
)

add_executable(${PROJECT_NAME} ${SOURCES})
	
add_custom_target(hex
	COMMAND ${CMAKE_OBJCOPY} -O ihex ${ELF_SECTIONS_TO_REMOVE} ${PROJECT_NAME}.elf ${PROJECT_NAME}.ihx
	DEPENDS ${PROJECT_NAME}
)
	
add_custom_target(optionbytes
	COMMAND ${STM8FLASH} -c stlinkv2 -p stm8s105?6 -s opt -w optionbytes.hex
)

add_custom_target(flash
	COMMAND ${STM8FLASH} -c stlinkv2 -p stm8s105?6 -w ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.ihx
	DEPENDS hex
)

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_SIZE} ${PROJECT_NAME}.elf
)

