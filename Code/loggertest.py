from Time_logger import TimerLogger
import time
timer_logger = TimerLogger()
    
timer_logger.start("Fast Function")
time.sleep(0.001)  # Simulating a very fast function (~1ms)
timer_logger.start("Very Fast Function")
time.sleep(0.2)
timer_logger.stop("Very Fast Function")
timer_logger.stop("Fast Function")