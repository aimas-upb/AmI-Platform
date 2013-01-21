/*
 * SPIManager.h -- SPI device manager header
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#ifndef __SPIDEVICEMANAGER_H__
#define __SPIDEVICEMANAGER_H__

#include "SPIDevice.h"

class SPIManager
{

public:
    SPIManager();

    void registerDevice();
    void unregisterDevice();

    boolean select(SPIDevice *dev);
    boolean deselect(SPIDevice *dev);

    inline boolean busy() { return !!_activeDev; }

#if SPI_USE_IRQ
    void interrupt();
#endif

private:
    uint8_t _count;
    SPIDevice *_activeDev;

};

#endif /* __SPIDEVICEMANAGER_H__ */
