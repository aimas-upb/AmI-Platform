/*
 * SPIManager.cpp -- SPI device manager implementation
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#include "SPIManager.h"

SPIManager::SPIManager()
{
    _count = 0;
    _activeDev = NULL;
}

void SPIManager::registerDevice()
{
    if (!_count) {
        SPI.begin();
        SPI.setBitOrder(MSBFIRST);
        SPI.setDataMode(SPI_MODE0);
        SPI.setClockDivider(SPI_CLOCK_DIV2);
    }
    _count++;
}

void SPIManager::unregisterDevice()
{
    _count--;
    if (!_count)
        SPI.end();
}

boolean SPIManager::select(SPIDevice *dev)
{
    if (_activeDev) {
        Serial.println("SPIManager::select failed.");
        return false;
    }
    _activeDev = dev;
    return true;
}

boolean SPIManager::deselect(SPIDevice *dev)
{
    if (_activeDev != dev) {
        Serial.println("SPIManager::deselect failed.");
        return false;
    }
    _activeDev = NULL;
    return true;
}

#if SPI_USE_IRQ
void SPIManager::interrupt()
{
    if (!_activeDev)
        return;
    _activeDev->interrupt();
}
#endif
