import threading
import time
import queue
import socket
import logging

# Fixed UDP communication parameters
UDP_IP = "127.0.0.1"  # To be determined and changed when communicate with Pi
UDP_PORT_SEND = 5005   # Port to send data (Delay sent)
UDP_PORT_RECV = 5006   # Port to receive feedback (Feedback from couch algorithm)
BUFFER_SIZE = 1024     # Size for UDP receiving buffer

# Setup logging
logging.basicConfig(
    filename="motion_trace.log",  # Log file
    level=logging.INFO,            # Log level
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()

def read_motion_trace(file_path):
    """Reads a motion trace file and returns a list of (timestamp, position) tuples."""
    motion_trace = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:  # Ensure the line has timestamp and position
                timestamp, position = float(parts[0]), float(parts[1])
                motion_trace.append((timestamp, position))
    return motion_trace

class MotionTraceReader(threading.Thread):
    def __init__(self, motion_trace, feedback_queue, latency=2):
        super().__init__()
        self.motion_trace = motion_trace
        self.motion_timeinterval = 1  # Input motion trace interval
        self.feedback_queue = feedback_queue
        self.stop_event = threading.Event()
        self.latency = latency  # Added latency parameter
        self.cumulative_feedback = 0  # Tracks cumulative feedback
        self.ground_truth_index = 0  # Tracks current ground truth index
        self.start_time = None
        self.delayed_queue = queue.Queue()  # For delayed output loop

        # UDP sockets
        self.udp_socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket_recv.bind((UDP_IP, UDP_PORT_RECV))

    def run(self):
        logger.info("TRACKING started")
        self.start_time = time.time()

        # Start threads for delayed output and UDP receiver
        delayed_output_thread = threading.Thread(target=self.delayed_output_loop, daemon=True)
        udp_receive_thread = threading.Thread(target=self.udp_receiver_loop, daemon=True)
        delayed_output_thread.start()
        udp_receive_thread.start()

        # Main loop: Process ground truth positions
        while self.ground_truth_index < len(self.motion_trace) and not self.stop_event.is_set():
            timestamp, original_position = self.motion_trace[self.ground_truth_index]
            logger.info(f"Starting: timestamp {timestamp}, position {original_position}")
            target_time = self.start_time + timestamp

            # Wait until the target timestamp
            current_time = time.time()
            if current_time < target_time:
                time.sleep(target_time - current_time)

            # Check for feedback and update cumulative feedback
            try:
                feedback = self.feedback_queue.get_nowait()
                logger.info(f"Received feedback {feedback}")
                self.cumulative_feedback += feedback
                logger.info(f"Reader: Cumulative feedback {self.cumulative_feedback}")
            except queue.Empty:
                pass

            # Update position based on cumulative feedback
            adjusted_position = original_position + self.cumulative_feedback
            logger.info(f"Updated ground truth: timestamp {timestamp}, adjusted position {adjusted_position}")

            # Add the adjusted position and timestamp to the delayed queue
            self.delayed_queue.put((timestamp, adjusted_position))

            # Move to the next ground truth index
            self.ground_truth_index += 1

        # Signal the delayed loop to stop
        self.delayed_queue.put(None)

    def delayed_output_loop(self):
        logger.info("Delayed output loop started")
        while not self.stop_event.is_set():
            try:
                data = self.delayed_queue.get(timeout=0.1)
                if data is None:  # End signal
                    break

                timestamp, adjusted_position = data

                # Calculate the target send time based on the original timestamp and latency
                target_time = self.start_time + timestamp + self.latency

                # Sleep until the target time
                current_time = time.time()
                if current_time < target_time:
                    time.sleep(target_time - current_time)

                # Send the adjusted position via UDP
                message = f"{timestamp},{adjusted_position}"
                self.udp_socket_send.sendto(message.encode(), (UDP_IP, UDP_PORT_SEND))

                # Compute the delayed timestamp
                delayed_timestamp = time.time() - self.start_time
                logger.info(f"Delayed output sent: timestamp {timestamp}, delayed timestamp {delayed_timestamp}, adjusted position {adjusted_position}")

            except queue.Empty:
                continue

    def udp_receiver_loop(self):
        logger.info("UDP receiver loop started")
        while not self.stop_event.is_set():
            try:
                data, addr = self.udp_socket_recv.recvfrom(BUFFER_SIZE)
                feedback = float(data.decode())
                logger.info(f"UDP RECEIVER: Received feedback {feedback} from {addr}")
                self.feedback_queue.put(feedback)
            except Exception as e:
                logger.error(f"UDP RECEIVER: Error {e}")

    def stop(self):
        self.stop_event.set()
        self.udp_socket_send.close()
        self.udp_socket_recv.close()

if __name__ == "__main__":
    # Path to motion trace file
    motion_trace_file = "motion_trace.txt"

    # Read motion trace from file
    motion_trace = read_motion_trace(motion_trace_file)

    # Create a shared queue for feedback communication
    feedback_queue = queue.Queue()

    # Initialize and start the motion trace reader thread
    reader_thread = MotionTraceReader(motion_trace, feedback_queue)
    reader_thread.start()

    try:
        reader_thread.join()  # Wait for the reader to finish
        logger.info("All threads finished.")
    except KeyboardInterrupt:
        logger.info("Stopping threads...")
        reader_thread.stop()
        reader_thread.join()
        logger.info("Threads stopped.")
