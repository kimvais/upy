# Copyright 2020 Kimmo Parviainen-Jalanko

import json
import socket
import struct
import time

import ds18x20
import machine
import network
import ntptime
import onewire

from nodemcu_gpio import *
from nodemcu_gpio_lcd import GpioLcd

NaN = float('nan')
MIN_OFFSET = 0
HOUR_OFFSET = 2


class Periodic:
    def __init__(self, rt, f, interval):
        self.rt = rt
        self.f = f
        self.interval = interval
        self.rt.periodics.add(self)

    def __call__(self):
        if self.rt.count % self.interval == 0:
            self.f()


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
        self.periodics = set()

    def startup(self, delay=10):
        self.delay = delay
        self.lcd.clear()
        self.lcd.putstr("...starting\n{}".format(self.machine_id))
        self.wlan = network.WLAN(network.STA_IF)
        while True:
            if self.wlan.ifconfig()[0] != "0.0.0.0":
                break
            print("Waiting to get IP address")
            time.sleep(1)
        while True:
            try:
                ntptime.settime()
                break
            except OSError as e:
                print("NTP failed with {}".format(e))
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

    def run(self):
        while True:
            self()
            time.sleep_ms(self.delay * 1000 - 750)

    def __call__(self):
        self.ip_addr = self.wlan.ifconfig()[0]
        temps = self.get_temps()
        cycle_messages = [self.ip_addr, self.machine_id]
        temperature = temps[0][1]
        dt = self.rtc.datetime()
        h = dt[4] + HOUR_OFFSET
        m = dt[5] + MIN_OFFSET
        try:
            row1 = "{0:+6.1f}\xdfC   {1:02d}:{2:02d}".format(temperature, h, m)
        except ValueError:
            row1 = "No 1-Wire! {0:02d}:{1:02d}".format(h, m)
        row2 = cycle_messages[self.count % len(cycle_messages)]
        self.send_temperatures(temps)
        self.lcd.clear()
        self.lcd.putstr(row1 + row2)
        self.count += 1

    def get_temps(self):
        try:
            temps = list(self.read_temps())
        except:
            temps = ('0' * 16, NaN)
        return temps

    def send_temperatures(self, temperatures):
        data = json.dumps(dict(temps=temperatures, node=self.machine_id, n=self.count))
        print(data)
        self.send(data.encode('utf-8'))

    def send(self, payload):
        self.sock.sendto(payload, (b"172.17.2.75", 54724))


RUNTIME = RunTime()


def main():
    RUNTIME.startup(30)
    Periodic(RUNTIME, ntptime.settime, 20)
    RUNTIME.run()


if __name__ == '__main__':
    main()
