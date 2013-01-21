/*
 * WiFlyDevice.h -- WiFly device driver header
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 *
 * Based on WiFlyDevice from original WiFly library.
 */

#ifndef __WIFLYDEVICE_H__
#define __WIFLYDEVICE_H__

#include "UARTOnSPIDevice.h"

#ifndef WIFLY_RX_BUF
#define WIFLY_RX_BUF 128
#endif

#ifndef WIFLY_TX_BUF
#define WIFLY_TX_BUF 128
#endif

#ifndef WIFLY_DEFAULT_BAUDRATE
#define WIFLY_DEFAULT_BAUDRATE 9600
#endif

class WiFlyDevice
{

public:
    WiFlyDevice(UARTOnSPIDevice &uart);

    boolean begin(unsigned long baudRate = WIFLY_DEFAULT_BAUDRATE);
    void end();

    boolean join(const char *ssid, const char *key = NULL, int isWPA = true);

    boolean connect(const char *host, unsigned short port);
    boolean listen(unsigned short port);

    boolean enterCommandMode();
    boolean exitCommandMode();
    boolean sendCommand(const char *command, boolean partial = false);
    boolean softwareReset();
    boolean hardwareReset();

private:
    UARTOnSPIDevice &_uart;
    boolean _commandMode;

};

extern SPIDevice spiWiFly;
extern UARTOnSPIDevice uartWiFly;
extern WiFlyDevice WiFly;

#endif /* __WIFLYDEVICE_H__ */
