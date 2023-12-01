# from logging import exception
import serial
import serial.tools.list_ports
import time
import traceback
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext
import traceback

# my libraries
from tktools.easyfiledialogs import get_path_to_save_file
import tenma_interpreter
import tktools
import plotTenmaLog


# def get_log_line_from_tenma_message(msg_in):
#     log_line = f"{msg_in['Time']},{msg_in['Mode']},{msg_in['OL']},{msg_in['Display Value']},{msg_in['Display Unit']},{msg_in['Actual Value']},{msg_in['Actual Unit']},{msg_in['AD/DC']},{msg_in['Reading Type']},{msg_in['Hold']},{msg_in['Meter State']},{msg_in['Bar Graph State']},{msg_in['Bar Graph Value']},{msg_in['Z1']},{msg_in['Z2']},{msg_in['Z3']},{msg_in['Z4']}"
#     return log_line

datalogger = tktools.SimpleLogger()
datalogger.set_logfile_prefix('Tenma_')

def quit():
    print("QUITTING...")
    serial_connection.close()
    window.destroy()

# todo, oop this
# create tenma object
def main_program_loop():
    if serial_connection.is_open():
        while serial_connection.in_waiting > 0:
            data = serial_connection.read_serial_line()

            if data == b'\r\n':
                """ if the message is blank, skip it """
                # logger.debug('blank message intercepted')
                continue

            try:
                meter_msg = tenma.interpret_tenma_722610_msg(data)
                # print(f"good - {data}")

                if meter_msg['OL'] == True:
                    lbl_display_val['text'] = 'OL'
                else:
                    lbl_display_val['text'] = f"{meter_msg['Display Value']:.03f}{meter_msg['Display Unit']}"
                    graph.add_y_point("tenma", meter_msg['Actual Value']) # append the read value to the coordinate data list

                    # print(f'{len(y_coords)},    {x_coords[-1]}, {y_coords[-1]}')
                    graph.set_ylabel(meter_msg['Actual Unit'])
                    graph.update_graph()

                    if log_controls.get_logging_state():
                        log_controls.toggle_logging_led()
                        out_text = tenma.get_log_line_from_tenma_message(meter_msg)
                        datalogger.write_line_to_log(out_text,b_add_timestamp=False)

            except:
                print(f"EXCEPTION! data read -> {data}")
                print(f"bad - {data}")
                print(traceback.format_exc())
                # pass # if we have a dodgy message, just skip it
         
    window.after(10,main_program_loop) # run this every 10 milli seconds

########## GRAPH FUNCTIONS ##########

def plot_last_log():
    last_log_filename = datalogger.get_last_log_filename()
    if (last_log_filename == None):
        print('no last log')
        pass
    else:
        plotTenmaLog.plot_tenma_logfile(last_log_filename)

""" DEFINE GUI WIDGETS """

tenma = tenma_interpreter.TenmaMeterSerialMsgs()

window = tk.Tk()
window.title('Tenma 72-2610 Multimeter Interface')
tenmaframe = tk.Frame(window)

serial_connection = tktools.tkSerial(window, name='Serial:', borderwidth=4, relief=tk.GROOVE)
serial_connection.configure_serial_port(
    baud = 2400,
    RTS = False, # required for tenma meters, as these lines power the optical reciever circuit
    DTR = True 
    )
serial_connection.pack()

display_value_readout = tk.Frame(tenmaframe)
lbl_display_val = tk.Label(display_value_readout, text='------', justify='center', font=('Arial',50), anchor=tk.CENTER, pady=2)
lbl_display_val.pack()
display_value_readout.pack()

graph = tktools.tkGraphMultiLine(tenmaframe)
graph.set_xlabel("Time [s]")
graph.pack()
graph.add_series(name="tenma", label="Tenma Actual Value")
graph.pack()

graph_controls = tktools.tkGraphControls(tenmaframe,graph)
graph_controls.pack()

log_controls = tktools.tkLoggingControls(tenmaframe,datalogger)
log_controls.pack()

plot_last_log_controls = tk.Frame(tenmaframe)
btn_plot_last_log = tk.Button(plot_last_log_controls, text='Plot Last Log', command=plot_last_log)
btn_plot_last_log.pack(side='left')
plot_last_log_controls.pack()

tenmaframe.pack()

### INITIALISATIONS ###

tenma_header = tenma.get_tenma_722610_msg_header() #f"Time,Mode,Display Value,Display Unit,Actual Value,Actual Unit,AD/DC,Reading Type,Hold,Meter State,Bar Graph State,Bar Graph Value,Z1,Z2,Z2,Z4"
datalogger.set_header(tenma_header)

main_program_loop()
window.mainloop()
