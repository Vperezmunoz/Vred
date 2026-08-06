# Multithreading example
# source: threading.html

# © 2026 Autodesk, Inc. All rights reserved.

import threading
import time

lock = threading.Lock()
threads = []

def newSceneCallback():
    global threads
    for t in threads:
        t.terminate()
        t.join()

setNewSceneCB(newSceneCallback)

class MyThread(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.index = index
        self.running = True

    def run(self):
        global lock
        while self.running:
            lock.acquire()
            print(('thread #' + str(self.index)))
            #with open('c:/log.txt', 'a') as logf:
            #    logf.write('thread #' + str(self.index) + '\n')
            lock.release()
            time.sleep(1)

    def terminate(self):
        self.running = False

for i in range(0,10):
    t = MyThread(i)
    threads.append(t)
    t.start()
