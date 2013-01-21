/*
 * SPIDevice.h -- generic SPI device driver header
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 *
 * Based on _Spi from original WiFly library.
 */

#ifndef __SPIDEVICE_H__
#define __SPIDEVICE_H__

#include "SPI.h"

#ifndef SPI_USE_IRQ
#define SPI_USE_IRQ 0
#endif

#if SPI_USE_IRQ
#define DEFAULT_RX_BUF_SIZE 16
#define DEFAULT_TX_BUF_SIZE 16
struct ring_buffer;
#endif

class SPIDevice
{

public:

#if SPI_USE_IRQ
    SPIDevice(uint8_t selectPin,
              unsigned int rxBufSize = DEFAULT_RX_BUF_SIZE,
              unsigned int txBufSize = DEFAULT_TX_BUF_SIZE);
    int peek();
    int read();
    void write(uint8_t c);
    void flush();
    int remaining();
    int available();
#else
    SPIDevice(uint8_t selectPin);
#endif /* SPI_USE_IRQ */

    void begin();
    void end();
    boolean select();
    boolean deselect();
    uint8_t transfer(uint8_t c);

private:
    uint8_t _selectPin;

#if SPI_USE_IRQ
    struct ring_buffer *_rxBuf;
    struct ring_buffer *_txBuf;
    volatile boolean _writeInProgress;

    void interrupt();

    friend class SPIManager;
#endif

};

#endif /* __SPIDEVICE_H__ */
