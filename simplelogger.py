import datetime
import time
# import traceback
from pathlib import Path
import tktools.easyfiledialogs
import logging
import tkinter as tk

class SimpleLogger():
    def __init__(self):
        self.filename_string = "default.txt"

        self.last_log_filename = None
        self.log_filename = None

        self.header_string = ''

        self.logfilename_prefix = ''

        logging.basicConfig(level=logging.ERROR)

    def set_logfile_prefix(self, logfile_prefix):
        self.logfilename_prefix = logfile_prefix
        
    def create_log_file(self, filename_string = ''):
        self.log_filename = easyfiledialogs.get_path_to_save_file(default_filename = self.create_default_filename(self.logfilename_prefix + filename_string))
        logging.debug(f"Saving logfile as {self.log_filename}")

        try:
            with open(self.log_filename, 'w', encoding="utf-8") as logfile:
                logfile.write('')
        except:
            logging.error(f"log_filename: {self.log_filename}", exc_info=True)

    def pause_logging(self):
        """ stop logging, but do not close the file """
        pass

    def stop_log(self):
        logging.debug(f"Logging Stopped")
        try:
            logfile = open(self.log_filename, 'a', encoding="utf-8")
            logfile.close()
            self.last_log_filename = self.log_filename
            self.log_filename = None
        except:
            logging.error(f"log_filename: {self.log_filename}", exc_info=True)

    def get_last_log_filename(self):
        """ returns the last log filename, for putting into a log plotting script"""
        return self.last_log_filename

    def get_log_filename(self):
        """ returns the last log filename, for putting into a log plotting script"""
        return self.log_filename

    def write_line_to_log(self, line_string, b_add_timestamp=True):
        """ Write a single line to the logfile """
        line_to_write = ''
        try:
            if self.log_filename != None:
                with open(self.log_filename, 'a', encoding="utf-8") as logfile:
                    if b_add_timestamp:
                        timestamp = datetime.datetime.now().timestamp()
                        line_to_write = f"{timestamp},{line_string}"
                    else:
                        line_to_write = f"{line_string}"
                    logfile.write(line_to_write + "\n")
                    logging.debug(line_to_write)
        except:
            logging.error(f"Write fail - log_filename: {self.log_filename} - line_string: {line_string}", exc_info=True)

    def set_header(self, header_string):
        self.header_string = header_string

    def write_header_to_log(self):
        self.write_line_to_log(self.header_string, False)  

    def get_datetime_string(self):
        return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        # return datetime.datetime.strftime("%Y-%m-%d_%H-%M-%S", datetime.datetime.now())

    def create_default_filename(self, string_in='', suffix='csv'):
        return f"{self.get_datetime_string()}_{string_in}.{suffix}"

class tkLoggingControls(tk.Frame):
    def __init__(self, parent, log, **kwargs):
        tk.Frame.__init__(self, parent, kwargs)

        self.logger = log

        self.b_logging = False
        self.b_led_toggle = False

        self.log_strip = tk.Frame(parent)

        self.led_log = tktools.tkLED(self.log_strip, on_colour='green', off_colour='black')
        self.led_log.pack(side='left')

        self.btn_log = tk.Button(self.log_strip, text='Start Log', command=self.toggle_logging,  padx=30)
        self.btn_log.pack(side='left')

    def toggle_logging(self):
        if self.b_logging:
            self.b_logging = False
            self.logger.stop_log()
            self.btn_log['text'] = 'Start Log'
        else:
            self.b_logging = True
            self.btn_log['text'] = 'Stop Log'
            # self.btn_log['bg'] = 'red'
            self.logger.create_log_file()
            self.logger.write_header_to_log()

    def toggle_logging_led(self):
        self.led_log.toggle()

    def get_logging_state(self):
        return self.b_logging

    """ Tkinter layout methods """    
    def grid(self, **kwargs):#row, column):
        self.log_strip.grid(kwargs)#row=row,column=column)#, side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def pack(self, **kwargs):
        self.log_strip.pack(kwargs)#(side=Tk.TOP, fill=Tk.BOTH, expand=1)
