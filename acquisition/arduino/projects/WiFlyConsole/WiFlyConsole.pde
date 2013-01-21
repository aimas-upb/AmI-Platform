/*
 * WiFlyConsole.pde -- utility for connecting to WiFly board and doing initial configuration
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#include "WiFlyHigh.h"

#define UART_BAUDRATE         115200

#define DEFAULT_BAUD_RATE     0
#define DEFAULT_AUTO_COMMAND  true

/* baud rates supported by WiFly; we don't care about baud rates lower than 9600 */
static const unsigned long baudRates[] = { 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600 };
#define NBAUDRATES (sizeof(baudRates) / sizeof(baudRates[0]))

static unsigned long selectedBaudRate = DEFAULT_BAUD_RATE;
static boolean autoCommandMode = DEFAULT_AUTO_COMMAND;


static void configure()
{
    uint8_t c, i, done;

    pinMode(13, OUTPUT);
    digitalWrite(13, HIGH);

    Serial.begin(UART_BAUDRATE);

    while (!Serial.available()) ;

    Serial.println("Welcome to WiFlyConsole. <enter> to continue, h for help.");

    for (done = 0; done < 2; ) {
        while (!Serial.available()) ;
        c = Serial.read();
        switch (c) {
        case 'h':
            Serial.println("h\t- show this help");
            Serial.print("c\t- toggle auto command mode (default: ");
            Serial.print(DEFAULT_AUTO_COMMAND ? "ON" : "OFF");
            Serial.println(")");
            for (i = 0; i < sizeof(baudRates) / sizeof(baudRates[0]); i++) {
                Serial.print(i, DEC);
                Serial.print("\t- select WiFly baud rate: ");
                Serial.print(baudRates[i], DEC);
                if (i == DEFAULT_BAUD_RATE)
                    Serial.print(" (default)");
                Serial.println();
            }
            Serial.println("<enter>\t- finish configuration");
            break;
        case 'c':
            autoCommandMode = !autoCommandMode;
            Serial.print("Auto command mode: ");
            Serial.println(autoCommandMode ? "ON" : "OFF");
            break;
        case '\r':
            if (Serial.peek() == '\n')
                Serial.read();
        case '\n':
            done++;
            break;
        default:
            if (c >= '0' && c < '0' + NBAUDRATES) {
                selectedBaudRate = baudRates[c - '0'];
                Serial.print("Selected WiFly baud rate: ");
                Serial.println(selectedBaudRate, DEC);
                break;
            }
            Serial.println("Unknown command. Use h for help.\n");
            break;
        }
    }

    Serial.println("Done configuration.");

    digitalWrite(13, LOW);
}

static void UARTOnSPI_interrupt()
{
    uartWiFly.interrupt();
}

void setup()
{
    configure();

    if (!WiFly.begin(selectedBaudRate)) {
        Serial.println("WiFly link init failed.");
        return;
    }

    Serial.println("WiFly link initialized.");

    attachInterrupt(2, UARTOnSPI_interrupt, FALLING);
    WiFly.hardwareReset();
    delay(1000);

    if (autoCommandMode) {
        Serial.println("Entering command mode...");
        WiFly.enterCommandMode();
        delay(1000);
    }
}

void loop()
{
    uartWiFly.processInterrupts();
    while (uartWiFly.available())
        Serial.write(uartWiFly.read());
    while (Serial.available())
        uartWiFly.write(Serial.read());
}
