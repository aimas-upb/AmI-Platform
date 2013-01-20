TOOLS_DIR     ?= .
LIBRARIES_DIR ?= $(TOOLS_DIRS)/../libraries

# Options can be overriden in Config.mk
-include $(TOOLS_DIR)/Config.mk

BOARD_TAG          ?= mega2560
ARDUINO_PORT       ?= /dev/ttyACM0

DEFAULT_BAUDRATE   ?= 115200
DEFAULT_LOG_FILE   ?= log.dat

ARDUINO_DIR        ?= /usr/share/arduino
ARDUINO_LIB_PATH   ?= $(LIBRARIES_DIR)
AVRDUDE_ARD_EXTRA_OPTS ?= -D
PARSE_BOARD        ?= $(TOOLS_DIR)/ard-parse-boards --boards_txt=$(BOARDS_TXT)

include $(TOOLS_DIR)/Arduino.mk

term: reset
	$(TOOLS_DIR)/miniterm.py -b $(DEFAULT_BAUDRATE) $(ARDUINO_PORT)

logterm: reset
	$(TOOLS_DIR)/miniterm.py -b $(DEFAULT_BAUDRATE) -l $(DEFAULT_LOG_FILE) $(ARDUINO_PORT)

.PHONY: term logterm
