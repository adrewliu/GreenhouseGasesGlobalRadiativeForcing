import urllib.request as ur
import requests
from bs4 import BeautifulSoup
import threading
import time
import queue
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from thread import MyThread
import functools
from tkinter import *
from multiprocessing import Process, Queue
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

#window = Tk()


class Backend:
    def __init__(self):
        page = ur.urlopen('https://www.esrl.noaa.gov/gmd/aggi/aggi.html')
        page = requests.get('https://www.esrl.noaa.gov/gmd/aggi/aggi.html')
        soup = BeautifulSoup(page.content, "lxml")
        data = []
        self.years = []
        self.agents_by_year = []
        self.agents = []
        self.names = ["CO2", "CH4", "N2O", "CFC12", "CFC11", "15-minor"]
        self.q = queue.Queue()
        self.co2_list = []
        self.ch4_list = []
        self.n20_list = []
        self.cfc12_list = []
        self.cfc11_list = []
        self.minor15_list = []
        self.x_ticks = []
        self.count = 0
        self.temp = []
        self.queue_lock = threading.Lock()
        self.thread_list = []
        self.labels = []
        self.np_x_ticks = np.array([])
        self.exitFlag = False


        for stuff in soup.find_all('div', class_='table-responsive'):
            for i in range(9, 49):
                nth_tr = (soup.find_all('tr')[i])
                for td in nth_tr.find_all('td'):
                    data.append(td.text)
        #print(data)

        real = [data[index:index + 10] for index in range(0, len(data), 11)]
        for ele in real:
            self.temp = [float(ind) if float(ind) else 0 for ind in ele]
            self.agents_by_year.append(self.temp[1:7])
            self.years.append(int(self.temp[0]))
        for y in range(len(self.agents_by_year)):
            print("Agents By Rows, Year:", self.years[y], "Values:", self.agents_by_year[y])

        for rows in range(len(self.agents_by_year[self.count])):
            self.temp = []
            while self.count < len(self.agents_by_year):
                self.temp.append(self.agents_by_year[self.count][rows])
                #print("Year:", self.years[self.count], "   Column:", self.names[rows], "      value:", self.agents_by_year[self.count][rows])
                self.count += 1
            self.agents.append(self.temp)
            if self.count == len(self.agents_by_year):
                self.count = 0
        for i in range(6):
            data_list = [list(zip(self.names, self.agents))]
        print('\n')
        for d in data_list[0]:
            print("Agents By Columns (Greenhouse Gases): ", d)
        # for l in range(len(self.agents)):
        #   self.agents[l].insert(0, self.years[l])
        # print(self.agents)
        self.np_agents = np.array(self.agents)
        print(self.np_agents)
        #self.np_x_ticks = np.array(self.x_ticks)
        self.np_names = np.array(self.years)


    def create_sql_table(self):
        self.conn = sqlite3.connect("co2_mixing.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("DROP TABLE IF EXISTS co2_mixing;")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS co2_mixing (co2 TEXT, ch4 TEXT, n20 TEXT, cfc12 TEXT, cfc11 TEXT, minor15 TEXT);")

        for values in self.agents_by_year:
            self.cursor.execute(
                "INSERT INTO co2_mixing (co2, ch4, n20, cfc12, cfc11, minor15) VALUES (?, ?, ?, ?, ?, ?)",
                (values[0], values[1], values[2], values[3], values[4], values[5]))
        self.conn.commit()
        #self.create_threads()

    def linearRegression(self):
        '''
        loop_once = 0
        if loop_once == 0:
            self.create_sql_table()
            self.create_threads()
            self.put_in_queue()
            self.get_item()
            loop_once += 1
        '''
        def estimate_coef(x, y):
            # number of observations/points
            #print(x, y)
            n = np.size(x)

            # mean of x and y vector
            m_x, m_y = np.mean(x), np.mean(y)

            # calculating cross-deviation and deviation about x
            SS_xy = np.sum(y * x) - n * m_y * m_x
            SS_xx = np.sum(x * x) - n * m_x * m_x

            # calculating regression coefficients
            b_1 = SS_xy / SS_xx
            b_0 = m_y - b_1 * m_x

            return b_0, b_1

        def plot_regression_line(x, y, b):
            # plotting the actual points as scatter plot
            plt.scatter(x, y, color='#DAF7A6', marker="o", s=30)

            # predicted response vector
            #print(x, y)
            y_pred = b[0] + b[1] * x

            # plotting the regression line
            plt.plot(x, y_pred)

            plt.xlabel('Year')
            plt.ylabel('Global Radiative Forcing')

        handles = ['1.', '2.', '3.', '4.', '5.', '6.']
        self.count = 0
        self.np_x_ticks = self.get_data_lists()
        for l in self.np_x_ticks:
            b = estimate_coef(self.np_names, l)
            print("Estimated coefficients: " + self.names[self.count] + "\nb_0 = {}  \
                         #\nb_1 = {}".format(b[0], b[1]))
            self.count += 1
            plot_regression_line(self.np_names, l, b)

            #plot_regression_line(self.np_names, l, b)
        self.labels = [list(zip(handles, self.names)) for n in self.names]
        #self.thread_queue()
        #print(self.labels)
        return self.labels


    def put_in_queue(self):
        self.queue_lock.acquire()
        for t in self.thread_list:
            #print(t.num)
            self.q.put(t)
        self.queue_lock.release()
        #self.get_item()

    def get_item(self):
        count = 0
        while not self.exitFlag:
            while not self.q.empty():
                count += 1
                if count == self.count:
                    break
                item = self.q.get()
                self.put_in_list(item)
                self.q.task_done()
            #if self.q.get():
            last_item = self.q.get()
            self.minor15_list.append(last_item.num)
            #print("eihra", self.get_data_lists())
            #self.linearRegression()
            self.exit_program()

            #p = self.q.get()
            #self.minor15_list.append(p.num)
            #print(self.minor15_list)
            #self.q.join()
            #if self.q.get():
            #last_item = self.q.get()
            #self.minor15_list.append(last_item.num)

            #self.linearRegression()

    def put_in_list(self, item):
        if not self.q.empty():
            if item.threadID == "co2":
                self.co2_list.append(float(item.num))
                #self.x_ticks = self.co2_list
            if item.threadID == "ch4":
                self.ch4_list.append(float(item.num))
                #self.x_ticks = self.ch4_list
            if item.threadID == "n20":
                self.n20_list.append(float(item.num))
                #self.x_ticks = self.n20_list
            if item.threadID == "cfc12":
                self.cfc12_list.append(float(item.num))
                #self.x_ticks = self.cfc12_list
            if item.threadID == "cfc11":
                self.cfc11_list.append(float(item.num))
                #self.x_ticks = self.cfc11_list
            if item.threadID == "minor15":
                self.minor15_list.append(float(item.num))
                #print("minor", self.minor15_list)
            #self.x_ticks = self.minor15_list
        #self.get_data_lists()

    def get_data_lists(self):
        self.x_ticks = [self.co2_list, self.ch4_list, self.n20_list, self.cfc12_list, self.cfc11_list,
                        self.minor15_list]
        y = np.array(self.x_ticks)
        self.np_x_ticks = y.astype(np.float)
        #print(self.x_ticks)
        #print(np.array(self.minor15_list))
        return self.np_x_ticks

    def create_threads(self):
        self.conn = sqlite3.connect('co2_mixing.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM co2_mixing")
        names = ["co2", "ch4", "n20", "cfc12", "cfc11", "minor15"]
        rows = self.cursor.fetchall()

        for row in rows:
            for index in range(len(row)):
                self.count += 1
                print("thread: ", self.count)
                my_thread = MyThread(names[index], row[index], index)
                self.thread_list.append(my_thread)
                #self.q.put(self.queue_lock)
                my_thread.start()
                time.sleep(.01)
            #self.put_in_queue()

    def exit_program(self):
        for t in self.thread_list:
            t.join()
        self.exitFlag = True


'''
def main():
    data = Backend()
    data.create_sql_table()
    data.thread_queue()
    data.put_in_queue()
    #print(data.q.qsize())
    data.get_item()

    #data.linearRegression()
    #print("hi", data.minor15_list)


if __name__ == '__main__':
    main()
'''