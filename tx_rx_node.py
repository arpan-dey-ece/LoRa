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


def get_com_port_input():
    port_input = input("Enter COM port (e.g., 3 for COM3): ").strip()
    com_port = f"COM{port_input}"
    return com_port


def get_user_input_for_tx_or_rx():
    mode = input("Enter mode (tx / rx): ").strip().lower()
    if mode not in ['tx', 'rx']:
        print("Invalid mode. Please enter either 'tx' or 'rx'.")
        return get_user_input_for_tx_or_rx()
    return mode


def main():
    while True:
        mode = get_user_input_for_tx_or_rx()

        if mode == 'tx':
            addr = int(input("Enter your node address (e.g., 100): "))
            other_addr = int(input("Enter other node address (e.g., 101): "))
            com_port = get_com_port_input()
            message = input("Enter message to send: ").strip()

            node = sx126x(serial_num=com_port, freq=433, addr=addr, power=22, rssi=False)

            try:
                while True:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    full_message = f"[tx_time:{timestamp}] from:{node.addr} to:{other_addr} msg:{message}"
                    data = (
                        bytes([other_addr >> 8]) +
                        bytes([other_addr & 0xFF]) +
                        bytes([node.offset_freq]) +
                        bytes([node.addr >> 8]) +
                        bytes([node.addr & 0xFF]) +
                        bytes([node.offset_freq]) +
                        full_message.encode()
                    )
                    node.send(data)
                    print(f"Sent to {other_addr}: {full_message}")
                    print()  # Add space after each iteration
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Exiting transmitter.")
                node.free_serial()

        elif mode == 'rx':
            addr = int(input("Enter your node address (e.g., 101): "))
            other_addr = int(input("Enter other node address (e.g., 100): "))
            com_port = get_com_port_input()

            node = sx126x(serial_num=com_port, freq=433, addr=addr, power=22, rssi=False)

            try:
                print(f"Receiver ready. Press Ctrl+C to exit.")
                while True:
                    if node.ser.inWaiting() > 0:
                        time.sleep(0.5)
                        r_buff = node.ser.read(node.ser.inWaiting())
                        if len(r_buff) >= 7:
                            src_addr = (r_buff[3] << 8) + r_buff[4]
                            dest_addr = (r_buff[0] << 8) + r_buff[1]
                            if dest_addr == node.addr:  # Only process if destination matches
                                msg_end_index = len(r_buff)
                                msg = r_buff[6:msg_end_index].decode(errors="ignore")
                                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                print(f"[{timestamp}] From:{src_addr} To:{dest_addr}")
                                print("Message:", msg)
                                print()
                            else:
                                print(f"Ignored message from {src_addr} to {dest_addr}.")
                        else:
                            print("Received incomplete or malformed data.\n")
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Exiting receiver.")
                node.free_serial()

        # Ask if the user wants to switch mode after completing the current task
        switch_mode = input("Do you want to switch mode (tx / rx)? (yes / no): ").strip().lower()
        if switch_mode == 'yes':
            print(f"Switching to { 'tx' if mode == 'rx' else 'rx' } mode...\n")
            continue  # Loop back to choose the new mode
        else:
            print("Exiting program.")
            break


if __name__ == "__main__":
    main()
