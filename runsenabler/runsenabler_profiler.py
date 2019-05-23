import time
import calendar
import os
import logging

import cProfile, pstats, io

class RunsEnablerLogger:
    def __init__(self):
        self.logfile_name = "runs-profile-"+str(calendar.timegm(time.gmtime()))+".txt"
        self.logfile_path = os.path.join(os.getcwd(), self.logfile_name)
        
        # Create the logger instance which will write the profiling data
        self.logger = logging.getLogger("runs enabler profiler")
        self.logger.setLevel(logging.DEBUG)
        file_handle = logging.FileHandler(self.logfile_path)
        file_handle.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handle.setFormatter(formatter)
        self.logger.addHandler(file_handle)
    
    def log_message_info(self, message):
        self.logger.info(message)
    
    def log_message_debug(self, message):
        self.logger.debug(message)

class Timer:
    def __init__(self, logger, profile_info):
        self.logger = logger
        self.time = 0
        self.info = profile_info

    def __enter__(self):
        self.time = time.time()
        return self
    
    def __exit__(self, t, v, traceback):
        self.time = time.time() - self.time
        self.logger.log_message_info(self.info+": total time - "+str(self.time)+"s")

class RunsEnablerProfiler:
    def __init__(self, logger):
        self.logger = logger
    
    def TimeBlock(self, info):
        return Timer(self.logger, info)
    
    def ProfileBlock(self):
        return Profiler(self.logger)

class Profiler:
    def __init__(self, logger):
        self.logger = logger
        self.pr = cProfile.Profile()
    
    def __enter__(self):
        self.pr.enable()
        return self

    def __exit__(self, t, v, traceback):
        self.pr.disable()
        stats = io.StringIO()
        ps = pstats.Stats(self.pr, stream=stats).sort_stats('cumtime')
        ps.print_stats()
        self.logger.log_message_info(stats.getvalue())

class NoOpTimer:
    def __init__(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, t, v, traceback):
        pass

class NoOpProfiler:
    def __init__(self):
        pass

    def TimeBlock(self, info):
        return NoOpTimer()
    
    def ProfileBlock(self):
        return NoOpTimer()

class NoOpLogger:
    def __init__(self):
        pass
    
    def log_message_info(self, message):
        pass
    
    def log_message_debug(self, message):
        pass