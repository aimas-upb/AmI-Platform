/*
 * UARTOnSPIDevice.h -- UARTOnSPI device driver header
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 *
 * Based on SpiUart from original WiFly library.
 */

#ifndef __UARTONSPIDEVICE_H__
#define __UARTONSPIDEVICE_H__

#include "SPIDevice.h"

struct ring_buffer;

class UARTOnSPIDevice : public Print
{

public:
    UARTOnSPIDevice(SPIDevice &spi, unsigned int rxBufSize, unsigned int txBufSize);

    boolean begin(unsigned long baudRate);
    void end();

    boolean connected();

    void setBaudRate(unsigned long baudRate = 9600);
    void setFlowControl(boolean autoCTS = true, boolean autoRTS = true);
    void setFIFO(boolean useFIFO = true, uint8_t rxTrigger = 3, uint8_t txTrigger = 3);

    int remaining();
    int available();
    int read();
    size_t write(uint8_t data);
    size_t writeBuffered(uint8_t data);
    size_t write(const char *str);
    size_t write(const uint8_t *buf, size_t size);
    size_t writeFast(const uint8_t *buf, size_t size);
    void flush();

    void ioSetDirection(uint8_t bits);
    void ioSetState(uint8_t bits);

    void interrupt() { _irqPending = true; }
    void processInterrupts();

private:
    SPIDevice &_spi;
    uint8_t _ier;
    uint8_t _rxLvl;
    uint8_t _txLvl;
    volatile boolean _irqPending;
    struct ring_buffer *_rxBuf;
    struct ring_buffer *_txBuf;

    void writeRegister(uint8_t reg, uint8_t data);
    void writeBulk(uint8_t size);
    uint8_t readRegister(uint8_t reg);
    void readBulk(uint8_t size);

    void enableInterrupts(uint8_t mask);
    void disableInterrupts(uint8_t mask);

};

#endif /* __UARTONSPIDEVICE_H__ */
