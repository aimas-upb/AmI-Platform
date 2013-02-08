/*
 * UARTOnSPIDevice.cpp -- UARTOnSPI device driver implementation
 *
 * Works with the SC16IS750 chip on WiFly boards, rev 3.
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 *
 * Based on SpiUart from original WiFly library.
 */

#include "UARTOnSPIDevice.h"
#include "SC16IS750.h"
#include "buffer.h"

UARTOnSPIDevice::UARTOnSPIDevice(SPIDevice &spi, unsigned int rxBufSize, unsigned int txBufSize) : _spi(spi)
{
    _irqPending = false;
    _ier = 0;
    _rxLvl = 0;
    _txLvl = 0;
    _rxBuf = buffer_alloc(rxBufSize);
    _txBuf = buffer_alloc(txBufSize);
}

boolean UARTOnSPIDevice::begin(unsigned long baudRate)
{
    _spi.begin();

    writeRegister(IER, _ier);

    setBaudRate(baudRate);
    setFlowControl();
    setFIFO();

    if (!connected())
        return false;

    _rxLvl = readRegister(RXLVL);
    _txLvl = readRegister(TXLVL);

    enableInterrupts(IER_RHR);

    return true;
}

void UARTOnSPIDevice::end()
{
    disableInterrupts(IER_RHR | IER_THR);
    _spi.end();
}

void UARTOnSPIDevice::setBaudRate(unsigned long baudRate)
{
    unsigned int divisor = BAUD_RATE_DIVISOR(baudRate);

    writeRegister(LCR, LCR_ENABLE_DIVISOR_LATCH);
    writeRegister(DLL, lowByte(divisor));
    writeRegister(DLM, highByte(divisor));
}

void UARTOnSPIDevice::setFlowControl(boolean autoCTS, boolean autoRTS)
{
    writeRegister(LCR, 0xBF);
    writeRegister(EFR, EFR_ENABLE_ENHANCED_FUNCTIONS
                       | (autoCTS ? EFR_ENABLE_CTS : 0)
                       | (autoRTS ? EFR_ENABLE_RTS : 0));
    writeRegister(LCR, 0x03); // 8 data bit, 1 stop bit, no parity
}

void UARTOnSPIDevice::setFIFO(boolean useFIFO, uint8_t rxTrigger, uint8_t txTrigger)
{
    writeRegister(FCR, 0x06); // reset TXFIFO, reset RXFIFO, non FIFO mode
    if (useFIFO)
        writeRegister(FCR, 0x01 | ((rxTrigger & 0x03) << 6)
                                | ((txTrigger & 0x03) << 4)); // enable FIFO mode and set RX/TX triggers
    else
        writeRegister(FCR, 0x00); // non FIFO mode

    _rxLvl = 0;
    _txLvl = 0;
}

boolean UARTOnSPIDevice::connected()
{
    const char TEST_CHARACTER = 'H';

    writeRegister(SPR, TEST_CHARACTER);

    return readRegister(SPR) == TEST_CHARACTER;
}

int UARTOnSPIDevice::remaining()
{
    return buffer_space(_txBuf);
}

int UARTOnSPIDevice::available()
{
    return buffer_len(_rxBuf) + _rxLvl;
}

int UARTOnSPIDevice::read()
{
    uint8_t data;

    if (!available())
        return -1;

    if (buffer_empty(_rxBuf)) {
        readBulk(min(_rxLvl, buffer_space(_rxBuf)));
        _rxLvl -= buffer_len(_rxBuf);
        if (!_rxLvl)
            enableInterrupts(IER_RHR);
    }

    buffer_read(_rxBuf, &data);
    
    return data;
}

size_t UARTOnSPIDevice::write(uint8_t data)
{
    if (!_txLvl || !buffer_empty(_txBuf)) {
        buffer_write(_txBuf, data);
        return 1;
    }

    writeRegister(THR, data);
    if (!--_txLvl)
        enableInterrupts(IER_THR);

    return 1;
}

