import socket
import time
import struct
 
# === CONFIGURATION ===
 
TRACE_FILE = "2.Medium_complexity_093_robot 1.txt"
LOCAL_IP = "0.0.0.0"            # Listen on all interfaces
LOCAL_PORT = 2400               # Fixed local port to receive feedback
TARGET_IP = "192.168.8.2"       # Raspberry Pi / C++ device
TARGET_PORT = 1400              # Port the C++ code listens on
 
# === SETUP SOCKET ===
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LOCAL_IP, LOCAL_PORT))
sock.settimeout(5.0)  # timeout for feedback receive
 
print(f"[PYTHON] Socket bound to {LOCAL_IP}:{LOCAL_PORT} for receive")
 
# === LOAD MOTION TRACE FILE ===
 
motion_data = []
 
with open(TRACE_FILE, "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) >= 3:
            timestamp = float(parts[0])
            y_position = float(parts[2])
            motion_data.append((timestamp, y_position))
 
# === MAIN SEND LOOP ===
 
start_time = time.time()
correction_total = 0.0
 
for idx, (timestamp, original_y) in enumerate(motion_data):
    # Wait until the real time catches up
    while time.time() - start_time < timestamp:
        time.sleep(0.001)
 
    # Apply correction
    corrected_y = original_y + correction_total
 
    # Send corrected Y value
    packed = struct.pack("d", corrected_y)
    sock.sendto(packed, (TARGET_IP, TARGET_PORT))
    print(f"[PYTHON] Sent Y = {corrected_y:.4f} (original: {original_y:.4f}) to {TARGET_IP}:{TARGET_PORT}")
 
    # Wait for feedback
    try:
        data, addr = sock.recvfrom(1024)
        if len(data) >= 8:
            feedback_val = struct.unpack("d", data[:8])[0]
            #print(f"[PYTHON] Raw feedback received from {addr}: {data}")
            print(f"[PYTHON] Feedback value received: {feedback_val:.4f}")
 
            # Apply feedback to future values
            correction_total += feedback_val
        else:
            print("[PYTHON] Incomplete feedback received")
    except socket.timeout:
        print("[PYTHON] No feedback received (timeout)")
 
# === CLEANUP ===
 
sock.close()
print("[PYTHON] Done.")
