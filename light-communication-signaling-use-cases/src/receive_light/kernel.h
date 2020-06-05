#ifndef RELEASE_KERNEL_H_
#define RELEASE_KERNEL_H_

#define ADDR_BASE_0 0x44e07000
#define ADDR_BASE_1 0x4804c000
#define READ_OFFSET 0x138
#define SET_OFFSET 0x194
#define CLEAR_OFFSET 0x190
#define BIT_MISO (23)
#define SPI_DELAY_CNT 10

#define GPIO_LED_ANODE 60
#define GPIO_LED_CATHODE 50
#define GPIO_BUFFER_CONTROL 51
#define GPIO_LED_OR_PD 2 // Choose between PD and LED
#define GPIO_H_POWER_LED 49 // Output of high power LED

#define SPI_CLC 45
#define SPI_MISO 23
#define SPI_MOSI 47
#define SPI_CS 27

#define BIT_CLC (45-32) // 32+13 P8_11
#define BIT_MOSI (47-32) // 32+15 P8_15
#define BIT_CS (27) // 0+27 P8_17

#define CONVERT_SENSING_INTERVAL 1000

#endif
