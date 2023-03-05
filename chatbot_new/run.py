import threading
import os
# 利用多執行緒來同時執行兩個py程式

def run_port_8080():
    os.system('python main_8080.py')


def run_port_8081():
    os.system('python main_8081.py')


threads = []
threads.append(threading.Thread(target=run_port_8080))
threads.append(threading.Thread(target=run_port_8081))

if __name__ == '__main__':
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()