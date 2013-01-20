/*
 * SPIDevice.cpp -- generic SPI device driver implementation
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 *
 * Based on _Spi from original WiFly library.
 */

#include "SPIDevice.h"
#include "SPIManager.h"

#if SPI_USE_IRQ
#include "buffer.h"
#endif /* SPI_USE_IRQ */

static SPIManager SPIMgr;


#if SPI_USE_IRQ
SIGNAL(SPI_STC_vect)
{
    SPIMgr.interrupt();
}
#endif /* SPI_USE_IRQ */

#if SPI_USE_IRQ
SPIDevice::SPIDevice(uint8_t selectPin, unsigned int rxBufSize, unsigned int txBufSize)
{
    _selectPin = selectPin;
    _rxBuf = buffer_alloc(rxBufSize);
    _txBuf = buffer_alloc(txBufSize);
    _writeInProgress = false;
}
#else
SPIDevice::SPIDevice(uint8_t selectPin)
{
    _selectPin = selectPin;
}
#endif /* SPI_USE_IRQ */

void SPIDevice::begin()
{
    SPIMgr.registerDevice();
    pinMode(_selectPin, OUTPUT);
}

void SPIDevice::end()
{
    SPIMgr.unregisterDevice();
}

boolean SPIDevice::select()
{
    if (!SPIMgr.select(this))
        return false;

    digitalWrite(_selectPin, LOW);

    return true;
}

boolean SPIDevice::deselect()
{
    if (!SPIMgr.deselect(this))
        return false;

    digitalWrite(_selectPin, HIGH);

    return true;
}

uint8_t SPIDevice::transfer(uint8_t c)
{
    SPDR = c;
    while (!(SPSR & _BV(SPIF))) ;

    return SPDR;
}

#if SPI_USE_IRQ

int SPIDevice::peek()
{
    uint8_t c;

    if (!buffer_peek_atomic(_rxBuf, &c))
        return -1;

    return c;
}

int SPIDevice::read()
{
    uint8_t c;

    if (!buffer_read_atomic(_rxBuf, &c))
        return -1;

    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        if (!_writeInProgress && !buffer_empty(_txBuf)) {
            buffer_read(_txBuf, &c);
            SPDR = c;
            _writeInProgress = true;
            SPI.attachInterrupt();
        }

    return c;
}

void SPIDevice::write(uint8_t c)
{
    while (!buffer_write_atomic(_txBuf, c))
        delay(1);

    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        if (!_writeInProgress && !buffer_empty(_txBuf) && !buffer_full(_rxBuf)) {
            buffer_read(_txBuf, &c);
            SPDR = c;
            _writeInProgress = true;
            SPI.attachInterrupt();
        }

    transfer(c);
}

void SPIDevice::flush()
{
    uint8_t c;

    while (_writeInProgress) ;
    buffer_clear(_rxBuf);

    while (buffer_read(_txBuf, &c)) {
        SPDR = c;
        while (!(SPSR & _BV(SPIF))) ;
    }
}

int SPIDevice::remaining()
{
    return buffer_len_atomic(_txBuf);
}

int SPIDevice::available()
{
    return buffer_len_atomic(_rxBuf);
}

void SPIDevice::interrupt()
{
    uint8_t c;

    if (SPSR & _BV(WCOL)) {
        c = SPDR;
        return;
    }

    c = SPDR;
    buffer_write(_rxBuf, c);

    if (buffer_full(_rxBuf)) {
        SPI.detachInterrupt();
        _writeInProgress = false;
    } else if (buffer_read(_txBuf, &c)) {
        SPDR = c;
    } else {
        _writeInProgress = false;
    }

}

#endif /* SPI_USE_IRQ */

