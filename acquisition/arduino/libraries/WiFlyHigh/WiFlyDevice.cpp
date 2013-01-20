/*
 * WiFlyDevice.cpp -- WiFly device driver implementation
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 *
 * Based on WiFlyDevice from original WiFly library.
 */

#include "WiFlyDevice.h"
#include "pins_arduino.h"

#define COMMAND_MODE_GUARD_TIME 250 // in milliseconds

SPIDevice spiWiFly(SS);
UARTOnSPIDevice uartWiFly(spiWiFly, WIFLY_RX_BUF, WIFLY_TX_BUF);
WiFlyDevice WiFly(uartWiFly);


WiFlyDevice::WiFlyDevice(UARTOnSPIDevice &uart) : _uart(uart)
{
}

boolean WiFlyDevice::begin(unsigned long baudRate)
{
    _uart.begin(baudRate);
}

void WiFlyDevice::end()
{
    _uart.end();
}

boolean WiFlyDevice::join(const char *ssid, const char *key, int isWPA)
{
    if (!enterCommandMode())
        return false;

    if (key && *key) {
        if (isWPA)
            _uart.print("set wlan phrase ");
        else
            _uart.print("set wlan key ");
        _uart.println(key);
    }

    _uart.print("join ");
    _uart.println(ssid);

    return true;
}

boolean WiFlyDevice::connect(const char *host, unsigned short port)
{
    if (!enterCommandMode())
        return false;

    _uart.print("open ");
    _uart.print(host);
    _uart.print(" ");
    _uart.println(port);

    return true;
}

boolean WiFlyDevice::listen(unsigned short port)
{
   if (!enterCommandMode())
        return false;

    _uart.print("set ip localport ");
    _uart.println(port);

    return true;
}

boolean WiFlyDevice::enterCommandMode()
{
    if (_commandMode)
        return true;

    delay(COMMAND_MODE_GUARD_TIME);
    _uart.print("$$$");
    delay(COMMAND_MODE_GUARD_TIME);

    _commandMode = true;

    return true;
}

boolean WiFlyDevice::exitCommandMode()
{
    if (!_commandMode)
        return true;

    _uart.println("exit");

    _commandMode = false;

    return true;
}

boolean WiFlyDevice::sendCommand(const char *command, boolean partial)
{
    if (!enterCommandMode())
        return false;

    if (partial)
        _uart.print(command);
    else
        _uart.println(command);

    return true;
}

boolean WiFlyDevice::softwareReset()
{
    if (!enterCommandMode())
        return false;

    _uart.println("reboot");

    _commandMode = false;

    return true;
}

boolean WiFlyDevice::hardwareReset()
{
    _uart.ioSetDirection(0x2);
    _uart.ioSetState(0x0);
    delay(1);
    _uart.flush();
    while (_uart.available())
        _uart.read();
    _uart.ioSetState(0x2);

    _commandMode = false;

    return true;
}
