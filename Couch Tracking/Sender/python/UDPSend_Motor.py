import socket
import struct
 

UDP_IP = "192.168.8.2"
UDP_PORT = 1400
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
print("Enter depths: ")
while True:
    line = input()
    if line == 'q':
        break
    try:
        depth = float(line)
        value = int(depth * 100)
 
        # Convert the depth value to a 64-bit unsigned integer (UInt64 in C#)
        val = struct.pack('<Q', value)  # Little-endian byte order
 
        # Construct the byte array to send over UDP
        byteArray = b't' + val
 
        # Pad the byte array with zeros to make it 9 bytes long
        byteArray += b'\x00' * (9 - len(byteArray))
 
        sock.sendto(byteArray, (UDP_IP, UDP_PORT))
    except ValueError:
        print("Invalid input! Please enter a valid depth value or 'q' to quit.")
 
sock.close()