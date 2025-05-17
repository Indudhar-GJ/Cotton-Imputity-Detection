import logging
import time

class TimerLogger:
    def __init__(self, log_file="timing.log"):
        self.logger = logging.getLogger("TimerLogger")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)
        self.start_times = {}

    def start(self, step_name):
        """Start timing a step."""
        self.start_times[step_name] = time.perf_counter()
        self.logger.info(f"Started: {step_name}")

    def stop(self, step_name):
        """Stop timing a step and log the duration in milliseconds."""
        if step_name not in self.start_times:
            self.logger.warning(f"No start time recorded for {step_name}")
            return
        elapsed_time = (time.perf_counter() - self.start_times.pop(step_name)) * 1000  # Convert to milliseconds
        self.logger.info(f"Completed: {step_name} in {elapsed_time:.3f} ms")

# Example usage
if __name__ == "__main__":
    timer_logger = TimerLogger()
    
    timer_logger.start("Fast Function")
    time.sleep(0.001)  # Simulating a very fast function (~1ms)
    timer_logger.stop("Fast Function")
