
# 📡 SX1268 LoRa Communication Experiment

This repository contains a Python-based setup to demonstrate long-range wireless data transmission using **SX1268 433 MHz LoRa HAT** modules. The setup uses two Python scripts: one for transmitting messages (`tx_node.py`) and another for receiving them (`rx_node.py`) via serial communication.

Messages are exchanged over a **433 MHz** channel using user-defined parameters like **COM ports**, **node addresses**, **transmission power**, and **delay intervals**.

---

## 📌 Notes

- **Default frequency:** 433 MHz  
- **Default baud rate:** 9600  
- **Default LoRa air speed:** 2400 bps  
- **Example addressing:**
  - TX Node: `100`
  - RX Node: `101`

---

## 🛠️ Hardware Used

- 2× SX1268 433M LoRa HAT modules  
- USB-to-Serial cables  
- PC or laptop running Python 3.x  

---

## 📁 File Descriptions

- **`tx_node.py`** – Script for sending messages to a specified destination node.
- **`rx_node.py`** – Script for continuously listening and printing received messages with timestamps and address info.

---

## 🧾 Message Format

Each transmitted message includes:

- Source and destination addresses  
- Frequency offset  
- Timestamped payload message  

Example:
```
[tx_time:2025-04-16 12:30:00] from:100 to:101 msg:Hello Receiver
```

---

## 🔧 Tunable Parameters

These parameters can be modified inside each script:

| Parameter     | Location                   | Default Value     | Description                                                  |
|---------------|----------------------------|-------------------|--------------------------------------------------------------|
| `serial_num`  | `tx_node.py` / `rx_node.py` | `"COM3"` / `"COM4"` | COM port used for TX and RX respectively *(tunable)*         |
| `addr`        | `tx_node.py` / `rx_node.py` | `100` / `101`       | Node address of TX and RX *(tunable)*                        |
| `power`       | Both scripts                | `22` dBm            | Transmission power *(tunable: 22, 17, 13, 10)*               |
| `air_speed`   | Both scripts                | `2400` bps          | LoRa air speed *(tunable: see dictionary in code)*           |
| `message`     | User input in `tx_node.py`  | N/A                 | Message content to send *(tunable)*                          |
| `delay_ms`    | User input in `tx_node.py`  | N/A                 | Delay between messages in milliseconds *(tunable)*           |

---

## ▶️ How to Run

1. Connect the LoRa modules to your PC via USB.
2. Update `serial_num`, `addr`, and other parameters as needed in both scripts.
3. Run `rx_node.py` to start the receiver.
4. Run `tx_node.py` and follow the prompt.  
   Example input:
   ```
   101,Hello Receiver,2000
   ```
   This sends the message to address `101` every `2 seconds`.

---

## 🧰 Dependencies

- Python 3.x  
- [`pyserial`](https://pypi.org/project/pyserial/) (`pip install pyserial`)  
- OS: **Windows** (due to `msvcrt` usage in `tx_node.py`)

---

## 🔗 Reference

For detailed technical specifications and hardware setup instructions, please refer to the official Waveshare documentation:  
📄 [Waveshare SX1268 433M LoRa HAT Wiki](https://www.waveshare.com/wiki/SX1268_433M_LoRa_HAT)
