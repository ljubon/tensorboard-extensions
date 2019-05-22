import time
import calendar
import os
import logging

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

class RunsEnablerProfiler:
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