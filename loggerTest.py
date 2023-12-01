import tktools.simplelogger as simplelogger
import logging

logging.basicConfig(level=logging.DEBUG)

myLogger = simplelogger.SimpleLogger()

myLogger.create_log_file('test')

myLogger.write_header_to_log('timestamp,stuff')

for i in range(20):
    myLogger.write_line_to_log(i)

myLogger.stop_log()
print(f"Last Log Filename: {myLogger.get_last_log_filename()}")
