import argparse
import socket
import time
import struct
import threading
import numpy as np
import matplotlib.pyplot as plt
import os


def _read_raw_trace(trace_file):
    """Load 2-col [t, y] or 7-col [t, *, y, ...] into (t, y), sorted by t."""
    times = []
    vals = []
    with open(trace_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) == 2:
                t, y = float(parts[0]), float(parts[1])
                times.append(t); vals.append(y)
            elif len(parts) == 7:
                t, y = float(parts[0]), float(parts[2])
                times.append(t); vals.append(y)
            else:
                # ignore malformed rows; or raise if you prefer strict
                continue
    t = np.asarray(times, dtype=float)
    y = np.asarray(vals, dtype=float)
    # ensure strictly increasing time (sort if needed)
    order = np.argsort(t)
    return t[order], y[order]

def _resample_trace(t_in, y_in, dt):
    """Linear resample to uniform grid with step=dt (seconds)."""
    if dt is None or dt <= 0:
        return t_in, y_in  # no change
    t0 = float(t_in[0])
    t1 = float(t_in[-1])
    # include the final point (avoid floating error with a small epsilon)
    t_out = np.arange(t0, t1 + 1e-12, dt, dtype=float)
    # numpy.interp does linear interpolation; outside bounds uses endpoints
    y_out = np.interp(t_out, t_in, y_in)
    return t_out, y_out



