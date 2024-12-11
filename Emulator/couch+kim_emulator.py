# KIM thread
# Measure and send
# Latency

# Couch thread
# Response accordingly and achieve compensation 
import threading
import time
import queue

'''
# Ground truth motion trace (timestamp in seconds, position in mm)
motion_trace = [
    (0.0, 0),
    (1.0, 2),
    (2.0, 4),
    (3.0, 6),
    (4.0, 8),
    (5.0, 10),
    (6.0, 12),
    (7.0, 14),
    (8.0, 16),
    (9.0, 18),
    (10.0, 20)
]

'''
# Ground truth motion trace (timestamp in seconds, position in mm)
motion_trace = [
    (0.0, 0),
    (1.0, 1),
    (2.0, 1),
    (3.0, 1),
    (4.0, 1),
    (5.0, 1),

]


class MotionTraceReader(threading.Thread):
    def __init__(self, motion_trace, output_queue, feedback_queue, latency=2):
        super().__init__()
        self.motion_trace = motion_trace
        self.motion_timeinterval = 1  # Input motion trace interval
        self.output_queue = output_queue
        self.feedback_queue = feedback_queue
        self.stop_event = threading.Event()
        self.latency = latency  # Added latency parameter
        self.cumulative_feedback = 0  # Tracks cumulative feedback
        self.ground_truth_index = 0  # Tracks current ground truth index
        self.start_time = None
        self.delayed_queue = queue.Queue()  # For delayed output loop

    def run(self):
        print("TRACKING started")
        self.start_time = time.time()

        # Start a separate thread for the delayed output loop
        delayed_output_thread = threading.Thread(target=self.delayed_output_loop, daemon=True)
        delayed_output_thread.start()

        # Main loop: Process ground truth positions
        while self.ground_truth_index < len(self.motion_trace) and not self.stop_event.is_set():
            timestamp, original_position = self.motion_trace[self.ground_truth_index]
            print(f"Starting: timestamp {timestamp}, position {original_position}")
            target_time = self.start_time + timestamp

            # Wait until the target timestamp
            current_time = time.time()
            if current_time < target_time:
                time.sleep(target_time - current_time)

            # Check for feedback and update cumulative feedback
            try:
                feedback = self.feedback_queue.get_nowait()
                print(f"Received feedback {feedback}")
                self.cumulative_feedback += feedback
                print(f"Reader: Cumulative feedback {self.cumulative_feedback}")
            except queue.Empty:
                pass

            # Update position based on cumulative feedback
            adjusted_position = original_position + self.cumulative_feedback
            print(f"Updated ground truth: timestamp {timestamp}, adjusted position {adjusted_position}")

            # Add the adjusted position and timestamp to the delayed queue
            self.delayed_queue.put((timestamp, adjusted_position))

            # Move to the next ground truth index
            self.ground_truth_index += 1

        # Signal the delayed loop to stop
        self.delayed_queue.put(None)




    def delayed_output_loop(self):
        print("  Delayed output loop started")
        
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

                # Compute the delayed timestamp
                delayed_timestamp = time.time() - self.start_time

                # Send the adjusted position to the processor thread
                self.output_queue.put((timestamp, adjusted_position))
                print(f"Delayed output sent: timestamp {timestamp}, delayed timestamp {delayed_timestamp}, adjusted position {adjusted_position}")

            except queue.Empty:
                continue

    def stop(self):
        self.stop_event.set()


# Thread to receive measurements and process them
class MeasurementProcessor(threading.Thread):
    def __init__(self, input_queue, feedback_queue):
        super().__init__()
        self.input_queue = input_queue
        self.feedback_queue = feedback_queue
        self.stop_event = threading.Event()
        self.isocenter = 0 
    def run(self):
        print(" COUCH started")
        while not self.stop_event.is_set():
            try:
                # Wait for data from the queue
                data = self.input_queue.get(timeout=0.1)
                if data is None:  # End of data
                    break
                timestamp, position = data
                if position != self.isocenter:
                    feedback = -(position - self.isocenter) # Motor moves in opposite direction to achieve compensation 
                    print(f"  COUCH: Processed time {timestamp}, position {position}, feedback {feedback}")
                    self.feedback_queue.put(feedback)
                # Process the measurement
                #modified_position = position - 1
                

                # Send feedback (relative adjustment)
               
                

            except queue.Empty:
                continue
    
    def stop(self):
        self.stop_event.set()

if __name__ == "__main__":
    # Create shared queues for communication between threads
    shared_queue = queue.Queue()
    feedback_queue = queue.Queue()

    # Initialize threads
    reader_thread = MotionTraceReader(motion_trace, shared_queue, feedback_queue)
    processor_thread = MeasurementProcessor(shared_queue, feedback_queue)

    # Start threads
    reader_thread.start()
    processor_thread.start()

    try:
        reader_thread.join()  # Wait for the reader to finish
        processor_thread.join()  # Wait for the processor to finish
        print("All threads finished.")
    except KeyboardInterrupt:
        print("Stopping threads...")
        reader_thread.stop()
        processor_thread.stop()
        reader_thread.join()
        processor_thread.join()
        print("Threads stopped.")
