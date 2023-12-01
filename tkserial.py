import serial
import serial.tools.list_ports
import tkinter as tk
import tkinter.ttk as ttk
import logging
import traceback
import tktools

"""
TkSerial

A module for providing a serial connection for a tkinter GUI
"""

"""
# TODO
- [/] create frame for connect
    - [x] label
    - [x] port combobox
    - [x] refresh button
    - [x] connect/disconnect button
    - [x] msg rec led
    - [x] msg sent led
- [ ] create frame for receive
- [ ] create frame for transmit

- [ ] serial functions
- [/] add logging for debug
    - [ ] setup to give timestamp, line number etc etc

- [ ] add shelve or pickle or similar for last used comport

"""


class tkSerial(tk.Frame):
    def __init__(self, parent, name='SERIAL CONNECTION', **kwargs):

        self.name = name

        self.serialport = serial.Serial()

        self.errorLogger = logging.getLogger(f"{__name__} - {name}")
        # self.errorLogger.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s')

        self.com_ports = self.get_com_ports()
        self.selected_port = None

        self.b_ser_port_open = False

        self.baudrate = 9600
        self.configure_serial_port(self.baudrate) # set defaults

        """ Serial Connect Frame"""
        self.serial_connect_frame = tk.Frame(parent,**kwargs)

        self.name_label = tk.Label(self.serial_connect_frame,text=self.name)
        self.cbo_ports = ttk.Combobox(self.serial_connect_frame)
        self.set_cbo_ports_values()
        self.btn_com_port_refresh = tk.Button(self.serial_connect_frame, text='Refresh', command=self.set_cbo_ports_values)
        
        self.cbo_speed = ttk.Combobox(self.serial_connect_frame)
        self.cbo_speed['values'] = (300,1200,2400,4800,9600,19200,38400,57600,74880,115200,230400)
        self.cbo_speed.current(9)
        
        self.btn_connect = tk.Button(self.serial_connect_frame, text='CONNECT',command=self.open_close_port)
        self.led_rec = tktools.tkled.tkLED(self.serial_connect_frame, on_colour='#FFFFCC', off_colour='white')
        self.led_tx = tktools.tkled.tkLED(self.serial_connect_frame, on_colour='#FFFFCC', off_colour='white')

        self.name_label.pack(side='left')
        self.cbo_ports.pack(side='left')
        self.btn_com_port_refresh.pack(side='left')
        self.cbo_speed.pack(side='left')
        self.btn_connect.pack(side='left')
        self.led_rec.pack(side='left')
        self.led_tx.pack(side='left')

        """ Serial Receive Frame """
        self.lbl_serial_rx = tk.Label(self.serial_connect_frame, text='serial comes out here')

        """" Serial Transmit Frame """

        self.btn_transmit = tk.Button(self.serial_connect_frame, text='TRANSMIT', command=self.send_serial)
        tx_text = tk.Entry(self.serial_connect_frame, width=30)
        tx_text.focus()

    """ Serial Setup Functions """

    def get_baud_rate(self):
        return self.cbo_speed.get()

    def set_baud_rate(self, rate):
        self.serialport.baudrate = rate

    def get_com_ports(self):
        self.errorLogger.debug("Finding COM ports...")
        return serial.tools.list_ports.comports()

    def get_names_of_available_com_ports(self):
        self.errorLogger.debug("Listing COM ports...")
        port_names = [i.description for i in self.com_ports] # or use description
        return port_names

    def get_selected_port(self):
        selected_index = self.cbo_ports.current()
        if selected_index == -1:
            return -1
        else:
            return self.com_ports[selected_index]

    def set_cbo_ports_values(self):
        list_of_ports = self.get_names_of_available_com_ports() #('/dev/ttyUSB0','/dev/ttyUSB1','COM17')
        if len(list_of_ports) == 0:
            list_of_ports = ['NO SERIAL PORTS']
        self.cbo_ports['value'] = list_of_ports
        self.cbo_ports.current(0) # start the box on the first value in the list

    def open_close_port(self):
        if self.b_ser_port_open: # if port is open, close it
            # close port
            self.serialport.close()
            self.errorLogger.debug(f'Closed serial port {self.selected_port}')
            self.b_ser_port_open = False
            self.btn_connect['text'] = "CONNECT"
        else:               # if port is closed, open it
            self.selected_port = self.get_selected_port()

            # if nothing has been selected, return without doing anything
            if self.selected_port == -1:
                self.errorLogger.debug(f'ERROR: No port selected')
                return

            self.serialport.close()
            self.serialport.port = self.selected_port.device
            self.baudrate = self.get_baud_rate()
            self.set_baud_rate(self.baudrate)
            try:
                self.serialport.open()
                self.errorLogger.debug(f'Opened serial port {self.selected_port.name}')
                self.b_ser_port_open = True
                self.btn_connect['text'] = "DISCONNECT"
                self.serialport.flush()
            except:
                self.errorLogger.error(traceback.format_exc())
                self.errorLogger.error(f'ERROR: Failed to open serial port {self.selected_port.name} at {self.baudrate}')

    """ Serial Properties """

    def is_open(self):
        return self.serialport.is_open

    @property
    def in_waiting(self):
        return self.serialport.in_waiting

    def close(self):
        self.serialport.close()

    def flush(self):
        self.serialport.flush()

    """ Serial Functions """

    def configure_serial_port(self,
                                baud,
                                bytesize = serial.EIGHTBITS,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                timeout = 3,
                                xonxoff = False,
                                rtscts = False,
                                dsrdtr = False,
                                writeTimeout = 3,
                                RTS = False,
                                DTR = False):

        self.serialport.baudrate = baud
        self.serialport.bytesize = bytesize
        self.serialport.parity = parity
        self.serialport.stopbits = stopbits
        self.serialport.timeout = timeout
        self.serialport.xonxoff = xonxoff
        self.serialport.rtscts = rtscts
        self.serialport.dsrdtr = dsrdtr
        self.serialport.writeTimeout = writeTimeout
        self.serialport.setRTS(RTS) # required for tenma meters, as these lines power the optical reciever circuit
        self.serialport.setDTR(DTR) 

    def read_serial_line(self):
        """TODO ideally this would be in a seperate thread and new info would go into a buffer to be read out from the mainloop
        which i guess this is kind of doing"""
        try:
            data = self.serialport.readline() # data = self.serialport.readline().decode('ascii').strip()#.split(,)
            self.errorLogger.debug(f"data - {data}")
            self.led_rec.toggle()
            return(data)
        except NameError: 
            self.errorLogger.error('ERROR: No Serial Port Open!, Name Error')
            # TODO - how to fail robustly here

    def send_serial(self,data):
        # add timeout check
        # return true or false for succeed/fail
        # add exception catching
        try:
            self.serialport.write(data.encode('utf-8'))
            self.errorLogger.debug('SEND: ' + data + '\n')
            self.led_tx.toggle()
        except NameError:
            self.errorLogger.error('ERROR: No Serial Port Open!, Name Error')
   
    """ tkinter functions """
    # pack all stuff into frame

    """ set background colour """
    def set_bg_color(self, color):
        self.serial_connect_frame['bg'] = color

    """ Tkinter layout methods """    
    def grid(self, **kwargs):#row, column):
        self.serial_connect_frame.grid(kwargs)#row=row,column=column)#, side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def pack(self, **kwargs):
        self.serial_connect_frame.pack(kwargs)#(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def lift(self, target):
        self.serial_connect_frame.lift(target)

""" MAIN RUN TEST """

if __name__ == "__main__":
    import tkled
    root = tk.Tk()
    ser_frame = tkSerial(root, name='CHEESE', borderwidth=4, relief=tk.GROOVE)
    ser_frame.pack()

    root.mainloop()

