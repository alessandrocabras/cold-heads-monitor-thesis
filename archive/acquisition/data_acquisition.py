import numpy as np
from cold_heads_monitor import *
import pickle
import threading

def acquire_data(stop_event):

    vectors = []
    filename = 'dataset_06_04_2023.pkl'
    counter = 0

    try:
        coldHeadsMonitor = ColdHeadsMonitor()
        coldHeadsMonitor.settimeout(1)
        coldHeadsMonitor.connect(("192.168.150.94", 1666))
        print(f'Connected to CHM; recording to {filename}.')
        print('Press Enter to stop.')
    except socket.error as errore:
        coldHeadsMonitor.errorandexit()

    while not stop_event.is_set():
        counter += 1
        rx = coldHeadsMonitor.acquire()
        if(len(rx) > 0):
            if(rx == 'OK'):
                ch1_vector = np.asarray(coldHeadsMonitor.getadc(0))
                ch2_vector = np.asarray(coldHeadsMonitor.getadc(1))
                ch3_vector = np.asarray(coldHeadsMonitor.getadc(2))

                vectors.append([ch1_vector, ch2_vector, ch3_vector])

                with open('dataset_06_04_2023.pkl', 'wb') as f:
                    pickle.dump(vectors, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"\rAcquiring window {counter}", end="")
        pass

def interrupt_loop(stop_event):
    input()
    print("Acquisition stopped")
    stop_event.set()

stop_event = threading.Event()

acquisition_thread = threading.Thread(target=acquire_data, args=(stop_event,))
acquisition_thread.start()

interrupt_thread = threading.Thread(target=interrupt_loop, args=(stop_event,))
interrupt_thread.start()

interrupt_thread.join()

stop_event.set()
acquisition_thread.join()
