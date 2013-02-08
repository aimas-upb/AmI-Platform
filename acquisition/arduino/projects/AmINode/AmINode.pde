/*
 * AmINode.pde -- controller for a single node in the AmI sensor network
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#include "WiFlyHigh.h"
#include "uthread.h"
#include "buffer.h"
#include "pins_arduino.h"

#define DEBUG           1

#if DEBUG
#define DBGPRINT        Serial.print
#define DBGPRINTLN      Serial.println
#else
#define DBGPRINT(...)   do { } while (0)
#define DBGPRINTLN(...) do { } while (0)
#endif

#define WIFLY_BAUD_RATE 921600

#define AUTO_COMMAND    0
#define AUTO_JOIN       0
#define AUTO_CONNECT    1

#define WLAN_SSID       ""
#define WLAN_KEY        ""
#define WLAN_IS_WPA     true

#define REMOTE_HOST     "141.85.37.140" /* ai-lab.cs.pub.ro */
#define REMOTE_PORT     4242

#define UART_BAUDRATE   115200

//#define MIC_SAMPLING_RATE  8000
#define MIC_BUFFER_SIZE    4000

static char cfg;
static struct ring_buffer *adcbuf;


SIGNAL(ADC_vect)
{
    uint8_t sample;

    sample = ADCH;
    analogWrite(2, sample);
    buffer_write(adcbuf, sample);
}

/*
SIGNAL(TIMER1_COMPB_vect)
{
}
*/

static void UARTOnSPI_interrupt()
{
    uartWiFly.interrupt();
}

static void interrupt_thread()
{
    DBGPRINTLN("Interrupt thread started.");

    while (1) {
        uartWiFly.processInterrupts();
        uthread_yield();
    }
}

static void wifly_debug_thread()
{
    DBGPRINTLN("WiFly debug thread started.");

    while (1) {
        while (uartWiFly.available())
            Serial.print(uartWiFly.read(), BYTE);
        uthread_yield();
    }
}

static void wifly_thread()
{
#if 0 /* terminal mode */
    while (1) {
        while (Serial.available())
            uartWiFly.print(Serial.read(), BYTE);
        uthread_yield();
    }
#elif 1 /* ADC data send mode over WiFly */
    uint8_t c;
    ADCSRA |= _BV(ADSC); // start conversion
    while (1) {
        while (buffer_read_atomic(adcbuf, &c))
            uartWiFly.writeBuffered(c);
        uthread_yield();
    }
#elif 0 /* ADC data send mode over serial */
    uint8_t c;
    ADCSRA |= _BV(ADSC); // start conversion
    while (1) {
        while (buffer_read_atomic(adcbuf, &c))
            Serial.write(c);
        uthread_yield();
    }
#elif 0 /* reliable send mode benchmark */
    uint8_t tmpbuf[256];
    memset(tmpbuf, 0x42, sizeof(tmpbuf));
    while (1) {
        uartWiFly.write(tmpbuf, 2);
        uthread_yield();
    }
#elif 0 /* blind send mode benchmark */
    uint8_t tmpbuf[256];
    memset(tmpbuf, 0x42, sizeof(tmpbuf));
    while (1) {
        uartWiFly.writeFast(tmpbuf, sizeof(tmpbuf));
        delay(2);
    }
#elif 0 /* loopback mode */
    while (1) {
        if (uartWiFly.available())
            uartWiFly.print(uartWiFly.read();, BYTE);
        uthread_yield();
    }
#else /* dummy mode */
    while (1) {
        uthread_yield();
    }
#endif
}

static void init_wifly()
{
    if (!WiFly.begin(WIFLY_BAUD_RATE)) {
        DBGPRINTLN("WiFly link init failed.");
        while (1) ;
    }

    DBGPRINTLN("WiFly link initialized.");

    uthread_create(interrupt_thread, 64, 0);
    uthread_create(wifly_debug_thread, 64, 0);

    attachInterrupt(2, UARTOnSPI_interrupt, FALLING);
    WiFly.hardwareReset();

    DBGPRINTLN("WiFly reset.");
    uthread_sleep(1000);

#if AUTO_COMMAND
    DBGPRINTLN("Entering command mode...");
    WiFly.enterCommandMode();
#endif

#if AUTO_JOIN
    DBGPRINT("Joining ");
    DBGPRINT(WLAN_SSID);
    DBGPRINTLN("...");
    WiFly.join(WLAN_SSID, WLAN_KEY, WLAN_IS_WPA);
#endif

#if AUTO_CONNECT
    uthread_sleep(5000);
    DBGPRINT("Connecting to ");
    DBGPRINT(REMOTE_HOST);
    DBGPRINT(":");
    DBGPRINT(REMOTE_PORT, DEC);
    DBGPRINTLN("...");
    WiFly.connect(REMOTE_HOST, REMOTE_PORT);
    uthread_sleep(3000);
#endif
}

void setup()
{
    pinMode(13, OUTPUT);
    digitalWrite(13, HIGH);

    Serial.begin(UART_BAUDRATE);
    while (!Serial.available()) ;
    cfg = Serial.read();
    if (Serial.peek() == '\n')
        Serial.read();

    digitalWrite(13, LOW);

    adcbuf = buffer_alloc(MIC_BUFFER_SIZE);

    ADMUX = _BV(REFS0) | _BV(ADLAR); // ADC left adjust result, mux to ADC0
    ADCSRA = _BV(ADEN) | _BV(ADATE) | _BV(ADIE) |  // enable ADC, auto-trigger, interrupt
//    ADCSRA = _BV(ADEN) | _BV(ADATE) | _BV(ADIE) |  // enable ADC, interrupt
//             _BV(ADPS2) | _BV(ADPS0); // prescaler 32
//             _BV(ADPS2) | _BV(ADPS1); // prescaler 64
             _BV(ADPS2) | _BV(ADPS1) | _BV(ADPS0); // prescaler 128
    ADCSRB = 0; // free running mode

    /*
    unsigned int divisor = F_CPU / 8 / MIC_SAMPLING_RATE; // 250 for 8000 Hz
    DBGPRINTLN(divisor);
    OCR1BH = highByte(divisor);
    OCR1BL = lowByte(divisor);
    TCCR1A = _BV(WGM12); // CTC (clear timer on compare match) mode
    TCCR1B = _BV(CS11); // clkIO / 8 prescaler
    TIMSK1 = _BV(OCIE1B); // enable output compare match B interrupt
    */

    /*
    TCCR3A = _BV(COM3B1) | _BV(WGM31) | _BV(WGM30);
    TCCR3B = _BV(WGM32)| _BV(CS30);
    DDRE |= _BV(DDE4);
    */

    init_wifly();

    uthread_create(wifly_thread, 256, 0);
}

void loop()
{
    uthread_yield();
}