class MotionCompensationSimulator:
    def __init__(self, trace_file, latency=1.0,
                 local_ip="0.0.0.0", local_port=2400, target_ip="192.168.8.2", target_port=1400,
                 log_file="simulation_log.txt", track_dt = None): # Motion trace, latency, UDP IP address x3, UDP port number, log file name, tracking timestamp interval
        
       
        self.trace_name = os.path.basename(trace_file)
        self.motor_velocity = None  # will be set by __main__ for local mode

        raw_t, raw_y = _read_raw_trace(trace_file)
        res_t, res_y = _resample_trace(raw_t, raw_y, track_dt)


 
        self.timestamps = res_t
        self.true_motion = res_y
 
        # Simulation parameters
        self.latency = latency  # In seconds
        self.cumulative_feedback = 0.0

        # UDP communication 
        # Define the IP address and Port number 
        self.local_ip = local_ip
        self.local_port = local_port
        self.target_ip = target_ip
        self.target_port = target_port
 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, self.local_port))
        self.sock.settimeout(1.0)
 
        # Logging
        self.log_file_path = log_file
        self.feedback_log_path = self.log_file_path.replace("simulation_log", "feedback_log")
        self.log_lines = []
 
        # Shared feedback state
        self.feedback_queue = []  # stores (recv_time, value)
        self.feedback_applied = [0.0 for _ in self.timestamps]
        self.feedback_lock = threading.Lock()
        self.stop_flag = threading.Event()

    def feedback_listener(self):
        while not self.stop_flag.is_set():
            try:
                data, addr = self.sock.recvfrom(1024)
            except socket.timeout:
                continue
            except OSError:
                # Socket was closed during shutdown; exit quietly
                break

            if not data or len(data) < 8:
                continue

            try:
                feedback_val = struct.unpack("d", data[:8])[0]
            except struct.error:
                continue

            recv_time = time.time() - self.start_time

            with self.feedback_lock:
                self.feedback_queue.append((recv_time, feedback_val))

            # If you don't want to log 0.0 busy acks, uncomment the next line.
            # if abs(feedback_val) < 1e-12: 
            # continue
            self.log_feedback(feedback_val, recv_time)
        

    def sender(self):
        self.start_time = time.time()
        start_time = self.start_time
        self.feedback_applied = [0.0 for _ in self.timestamps]

        for i, t in enumerate(self.timestamps):
            # wait until scheduled send time (trace time + latency)
            while time.time() < start_time + t + self.latency:
                time.sleep(0.001)

            # drain feedbacks and map each to earliest valid timestamp bin
            with self.feedback_lock:
                if self.feedback_queue:
                    # unpack to arrays for fast mapping
                    rts = np.array([rt for rt, _v in self.feedback_queue], dtype=float)
                    vals = np.array([_v for rt, _v in self.feedback_queue], dtype=float)

                    # next original timestamp >= recv_time
                    idxs = np.searchsorted(self.timestamps, rts, side="left")
                    # never apply to already-sent bins
                    idxs = np.maximum(idxs, i)

                    # apply to bins within range; keep the rest
                    keep = []
                    for rt, v, j in zip(rts, vals, idxs):
                        if j < len(self.feedback_applied):
                            self.feedback_applied[j] += v
                        else:
                            keep.append((rt, v))  # no future bin left
                    self.feedback_queue = keep

            # build and send this sample
            self.cumulative_feedback += self.feedback_applied[i]
            corrected_y = self.true_motion[i] + self.cumulative_feedback
            packed = struct.pack("d", corrected_y)
            self.sock.sendto(packed, (self.target_ip, self.target_port))

            send_actual_time = time.time() - start_time
            self.log_lines.append(
                f"{t:.5f}\t{self.true_motion[i]:.4f}\t{corrected_y:.4f}\t{self.feedback_applied[i]:.4f}\t{send_actual_time:.5f}"
            )
    '''
    def log_feedback(self, feedback_val, recv_time):
        with open(self.log_file_path.replace("simulation_log", "feedback_log"), "a") as f:
            f.write(f"{recv_time:.9f}\t{feedback_val:.6f}\n")
    '''
    def log_feedback(self, feedback_val, recv_time):
        with open(self.feedback_log_path, "a") as f:
            f.write(f"{recv_time:.9f}\t{feedback_val:.6f}\n")

    def run_simulation(self):
        # --- RESET feedback log at the start ---
        self.feedback_log_path = self.log_file_path.replace("simulation_log", "feedback_log")
        with open(self.feedback_log_path, "w") as f:
            f.write("RecvTime\tFeedback\n")

        # Start threads
        recv_thread = threading.Thread(target=self.feedback_listener, daemon=True)
        send_thread = threading.Thread(target=self.sender)

        recv_thread.start()
        send_thread.start()

        send_thread.join()
        recv_thread.join(timeout=2.0)

        self.sock.close()

        # --- SAVE simulation log at the end ---
        with open(self.log_file_path, "w") as f:
            f.write("Time\tOriginal_motion\tCompensated_motion(SentY)\tReceived_feedback\tActualSendTime\n")
            f.write("\n".join(self.log_lines))

    def evaluate_auc(self):

        times, true_y, sent_y = [], [], []
        with open(self.log_file_path, "r") as f:
            next(f)  # Skip header
            for line in f:

                t, ty, sy, *_ = map(float, line.strip().split())

                times.append(t)

                true_y.append(ty)

                sent_y.append(sy)

        times = np.array(times)
        true_y = np.array(true_y)
        sent_y = np.array(sent_y)
        delta_t = np.mean(np.diff(times))  # Assume uniform time steps
    
        auc_original = np.sum(np.abs(true_y)) * delta_t

        auc_compensated = np.sum(np.abs(sent_y)) * delta_t

        auc_diff = auc_original - auc_compensated

        reduction_ratio = 1 - (auc_compensated / auc_original)
    
        print(f"AUC Original:     {auc_original:.2f}")

        print(f"AUC Compensated: {auc_compensated:.2f}")

        print(f"Δ AUC:            {auc_diff:.2f} (Reduction: {reduction_ratio:.2%})")
    
        return {

            "auc_original": auc_original,

            "auc_compensated": auc_compensated,

            "auc_diff": auc_diff,

            "reduction_ratio": reduction_ratio

        }

 
 
    def plot_results(self, plot_motor_position=True):
        import os, time
        # --- load main simulation log ---
        time_vals, true_y, sent_y, corrected_y = [], [], [], []
        with open(self.log_file_path, "r") as f:
            next(f)  # skip header
            for line in f:
                parts = line.strip().split()
                if len(parts) < 4:
                    continue
                t, ty, sy, cy = map(float, parts[:4])
                time_vals.append(t)
                true_y.append(ty)
                sent_y.append(sy)
                corrected_y.append(cy)

        # Basic metrics
        residual_error = [ty - cy for ty, cy in zip(true_y, corrected_y)]
        track_dt = float(np.mean(np.diff(self.timestamps))) if len(self.timestamps) > 1 else float("nan")

        # --- (optional) motor position from feedback log, plotted as scatter ---
        motor_t, motor_pos = None, None
        if plot_motor_position:
            fb_path = getattr(self, "feedback_log_path", self.log_file_path.replace("simulation_log", "feedback_log"))
            if os.path.exists(fb_path):
                recv_times, fb_vals = [], []
                with open(fb_path, "r") as f:
                    # skip header if present
                    first = f.readline()
                    try:
                        a, b = first.strip().split()[:2]
                        _ = float(a); _ = float(b)
                        # header was actually data -> keep it
                        recv_times.append(float(a)); fb_vals.append(float(b))
                    except Exception:
                        pass  # real header; move on

                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 2:
                            continue
                        try:
                            recv_times.append(float(parts[0]))
                            fb_vals.append(float(parts[1]))
                        except ValueError:
                            continue

                if recv_times:
                    recv_times = np.array(recv_times, dtype=float)
                    fb_vals = np.array(fb_vals, dtype=float)
                    # cumulative position from feedback deltas
                    pos = np.cumsum(fb_vals)
                    order = np.argsort(recv_times)
                    motor_t = recv_times[order]
                    motor_pos = pos[order]

        # --- title pieces ---
        trace_label = getattr(self, "trace_name", os.path.basename(self.log_file_path))
        latency_ms = self.latency * 1000
        latency_label = f"{latency_ms:.1f} ms"
        vel = getattr(self, "motor_velocity", None)
        vel_label = f"{vel:.1f} mm/s" if isinstance(vel, (int, float)) and vel is not None else "N/A"
        track_dt_ms = track_dt * 1000 if np.isfinite(track_dt) else float("nan")
        track_dt_label = f"{track_dt_ms:.1f} ms" if np.isfinite(track_dt_ms) else "N/A"
        title = f"{trace_label} | Latency: {latency_label} | Motor speed: {vel_label} | Tracking Δt: {track_dt_label}"


        # --- plot ---
        plt.figure(figsize=(10, 6))
        plt.plot(time_vals, true_y, label="Original Motion")
        plt.plot(time_vals, sent_y, label="Compensated motion", linestyle="--")

        if (motor_t is not None) and (motor_pos is not None):
            # scatter to avoid line artifacts
            plt.scatter(motor_t, motor_pos, s=10, color = 'green', label="Couch position")

        plt.xlabel("Time (s)")
        plt.ylabel("Position (mm)")
        plt.title(title)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        out_name = f"plot_{trace_label}_{self.latency:.3f}s_{time.strftime('%Y%m%d_%H%M%S')}.png".replace(" ", "_")
        plt.savefig(out_name, dpi=300)
        plt.show()

        print(f"Saved plot to: {out_name}")
        print(f"Max Error: {max(abs(e) for e in residual_error):.2f} mm")
        print(f"RMS Error: {np.sqrt(np.mean(np.square(residual_error))):.2f} mm")