size_t UARTOnSPIDevice::writeBuffered(uint8_t data)
{
    int n;

    buffer_write(_txBuf, data);
    if (!buffer_full(_txBuf))
        return 1;

    n = min(_txLvl, buffer_len(_txBuf));
    if (!n)
        return 1;

    writeBulk(n);
    _txLvl -= n;
    if (!_txLvl)
        enableInterrupts(IER_THR);

    return 1;
}

size_t UARTOnSPIDevice::write(const char *str)
{
    int i, ret, n;

    ret = 0;
    for (i = 0; *str; i++, ret++)
        buffer_write(_txBuf, *str++);

    n = min(_txLvl, buffer_len(_txBuf));
    if (!n)
        return ret;

    writeBulk(n);
    _txLvl -= n;
    if (!_txLvl) {
        if (buffer_len(_txBuf))
            while (_txLvl < 32)
                _txLvl = readRegister(TXLVL);
        else
            enableInterrupts(IER_THR);
    }

    return ret;
}

size_t UARTOnSPIDevice::write(const uint8_t *buf, size_t size)
{
    int i, n;

    for (i = 0; i < size; i++)
        buffer_write(_txBuf, buf[i]);

    n = min(_txLvl, buffer_len(_txBuf));
    if (!n)
        return size;

    writeBulk(n);
    _txLvl -= n;

    if (!_txLvl) {
        if (buffer_len(_txBuf))
            while (_txLvl < 32)
                _txLvl = readRegister(TXLVL);
        else
            enableInterrupts(IER_THR);
    }

    return size;
}

size_t UARTOnSPIDevice::writeFast(const uint8_t *buf, size_t size)
{
    int i;

    for (i = 0; i < size; i++)
        buffer_write(_txBuf, buf[i]);

    writeBulk(size);

    return size;
}

void UARTOnSPIDevice::flush()
{
    while (!buffer_empty(_txBuf))
        write(NULL, 0);
}

void UARTOnSPIDevice::ioSetDirection(uint8_t bits)
{
    writeRegister(IODIR, bits);
}

void UARTOnSPIDevice::ioSetState(uint8_t bits)
{
    writeRegister(IOSTATE, bits);
}

void UARTOnSPIDevice::writeRegister(uint8_t reg, uint8_t data)
{
    _spi.select();
    _spi.transfer(reg << 3);
    _spi.transfer(data);
    _spi.deselect();
}

void UARTOnSPIDevice::writeBulk(uint8_t size)
{
    uint8_t data;

    _spi.select();
    _spi.transfer(THR << 3);
    while (size--) {
        buffer_read(_txBuf, &data);
        _spi.transfer(data);
    }
    _spi.deselect();
}

uint8_t UARTOnSPIDevice::readRegister(uint8_t reg)
{
    uint8_t data;

    _spi.select();
    _spi.transfer(SPI_READ_MODE_FLAG | (reg << 3));
    data = _spi.transfer(SPI_DUMMY_BYTE);
    _spi.deselect();

    return data;
}

void UARTOnSPIDevice::readBulk(uint8_t size)
{
    uint8_t data;

    _spi.select();
    _spi.transfer(SPI_READ_MODE_FLAG | (RHR << 3));
    while (size--) {
        data = _spi.transfer(SPI_DUMMY_BYTE);
        buffer_write(_rxBuf, data);
    }
    _spi.deselect();
}

void UARTOnSPIDevice::enableInterrupts(uint8_t mask)
{
    mask |= _ier;
    if (_ier != mask) {
        _ier = mask;
        writeRegister(IER, mask);
    }
}

void UARTOnSPIDevice::disableInterrupts(uint8_t mask)
{
    mask &= _ier;
    if (_ier != mask) {
        _ier = mask;
        writeRegister(IER, mask);
    }
}

void UARTOnSPIDevice::processInterrupts()
{
    if (!_irqPending)
        return;

    readRegister(IIR);

    _rxLvl = readRegister(RXLVL);
    if (_rxLvl)
        disableInterrupts(IER_RHR);

    _txLvl = readRegister(TXLVL);
    if (_txLvl) {
        disableInterrupts(IER_THR);
        write(NULL, 0);
    }

    if (_txLvl) // HACK?
        _irqPending = false;
}
