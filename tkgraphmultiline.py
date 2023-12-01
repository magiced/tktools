import matplotlib
matplotlib.use('TkAgg')
# from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk )
from matplotlib.figure import Figure
import tkinter as tk
import tkinter.ttk as ttk
import random
import datetime
import logging
try:
    import tktools.easyfiledialogs as easyfiledialogs
except ModuleNotFoundError:
    import easyfiledialogs

# https://matplotlib.org/stable/api/backend_tk_api.html#matplotlib.backends.backend_tkagg.FigureCanvasTkAgg
"""
TODO

* [x] modify update code to work with my data
* [x] DONE - add graph title/ axis labels
* [x] - work out why titles etc are not given space in canvas widgets
* [x] - add second/more graphs
* add second line 
* [x] - move update function into class (think this may solve update problem)
* [x] clean up update function
* [x] add start and stop graph functions for connecting to buttons
* [x] autoscale y, possible also x
* [ ] add 'start graph' function to make first call clearer to user
* [ ] add input cleaning to check for unplottable/garbage data
* [ ] could autoscale x be used to re-scale the x axis. i.e. it will change to 
        fit the number of values in the dataset plotted. so you could chane the 
        size of the dataset to change the graph width. i.e. change from 60 rows to 
        3600 rows. you'd generate x lines of [time, 0], then add the existing data
        at the end to 

* [ ] change graph size function
* [ ] reset graph function    

other functions
pop
len (is there a way of doing a proper len? don't make your life difficult ed...
set_max_width
change max width

"""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                        Multiple Line Graph
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class tkGraphMultiLine(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.logger = logging.getLogger(f"{__name__}")

        self.series = {}
        self.lines = {}

        self.x_data = []
        self.y_data = []

        self.start_time = None
        self.b_elapsed_time = False

        self.max_y_value = 0
        self.min_y_value = 0
        self.max_x_value = 0
        self.min_x_value = 0

        self.traces = dict()
        self.b_running = True

        self.b_graph_created = False

        self.autoscale_y_on = False
        self.autoscale_x_on = False

        # Define matplotlib figure
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.set_tight_layout(True)
        self.ax.autoscale(tight=False)

        self.graph_width = 600 # ten minutes

        # self.ax.set_ylim(34,46)
        # self.ax.set_xlim()
        # self.ax.legend()

        # Tell Tkinter to display matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw() # show() - show does not work for this

    """ Tkinter layout methods """    
    def grid(self, **kwargs):#row, column):
        self.canvas.get_tk_widget().grid(kwargs)#row=row,column=column)#, side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def pack(self, **kwargs):
        self.canvas.get_tk_widget().pack(kwargs)#(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    """" graph format methods """

    def set_xlabel(self, label, **kwargs):
        self.ax.set_xlabel(label, kwargs)
        pass

    def set_ylabel(self, label, **kwargs):
        self.ax.set_ylabel(label, kwargs)
        pass

    def set_secondary_ylabel(self, label, **kwargs):
        self.ax2.set_ylabel(label, kwargs)
        pass

    def set_title(self, title, **kwargs):
        self.ax.set_title(title, kwargs)
        pass

    def add_legend(self, **kwargs):
        self.fig.legend(kwargs)

    # def set_color(self,color):
    #     self.ax.line1.set_color(color)
    #     pass

    def set_grid_lines(self, visible=None, which='major', axis='both', **kwargs):
        self.ax.grid(visible, which, axis, **kwargs)

    def set_bg_color(self, color):
        self.ax.set_facecolor(color)

    def set_graph_width(self, width):
        """ method to set the graph width, used for resetting and increasing the 
        amount of data displayed on the graph """
        self.graph_width = width

    """ Graph use methods """

    def add_series(self, name='default', label='', secondary_axis=False, elapsed_time=False, **kwargs):
        self.logger.debug(f"{name}, {label}, Secondary Axis: {secondary_axis}, elapsed time: {elapsed_time} ")
        # TODO kwargs
        if (label == ''):
            label = name

        self.series[name] = { 'label': label,
        'x': [],
        'y': [],
        'secondary_axis':secondary_axis
        }
        
        if secondary_axis == False:
            self.lines[name] = self.ax.plot(self.series[name]['x'], self.series[name]['y'],label=label, **kwargs)
        else:
            self.ax2 = self.ax.twinx()
            self.lines[name] = self.ax2.plot(self.series[name]['x'], self.series[name]['y'],label=label, **kwargs)
        
    def get_elapsed_time(self):
        return (datetime.datetime.now() - self.start_time).total_seconds()
        # try:
        #     return (datetime.datetime.now() - self.start_time).total_seconds()
        # except TypeError:
        #     print(f"get_elapsed_time TypeError")
        #     self.set_start_time()
        #     pass

    def reset_graph(self):
        for key,item in self.series.items():
            self.series[key]['x'] = []
            self.series[key]['y'] = []
        pass
        # self.reset_y_max_min()

    def toggle_graph(self):
        """ toggles the graph running bool """
        if self.b_running == True:
            self.b_running = False
        elif self.b_running == False:
            self.b_running = True

    def set_start_time(self):
        self.start_time = datetime.datetime.now()
        print(f"start time set {self.start_time}")

    def get_graph_running_state(self):
        """ returns the running state """
        return self.b_running

    def start_graph(self):
        self.logger.debug('start graph')
        self.b_running = True
        self.start_time = datetime.datetime.now()
        """if graph has been paused, restart it""" 
        pass

    def unpause_graph(self):
        self.logger.debug('unpause graph')
        self.b_running = True
        """if graph has been paused, restart it""" 
        pass

    def pause_graph(self):
        # self.logger.debug('pause graph')
        self.b_running = False
        """ if graph is running, stop it where it is, but keep the data """

    def save_graph(self):
        """ opens a filedialog to choose a save place and filename, and then saves
        a png of the graph """
        self.pause_graph()
        filename = easyfiledialogs.get_path_to_save_file(default_filename = easyfiledialogs.create_default_filename('','png'))
        self.fig.savefig(filename, dpi=200)
        self.unpause_graph()
        pass

    def set_autoscale_y_on(self):
        self.autoscale_y_on = True

    def set_autoscale_y_off(self):
        self.autoscale_y_on = False
    
    def set_autoscale_x_on(self):
        self.autoscale_x_on = True

    def set_autoscale_x_off(self):
        self.autoscale_x_on = False

    """ Methods for setting data """

    def limit_series_width(self, name):
        if (len(self.series[name]['x']) > self.graph_width):
            del self.series[name]['x'][0]
            del self.series[name]['y'][0]

    def add_xy_point(self, name, x_point, y_point):
        self.series[name]['x'].append(x_point)
        self.series[name]['y'].append(y_point)
        self.limit_series_width(name)

    def add_y_point(self, name, y_point):
        if (self.start_time == None):
            self.set_start_time()

        time_value_s = self.get_elapsed_time()
        self.series[name]['x'].append(time_value_s)
        self.series[name]['y'].append(y_point)
        self.limit_series_width(name)

    def update_graph(self):
        """ directly sets the graph, using either external data or the classes'
        internal x_data and y_data variables if called by the graph_update_timer method"""

        if self.b_running:
            self.logger.debug("graph running")
            if self.b_graph_created: # if it's not a new line
                self.logger.debug("writing to graph")
                for key,item in self.series.items():
                    self.lines[key][0].set_data(item['x'],item['y'])
                # self.update_y_max_min(dataset_y)                
                # self.ax.set_ylim(self.min_y_value - abs(0.2*self.min_y_value), self.max_y_value + 0.2*self.max_y_value) # don't need to resize x axis, as this is controlled by the dataset width
                    if item['secondary_axis'] == False:
                        self.ax.axes.relim() # redraws the axes to account for any change in limits
                        self.ax.autoscale_view()
                    else:
                        self.ax2.axes.relim() # redraws the axes to account for any change in limits
                        self.ax2.autoscale_view()

            else: # if it is a new line
                self.logger.debug("Create New Graph")
                self.b_graph_created = True
                self.set_start_time()
                for key,item in self.series.items():
                    self.logger.debug('adding line')
                    if item['secondary_axis'] == False:
                        self.logger.debug(f'{key}: primary')
                        self.lines[key] = self.ax.plot(item['x'], item['y'], label=item['label']) # draw the lines in the series
                    else:
                        self.logger.debug(f'{key}: secondary')
                        # self.ax2 = self.ax.twinx()
                        self.lines[key] = self.ax2.plot(item['x'], item['y'], label=item['label']) # draw the lines in the series
                    
        self.canvas.draw()

    def graph_update_timer(self, update_period):
        """ periodically updates the graph using the data set seperately"""
        self.update_graph()
        root.after(update_period,self.graph_update_timer,update_period)

    """
    - [ ] - TODO set maximum graph width function
                    if (len(x_coords) > 0):
                    x_coords.append(x_coords[-1] + 1) # add the next value to the x_coords, note that this should probably be elapsed time
                else:
                    x_coords.append(0)
                if (len(y_coords_v1) > graph_width): # if the dataset length is greater than the maximum size, remove the first value. this provides a FIFO buffer of values
                    del y_coords_v1[0]
                    del y_coords_v2[0]
                    del x_coords[0]
    """


"""
- [ ] TODO - update the min max values for each series
"""

    # def update_y_max_min(self, this_y_data):
    #     # todo - READ ALL Y DATA in one axis (so primary/secondary) and find the maximum
    #     # max(series[key]['y]) = max_y_value

    #     # update max y
    #     if len(this_y_data) > 2:
    #         # print('update')
    #         if (max(this_y_data) > self.max_y_value):
    #             # print('max update')
    #             self.max_y_value = max(this_y_data)

    #         if (min(this_y_data) < self.min_y_value):
    #             # print('min update')
    #             self.min_y_value = min(this_y_data)

    #     elif len(this_y_data) <= 2:
    #         # print('set')
    #         self.max_y_value = this_y_data[0]
    #         self.min_y_value = this_y_data[0]
    #     # else:
    #     #     print('pass')
    #     #     pass

    #     # print(f'max x: {self.max_y_value}, min x: {self.min_y_value}, {max(this_y_data)}, {min(this_y_data)}')  
    #     # 

    # def reset_y_max_min(self):
    #     self.max_y_value = self.min_y_value      # note, this is a dirty hack until i rearrrange how the library handles data 

    # def update_x_max_min(self):
    #     # update max x vals
    #     if (len(self.x_data) > 0):
    #         if max(self.x_data) > self.max_x_value:
    #             self.max_x_value = max(self.x_data)

    #         if min(self.x_data) < self.min_x_value:
    #             self.min_x_value = min(self.x_data)
    #     else:
    #         pass

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                          Graph Controls Script
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class tkGraphControls(tk.Frame):
    def __init__(self, parent, graph, **kwargs):
        tk.Frame.__init__(self, parent, kwargs)

        self.logger = logging.getLogger(f"{__name__}")

        self.graph = graph

        self.graph_button_strip = tk.Frame(parent)

        self.btn_reset = tk.Button(self.graph_button_strip, text='Reset Graph', command=self.graph.reset_graph)
        self.btn_reset.pack(side='left')

        self.btn_save_graph = tk.Button(self.graph_button_strip, text='Save Graph', command=self.graph.save_graph)
        self.btn_save_graph.pack(side='left')

        self.lbl_graph_width = tk.Label(self.graph_button_strip, text='Graph time [s]', justify='left')
        self.lbl_graph_width.pack(side='left')
        
        self.cbo_graph_width = ttk.Combobox(self.graph_button_strip)
        self.cbo_graph_width['values'] = (5,10,60,180,300,600,3600)
        self.cbo_graph_width.current(5)
        self.set_graph_width('')
        self.cbo_graph_width.pack(side='left')
        self.cbo_graph_width.bind('<<ComboboxSelected>>', self.set_graph_width)

    def set_graph_width(self, event):
        self.graph.set_graph_width(int(self.cbo_graph_width.get()))
        self.logger.debug(f"graph width set to {int(self.cbo_graph_width.get())}")

        """ Tkinter layout methods """    
    def grid(self, **kwargs):#row, column):
        self.graph_button_strip.grid(kwargs)#row=row,column=column)#, side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def pack(self, **kwargs):
        self.graph_button_strip.pack(kwargs)#(side=Tk.TOP, fill=Tk.BOTH, expand=1)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                          Demonstration Code
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

if __name__=="__main__":

    # def create_sin_curve(phase):
    #     t = arange(0.0, 3.0, 0.01)
    #     s = sin(2*pi*t + phase)
    #     phase += 0.1
    #     # self.update_graph("test",t,s)
    #     return phase, [t,s]

    def pause_button_clicked():
        plot.toggle_graph()
        if plot.get_graph_running_state() == True:
            button1['text'] = 'PAUSE'
        else:
            button1['text'] = 'START'

    def set_test_graph_width(event):
        plot.set_graph_width(int(cbo_graph_width.get()))
        print(f"graph width set to {int(cbo_graph_width.get())}")

    def main_loop():
        global phase
        global sin_data

        # plot.add_xy_point('random',phase,random.randint( 0 , 10 ))
        # plot.add_xy_point('sin',phase, random.randint( 11 , 20 ) )
        # plot.add_xy_point('secondary',phase, random.randint( 0 , 100 ) )

        plot.add_y_point('random', random.randint( 0 , 10 ))
        plot.add_y_point('sin', random.randint( 11 , 20 ) )
        plot.add_y_point('secondary', random.randint( 0 , 100 ) )

        plot.update_graph() #.set_graph_data(sin_data[0], sin_data[1])
        # plotB.set_graph_data(rand_x, rand_y)

        # # changes background color based on max value, for an alert
        # if max(rand_y) >= 10:
        #     plotB.set_bg_color('red')
        #     print('RED')
        # else:
        #     plotB.set_bg_color('green')
        # # plot.update_graph(sin_data[0], sin_data[1])
        # # plotB.update_graph(rand_x, rand_y)

        phase += 1

        root.after(250, main_loop)


    root = tk.Tk()

    plot = tkGraphMultiLine(root)
    # plotB = tkGraph(root)
    plot.set_xlabel('Time [s]')
    plot.add_series(name = 'random', label = 'Random Data')
    plot.add_series(name = 'sin', label = 'Sine Curve')
    plot.add_series(name= 'secondary', label='2ndary axis', secondary_axis=True)

    plot.set_title('random line')
    plot.set_ylabel('RANDOM')
    plot.set_secondary_ylabel('also RANDOM')
    # plot.set_color('red')
    plot.set_grid_lines(color='navy', axis='x')
    plot.add_legend()
        
    button1 = tk.Button(root,text='PAUSE', command=pause_button_clicked)
    
    plot.pack()
    # plotB.grid(row=1,column=0)
    button1.pack()

    graph_button_strip = tk.Frame(root)
    btn_reset = tk.Button(root, text='Reset Graph', command=plot.reset_graph)
    btn_reset.pack(side='left')
    btn_save_graph = tk.Button(root, text='Save Graph', command=plot.save_graph)
    btn_save_graph.pack(side='left')
    lbl_graph_width = tk.Label(root, text='Graph time [s]', justify='left')
    lbl_graph_width.pack(side='left')
    cbo_graph_width = ttk.Combobox(graph_button_strip)
    cbo_graph_width['values'] = (3,60,180,300,600,3600)
    cbo_graph_width.current(1)
    cbo_graph_width.pack(side='left')
    cbo_graph_width.bind('<<ComboboxSelected>>', set_test_graph_width)
    set_test_graph_width('')

    graph_button_strip.pack()
    
    sin_data = [ [] , [] ]

    phase = 0
    rand_x = [i for i in range(10)]
    rand_y = [0 for i in range(10)]

    main_loop()

    root.mainloop()