import socket
import struct
import threading
import time

class MotorEmulator:
    """
    Two-thread UDP motor emulator with strict 'first-after-finish' selection:
      - Receiver thread: always listening for incoming targets.
        * If motor is IDLE: accept the target, mark BUSY, wake motor thread.
        * If motor is BUSY: discard the packet and immediately send 0.0 feedback.
      - Motor thread: executes one move at a time at constant velocity, then becomes IDLE.
        * Only after it becomes IDLE can the receiver accept the next (first) packet that arrives.

    Feedback policy:
      - For skipped packets while busy: send 0.0 immediately (matches your C++ behavior).
      - For executed move: send feedback equal to the executed compensation (move_mm = -error).
    """
    def __init__(
        self,
        listen_ip: str,
        listen_port: int,
        feedback_target_ip: str,
        feedback_target_port: int,
        motor_velocity_mm_per_s: float = 100.0,
        log_fn=print
    ):
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.feedback_target_ip = feedback_target_ip
        self.feedback_target_port = feedback_target_port
        self.v = float(motor_velocity_mm_per_s)
        self.log = log_fn

        # UDP socket for recv+send
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.listen_ip, self.listen_port))

        # Shared state
        self._lock = threading.Lock()
        self._running = threading.Event(); self._running.set()

        self._motor_busy = False
        self._active_target = None       # the ONE target motor will execute next
        self._move_event = threading.Event()

        # Optional internal pose tracking (diagnostics)
        self._couch_pos_mm = 0.0

        # Threads
        self._recv_th = threading.Thread(target=self._recv_loop, name="MotorRecv", daemon=True)
        self._move_th = threading.Thread(target=self._motor_loop, name="MotorExec", daemon=True)

    def start(self):
        self.log(f"[MOTOR] Listening on {self.listen_ip}:{self.listen_port} | "
                 f"velocity={self.v:.1f} mm/s | policy=first-after-finish")
        self._recv_th.start()
        self._move_th.start()

    def stop(self):
        self._running.clear()
        self._move_event.set()  # wake motor loop if waiting
        try:
            self.sock.close()
        except Exception:
            pass
        time.sleep(0.1)

    # ---------------- receiver thread ----------------
    def _recv_loop(self):
        while self._running.is_set():
            try:
                data, _addr = self.sock.recvfrom(1024)
            except OSError:
                break  # socket closed
            except Exception as e:
                self.log(f"[MOTOR][RECV] Error: {e}")
                continue

            if len(data) < 8:
                continue

            target = struct.unpack("d", data[:8])[0]

            with self._lock:
                if not self._motor_busy and self._active_target is None:
                    # Motor is idle and no target in flight: accept this target
                    self._active_target = target
                    self._motor_busy = True
                    self._move_event.set()
                    self.log(f"[MOTOR][RECV] Accepted target {target:.4f} (idle -> start move)")
                    # NOTE: no immediate feedback; feedback is sent after the move completes
                else:
                    # Motor busy or a target already queued -> discard and send 0.0 immediately
                    self._send_feedback_immediate(0.0)
                    self.log(f"[MOTOR][RECV] Busy -> skipped {target:.4f} (sent 0.0 feedback)")

    # ---------------- motor thread ----------------
    def _motor_loop(self):
        while self._running.is_set():
            self._move_event.wait(timeout=0.1)
            if not self._running.is_set():
                break

            with self._lock:
                target = self._active_target
                # clear the event so we don't immediately loop without a new acceptance
                self._move_event.clear()

            if target is None:
                # spurious wake-up; continue waiting
                continue

            # Interpret target as measured deviation (mm). Compensation is opposite direction.
            error = float(target)
            move_mm = -error
            duration = abs(move_mm) / self.v if self.v > 0 else 0.0

            self.log(f"[MOTOR][MOVE] Executing {move_mm:.4f} mm "
                     f"(|{move_mm:.4f}|/{self.v:.1f} mm/s) -> {duration:.3f}s")

            # Simulate motion
            t0 = time.time()
            while self._running.is_set() and (time.time() - t0) < duration:
                time.sleep(0.001)

            # Update pose and send feedback for the executed move
            with self._lock:
                self._couch_pos_mm += move_mm

            self._send_feedback_immediate(move_mm)
            self.log(f"[MOTOR][MOVE] Done. Sent feedback {move_mm:.4f} | couch={self._couch_pos_mm:.4f} mm")

            # Become idle; accept only the first new packet that arrives after this point
            with self._lock:
                self._active_target = None
                self._motor_busy = False
                # Now receiver thread will accept the first subsequent packet only

    # ---------------- feedback helper ----------------
    def _send_feedback_immediate(self, value: float):
        try:
            self.sock.sendto(struct.pack("d", float(value)),
                             (self.feedback_target_ip, self.feedback_target_port))
        except Exception as e:
            self.log(f"[MOTOR][FEEDBACK] Send error: {e}")



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Motion compensation simulator runner")
    parser.add_argument("--mode", choices=["cross", "local"], default="cross",
                        help="cross = send to external Pi; local = run Python motor emulator")
    parser.add_argument("--trace", type=str, required=True, help="Path to input motion trace file")
    parser.add_argument("--latency", type=float, default=0, help="Tracker latency (seconds)") # Default value is zero unless specified 
    parser.add_argument("--local-port", type=int, default=2400, help="UDP port the tracker listens on for feedback")
    parser.add_argument("--target-port", type=int, default=1400, help="UDP port the motor listens on for commands")
    parser.add_argument("--velocity", type=float, default=12.0, help="Motor velocity (mm/s) for local emulator") # Default motor speed is 12mm/s, consistent with real motor hardware
    parser.add_argument("--pi-ip", type=str, default="192.168.8.2",
                        help="Target IP for cross-device mode (Pi motor emulator)")
    parser.add_argument("--track-dt", type=float, default=None,
                    help="Tracker sampling interval in seconds (e.g., 0.05 for 50 ms). If omitted, use file as-is.")

    args = parser.parse_args()

    # Resolve IPs based on mode (ports come from args)
    if args.mode == "local":
        local_ip = "127.0.0.1"
        target_ip = "127.0.0.1"
        print("[MODE] LOCAL — tracker + motor emulator on this machine via UDP localhost")
    else:
        local_ip = "0.0.0.0"    # bind all interfaces to receive feedback
        target_ip = args.pi_ip  # send commands to the Pi
        print(f"[MODE] CROSS — tracker -> {target_ip}:{args.target_port} (Pi)")

    log_file = f"simulation_log_{args.mode}.txt"

    # Instantiate your existing tracker/compensator (UNCHANGED)
    sim = MotionCompensationSimulator(
        trace_file=args.trace,
        latency=args.latency,
        local_ip=local_ip,
        local_port=args.local_port,
        target_ip=target_ip,
        target_port=args.target_port,
        log_file=log_file,
        track_dt=args.track_dt
    )
    if args.mode == "local":
        sim.motor_velocity = args.velocity
    else:
        sim.motor_velocity = None  # unknown / N/A


    # Start local motor emulator only in LOCAL mode
    motor = None
    try:
        if args.mode == "local":
            # Ensure MotorEmulator class is defined above with first-after-finish policy
            motor = MotorEmulator(
                listen_ip="127.0.0.1",
                listen_port=args.target_port,
                feedback_target_ip="127.0.0.1",
                feedback_target_port=args.local_port,
                motor_velocity_mm_per_s=args.velocity
            )
            motor.start()

        # Run the simulation and post-process
        sim.run_simulation()
        sim.evaluate_auc()
        sim.plot_results()

    except KeyboardInterrupt:
        print("\n[MAIN] Interrupted by user.")
    finally:
        if motor:
            motor.stop()
        print("[MAIN] Done.")
