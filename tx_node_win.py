import time
import sys
import serial
import msvcrt
from datetime import datetime

class sx126x:
    cfg_reg = [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x12, 0x43, 0x00, 0x00]
    get_reg = bytes(12)
    rssi = False
    addr = 100
    serial_n = ""
    addr_temp = 0
    start_freq = 433
    offset_freq = 23

    SX126X_PACKAGE_SIZE_240_BYTE = 0x00
    SX126X_PACKAGE_SIZE_128_BYTE = 0x40
    SX126X_PACKAGE_SIZE_64_BYTE = 0x80
    SX126X_PACKAGE_SIZE_32_BYTE = 0xC0

    SX126X_Power_22dBm = 0x00
    SX126X_Power_17dBm = 0x01
    SX126X_Power_13dBm = 0x02
    SX126X_Power_10dBm = 0x03

    lora_air_speed_dic = {
        1200: 0x01,
        2400: 0x02,
        4800: 0x03,
        9600: 0x04,
        19200: 0x05,
        38400: 0x06,
        62500: 0x07
    }

    lora_power_dic = {
        22: 0x00,
        17: 0x01,
        13: 0x02,
        10: 0x03
    }

    lora_buffer_size_dic = {
        240: SX126X_PACKAGE_SIZE_240_BYTE,
        128: SX126X_PACKAGE_SIZE_128_BYTE,
        64: SX126X_PACKAGE_SIZE_64_BYTE,
        32: SX126X_PACKAGE_SIZE_32_BYTE
    }

    def __init__(self, serial_num, freq, addr, power, rssi, air_speed=2400,
                 net_id=0, buffer_size=240, crypt=0, relay=False, lbt=False, wor=False):
        self.rssi = rssi
        self.addr = addr
        self.freq = freq
        self.serial_n = serial_num
        self.power = power
        self.ser = serial.Serial(serial_num, 9600)
        self.ser.flushInput()

    def send(self, data):
        self.ser.write(data)
        time.sleep(0.1)

    def receive(self):
        if self.ser.inWaiting() > 0:
            time.sleep(0.5)
            r_buff = self.ser.read(self.ser.inWaiting())
            print("From addr %d at %d.125MHz" % ((r_buff[0] << 8) + r_buff[1], r_buff[2] + self.start_freq))
            print("Message: " + str(r_buff[3:-1]))
            if self.rssi:
                print("Packet RSSI: -{0} dBm".format(256 - r_buff[-1:][0]))
                self.get_channel_rssi()
            print()  

    def get_channel_rssi(self):
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.write(bytes([0xC0, 0xC1, 0xC2, 0xC3, 0x00, 0x02]))
        time.sleep(0.5)
        if self.ser.inWaiting() > 0:
            re_temp = self.ser.read(self.ser.inWaiting())
            if re_temp[0] == 0xC1 and re_temp[1] == 0x00 and re_temp[2] == 0x02:
                print("Channel RSSI: -{0} dBm".format(256 - re_temp[3]))
            else:
                print("Failed to get channel RSSI")

    def free_serial(self):
        self.ser.close()


node = sx126x(serial_num="COM3", freq=433, addr=100, power=22, rssi=True)

def send_loop():
    print("Input in format: <dest_addr>,<message>,<delay_ms>")
    try:
        user_input = input("Enter and press Enter: ")
        dest_addr_str, message, delay_ms = user_input.strip().split(",", 2)
        dest_addr = int(dest_addr_str.strip())
        message = message.strip()
        delay = int(delay_ms.strip()) / 1000.0
    except ValueError:
        print("Invalid input. Format should be: <dest_addr>,<message>,<delay_ms>")
        return

    try:
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"[tx_time:{timestamp}] from:{node.addr} to:{dest_addr} msg:{message}"
            data = (
                bytes([dest_addr >> 8]) +
                bytes([dest_addr & 0xFF]) +
                bytes([node.offset_freq]) +
                bytes([node.addr >> 8]) +
                bytes([node.addr & 0xFF]) +
                bytes([node.offset_freq]) +
                full_message.encode()
            )
            node.send(data)
            print("Sent:", full_message)
            print()  
            time.sleep(delay)
    except KeyboardInterrupt:
        print("Stopped sending.")

try:
    print("Press Ctrl+C to exit")
    while True:
        send_loop()
        node.receive()
except KeyboardInterrupt:
    print("Exiting...")
    node.free_serial()
