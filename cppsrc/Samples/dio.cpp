#include "dio.h"
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/types.h>
#include <linux/spi/spidev.h>
#include <sys/stat.h>
#include <sys/types.h>


std::string dio::hello(){
    return "Hello World";
}

int dio::add(int a, int b){
  return a + b;
}


Napi::String dio::HelloWrapped(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::String returnValue = Napi::String::New(env, dio::hello());
    return returnValue;
}

Napi::Number dio::ChannelWrapped(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    if (info.Length() < 2 || !info[0].IsNumber() || !info[1].IsNumber()) {
        Napi::TypeError::New(env, "Number expected").ThrowAsJavaScriptException();
    } 

    Napi::Number first = info[0].As<Napi::Number>();
    Napi::Number second = info[1].As<Napi::Number>();

    int returnValue = dio::channel(first.Int32Value(), second.Int32Value());
    
    return Napi::Number::New(env, returnValue);
}

Napi::Number dio::AddWrapped(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    if (info.Length() < 2 || !info[0].IsNumber() || !info[1].IsNumber()) {
        Napi::TypeError::New(env, "Number expected").ThrowAsJavaScriptException();
    } 

    Napi::Number first = info[0].As<Napi::Number>();
    Napi::Number second = info[1].As<Napi::Number>();

    int returnValue = dio::add(first.Int32Value(), second.Int32Value());
    
    return Napi::Number::New(env, returnValue);
}

Napi::Object dio::Init(Napi::Env env, Napi::Object exports) {
    exports.Set("hello", Napi::Function::New(env, dio::HelloWrapped));
    exports.Set("add", Napi::Function::New(env, dio::AddWrapped));
    exports.Set("channel", Napi::Function::New(env, dio::ChannelWrapped));
    return exports;
}
static uint8_t x = 16;
static uint8_t y = 16;
static const char *device = "/dev/spidev0.0";
static uint8_t mode = 0;
static uint8_t bits = 8;
static uint32_t speed = 20000;
static uint16_t ddelay = 0;
static void pabort(const char *s)
{
	perror(s);
	abort();
}


static void transfer(int fd, int a, int b)
{
	int ret;
	uint8_t tx[32] = {0, };
	x = a;
	y = b;
        int ydim;
	for (ydim = 0; ydim < 16; ydim++) {
            if(ydim == 15 - y) {
		if(x == 0) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b00000001;
		}
		if(x == 1) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b00000010;
		}
		if(x == 2) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b00000100;
		}
		if(x == 3) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b00001000;
		}
		if(x == 4) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b00010000;
		}
		if(x == 5) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b00100000;
		}
		if(x == 6) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b01000000;
		}
		if(x == 7) {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b10000000;
		}
		if(x == 8) {
		    tx[ydim * 2]     = 0b00000001;
		    tx[ydim * 2 + 1]     = 0b00000000;
		}
		if(x == 9) {
		    tx[ydim * 2]     = 0b00000010;
		    tx[ydim * 2 + 1]     = 0b00000000;
		}
		if(x == 10) {
		    tx[ydim * 2]     = 0b00000100;
		    tx[ydim * 2 + 1]     = 0b00000000;
		}
		if(x == 11) {
		    tx[ydim * 2]     = 0b00001000;
		    tx[ydim * 2 + 1]     = 0b00000000;
		}
		if(x == 12) {
		    tx[ydim * 2]     = 0b00010000;
		    tx[ydim * 2 + 1]     = 0b00000000;
		}
		if(x == 13) {
		    tx[ydim * 2]     = 0b00100000;
		    tx[ydim * 2 + 1]     = 0b00000000;
		}
		if(x == 14) {
		    tx[ydim * 2]     = 0b01000000;
		    tx[ydim * 2 + 1] = 0b00000000;
		}
		if(x == 15) {
		    tx[ydim * 2]      = 0b10000000;
		    tx[ydim * 2 + 1]  = 0b00000000;
		}




	    } else {
		    tx[ydim * 2]     = 0b00000000;
		    tx[ydim * 2 + 1]     = 0b00000000;

            }
	}

	uint8_t rx[32] = {0, };
	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)rx,
		.len = 32,
		.speed_hz = speed,
		.delay_usecs = ddelay,
		.bits_per_word = bits,
	};

	ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
	if (ret < 1)
		pabort("can't send spi message");

	for (ret = 0; ret < 32; ret++) {
		if (!(ret % 2))
			puts("");
		printf("%.2X ", tx[ret]);
	}
	for (ret = 0; ret < 32; ret++) {
		if (!(ret % 2))
			puts("");
		printf("%.2X ", rx[ret]);
	}
	puts("");
}

int dio::channel(int a, int b){
	int ret = 0;
	int fd;

	fd = open(device, O_RDWR);
	if (fd < 0)
		pabort("can't open device");

	/*
	 * spi mode
	 */
	ret = ioctl(fd, SPI_IOC_WR_MODE, &mode);
	if (ret == -1)
		pabort("can't set spi mode");

	ret = ioctl(fd, SPI_IOC_RD_MODE, &mode);
	if (ret == -1)
		pabort("can't get spi mode");

	/*
	 * bits per word
	 */
	ret = ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits);
	if (ret == -1)
		pabort("can't set bits per word");

	ret = ioctl(fd, SPI_IOC_RD_BITS_PER_WORD, &bits);
	if (ret == -1)
		pabort("can't get bits per word");

	/*
	 * max speed hz
	 */
	ret = ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed);
	if (ret == -1)
		pabort("can't set max speed hz");

	ret = ioctl(fd, SPI_IOC_RD_MAX_SPEED_HZ, &speed);
	if (ret == -1)
		pabort("can't get max speed hz");

	printf("spi mode: %d\n", mode);
	printf("bits per word: %d\n", bits);
	printf("max speed: %d Hz (%d KHz)\n", speed, speed/1000);

	transfer(fd,a,b);
	close(fd);
	return ret;
}

