import struct
import time

import ds18x20
import machine
import network
import onewire

from nodemcu_gpio import *
from nodemcu_gpio_lcd import GpioLcd

wlan = network.WLAN(network.STA_IF)


class RunTime:
    def __init__(self):
        _machine_id = machine.unique_id()
        self.machine_id = struct.unpack("I", _machine_id)[0]
        self.ow = onewire.OneWire(Pin(13))
        self.ds = ds18x20.DS18X20(self.ow)
        self.lcd = GpioLcd(d6, d5, d4, d3, d2, d1)

    def read_temps(self):
        self.ds.convert_temp()
        time.sleep_ms(750)
        for rom in self.ds.scan():
            yield self.ds.read_temp(rom)

    def run(self, delay=5):
        while True:
            self.update()
            time.sleep_ms(delay * 1000 - 750)

    def update(self):
        ip_addr = wlan.ifconfig()[0]
        try:
            temps = list(self.read_temps())
            temp = temps[0]
        except:
            print("Can't read temperature!")
            temp = -99.9
        self.lcd.clear()
        # self.lcd.putstr("{0:.1f}\xdfC {1:08x}\n{2}".format(temp, self.machine_id, ip_addr))
        self.lcd.putstr("{0:+5.1f}\xdfC {1:08x}{2}".format(temp, self.machine_id, ip_addr))


rt = RunTime()
rt.update()


def main():
    rt.run(10)


if __name__ == '__main__':
    main()
