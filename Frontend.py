import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os.path
from tkinter import messagebox
from backend import Backend
import sys

'''
class DialogWindow(tk.Toplevel):

    def __init__(self, master, backend):
        self.backend = backend
        tk.Toplevel.__init__(self, master)

        self.labels = backend.labels

    def get_list(self):
        print("LABELS", self.labels)
        return self.labels
'''
class PlotWindow(tk.Toplevel):
    '''
    this class plots the price trend or bar chart depending on the user choice
    '''

    def __init__(self, master, fct):
        self.master = master
        super().__init__(master)
        fig = plt.figure(1)
        ax = fig.add_subplot(2, 1, 1)
        labels = fct()
        for i in reversed(range(6)):
            lgd = ax.legend(labels[i], loc='upper right', bbox_to_anchor=(0.2, -0.8, 0.5, 0.5))
        text = ax.text(-0.5, 1.05, "", transform=ax.transAxes)
        ax.set_title("Greenhouse Gases Linear Regression")
        ax.grid('on')
        fig.savefig('savedfig', bbox_extra_artists=(lgd, text), bbox_inches='tight')
        fct
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid()
        canvas.draw()


class MainWindow(tk.Tk):
    '''
    this class create main window from tk class and catches errors with the opening of the files
    '''

    def __init__(self, *infilenames):
        self.backend = Backend()
        super().__init__()
        self.canvas = tk.Canvas(self, height=700, width=800)
        self.canvas.pack()

        frame = tk.Frame(self.canvas, background='#E5E7E9', border=5)
        frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

        button = tk.Button(frame, text='Linear Regression', background='#CBD7D5', border=5,
                            command=self.displayLinearRegression)
        button.place(relx=0.15, rely=0.5, relwidth=0.7, relheight=0.2)
        button.config(font=("Palatino Linotype", 13, 'bold'))

        button2 = tk.Button(frame, text='Exit', background='#CBD7D5', border=5,
                           command=self.close_program)
        button2.place(relx=0.18, rely=0.8, relwidth=0.5, relheight=0.2)
        button2.config(font=("Palatino Linotype", 13, 'bold'))

        label = tk.Label(frame, text='Linear Regression Graphs \nGreenhouse Gases'' Global Radiative Forcing', background='#2C5881')
        label.place(relx=0.04, rely=0.1, relwidth=1, relheight=0.2)
        label.config(font=("Palatino Linotype", 15, 'bold'), bg='#E5E7E9')


        for file in infilenames:
            if not os.path.exists(file) or not os.path.isfile(file):
                tk.messagebox.showwarning("Error", "Cannot open this file\n(%s)" % file)

    def displayLinearRegression(self):
        '''
        creates a linear regression graph
        '''
        self.backend.create_sql_table()
        self.backend.create_threads()
        self.backend.put_in_queue()
        self.backend.get_item()
        PlotWindow(self, self.backend.linearRegression)

    def displayDialog(self):
        #dWin = DialogWindow(self, self.backend.labels)
        #self.wait_window(dWin)
        #label_list = dWin.get_list()
        pWin = PlotWindow(self, self.backend.linearRegression)
        self.wait_window(pWin)
        self.close_program

    def close_program(self):
        sys.exit()


infileNames = ["co2_mixing.db"]

mainWin = MainWindow(*infileNames)
mainWin.mainloop()
