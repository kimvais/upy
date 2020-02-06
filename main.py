# Copyright 2020 Kimmo Parviainen-Jalanko

import json
import socket
import struct
import time

import ds18x20
import machine
import network
import onewire

from nodemcu_gpio import *
from nodemcu_gpio_lcd import GpioLcd


class RunTime:
    def __init__(self):
        _machine_id = machine.unique_id()
        self.count = 0
        self.machine_id = '{2:0x}:{1:0x}:{0:0x}'.format(*_machine_id)
        self.ow = onewire.OneWire(d7)
        self.ds = ds18x20.DS18X20(self.ow)
        self.lcd = GpioLcd(d6, d5, d4, d3, d2, d1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.startup()

    def startup(self):
        self.wlan = network.WLAN(network.STA_IF)
        while True:
            if self.wlan.ifconfig()[0] != "0.0.0.0":
                break
            print("Waiting to get IP address")
            time.sleep(1)
        self.rtc = machine.RTC()

    def read_temps(self):
        self.ds.convert_temp()
        time.sleep_ms(750)
        for rom in self.ds.scan():
            value = self.ds.read_temp(rom)
            rom_id = '{0:x}'.format(*struct.unpack('!Q', rom))
            print("{0}: {1} C".format(rom_id, value))
            yield (rom_id, value)

    def run(self, delay=5):
        while True:
            self()
            time.sleep_ms(delay * 1000 - 750)

    def __call__(self):
        self.ip_addr = self.wlan.ifconfig()[0]
        temps = self.get_temps()
        cycle_messages = [self.ip_addr, self.machine_id]
        row1 = "{0:+6.1f}\xdfC\n".format(temps[0][1])
        row2 = cycle_messages[self.count % len(cycle_messages)]
        self.send_temperatures(temps)
        self.lcd.clear()
        self.lcd.putstr(row1 + row2)
        self.count += 1

    def get_temps(self):
        try:
            temps = list(self.read_temps())
        except:
            print("Can't read temperature!")
            temps = ('0' * 16, float('nan'))
        return temps

    def send_temperatures(self, temperatures):
        data = json.dumps(dict(temps=temperatures, node=self.machine_id, n=self.count))
        print(data)
        self.send(data.encode('utf-8'))

    def send(self, payload):
        self.sock.sendto(payload, (b"172.17.2.75", 54724))


RUNTIME = RunTime()


def main():
    RUNTIME.run(10)


if __name__ == '__main__':
    main()
