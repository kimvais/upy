#  This file is executed on every boot (including wake-boot from deepsleep)


#  import esp
#  esp.osdebug(None)
#  uos.dupterm(None, 1) #   disable REPL on UART(0)
#  import webrepl
#  webrepl.start()
#  import network
#  wlan = network.WLAN(network.STA_IF)
#  wlan.active(True)
import gc

gc.collect()
