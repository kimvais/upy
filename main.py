import struct
import time

import machine
from nodemcu_gpio_lcd import GpioLcd

from nodemcu_gpio import *

def main():
    adc = machine.ADC(0)
    _machine_id = machine.unique_id()
    machine_id = struct.unpack("I", _machine_id)[0]
    lcd = GpioLcd(d5, d6, d4, d0, d2, d1)

    while True:
        temp = adc.read() / 1024.0 * 330
        lcd.clear()
        lcd.putstr("{0:.1f}\xdfC\nID: {1:08x}".format(temp, machine_id))
        time.sleep(5)


if __name__ == '__main__':
    main()
