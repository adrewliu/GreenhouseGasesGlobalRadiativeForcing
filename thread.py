import threading
import time
import queue

exitFlag = False
'''

def process_data(threadName, q):
    while not exitFlag:
        if not workQueue.empty():
            queueLock.acquire()
            data = q.get()
            print("%s processing %s" % (threadName, data))
            queueLock.release()
        time.sleep(1)
'''

class MyThread (threading.Thread):
   def __init__(self, threadID, num, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.num = num
      self.counter = counter

   def run(self):
      print ("Starting thread " + self.threadID + ": " + self.num)
      #print_time(self.name, self.counter, 5)
      print ("Exiting thread " + str(self.counter))
'''
threadList = ["CO2", "CH4", "N2O", "CFC12", "CFC11", "15-minor"]
numList = []
queueLock = threading.Lock()
workQueue = queue.Queue(240)
threads = []

# Create new threads

count = 0
for tName in threadList:
    thread = MyThread(tName, workQueue, count)
    threads.append(thread)
    thread.start()
    count += 1

# Fill the queue
queueLock.acquire()
for n in numList:
    workQueue.put(n)
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
exitFlag = True

# Wait for all threads to complete
for t in threads:
    t.join()
print("Exiting Main Thread")
'''

