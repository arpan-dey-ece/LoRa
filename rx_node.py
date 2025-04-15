import time
import serial
from datetime import datetime

class sx126x:
    cfg_reg = [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x12, 0x43, 0x00, 0x00]
    get_reg = bytes(12)
    rssi = False
    addr = 101  
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

    def __init__(self, serial_num, freq, addr, power, rssi=False, air_speed=2400,
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
        while True:
            if self.ser.inWaiting() > 0:
                time.sleep(0.5)
                r_buff = self.ser.read(self.ser.inWaiting())
                # Raw Data
                # print(f"Received raw data: {r_buff.hex()}")  
                
                # Check for valid message length
                if len(r_buff) >= 7:
                    src_addr = (r_buff[3] << 8) + r_buff[4]
                    dest_addr = (r_buff[0] << 8) + r_buff[1]
                    msg_end_index = len(r_buff)  
                    msg = r_buff[6:msg_end_index].decode(errors="ignore")  
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] From:{src_addr} To:{dest_addr}")
                    print("Message:", msg)
                    print()  
                else:
                    print("Received incomplete or malformed data.\n")
            else:
                time.sleep(0.1)

    def free_serial(self):
        self.ser.close()


node = sx126x(serial_num="COM4", freq=433, addr=101, power=22, rssi=False)

try:
    print("Receiver ready. Press Ctrl+C to exit.")
    node.receive()  # Start receiving loop
except KeyboardInterrupt:
    print("Exiting...")
    node.free_serial()
