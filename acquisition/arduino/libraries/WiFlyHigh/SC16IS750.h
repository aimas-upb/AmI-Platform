/*
 * SC16IS750.h -- header file for SC16IS750 chip
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 *
 * Based on SpiUart from original WiFly library.
 */

#ifndef __SC16IS750_H__
#define __SC16IS750_H__

// SC16IS750 Register definitions
#define THR        0x00
#define RHR        0x00
#define IER        0x01
#define FCR        0x02
#define IIR        0x02
#define LCR        0x03
#define MCR        0x04
#define LSR        0x05
#define MSR        0x06
#define SPR        0x07
#define TXLVL      0x08
#define RXLVL      0x09
#define DLAB       0x80
#define IODIR      0x0A
#define IOSTATE    0x0B
#define IOINTMSK   0x0C
#define IOCTRL     0x0E
#define EFCR       0x0F

#define DLL        0x00
#define DLM        0x01
#define EFR        0x02
#define XON1       0x04
#define XON2       0x05
#define XOFF1      0x06
#define XOFF2      0x07

#define SPI_READ_MODE_FLAG   0x80
#define SPI_DUMMY_BYTE       0xFF

#define IER_RHR    0x01
#define IER_THR    0x02

#define IIR_MASK   0x3E
#define IIR_RXTO   0x0C
#define IIR_RHR    0x04
#define IIR_THR    0x02

// See section 8.10 of the datasheet for definitions
// of bits in the Enhanced Features Register (EFR)
#define EFR_ENABLE_CTS _BV(7)
#define EFR_ENABLE_RTS _BV(6)
#define EFR_ENABLE_ENHANCED_FUNCTIONS _BV(4)

// See section 8.4 of the datasheet for definitions
// of bits in the Line Control Register (LCR)
#define LCR_ENABLE_DIVISOR_LATCH _BV(7)

// The original crystal frequency used on the board (~12MHz) didn't
// give a good range of baud rates so around July 2010 the crystal
// was replaced with a better frequency (~14MHz).
#ifndef USE_14_MHZ_CRYSTAL
#define USE_14_MHZ_CRYSTAL true // true (14MHz) , false (12 MHz)
#endif

#if USE_14_MHZ_CRYSTAL
#define XTAL_FREQUENCY 14745600UL // On-board crystal (New mid-2010 Version)
#else
#define XTAL_FREQUENCY 12288000UL // On-board crystal (Original Version)
#endif

// See datasheet section 7.8 for configuring the
// "Programmable baud rate generator"
#define PRESCALER 1 // Default prescaler after reset
#define BAUD_RATE_DIVISOR(baud) ((XTAL_FREQUENCY/PRESCALER)/(baud*16UL))

#endif /* __SC16IS750_H__ */
