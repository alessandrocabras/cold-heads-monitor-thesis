import numpy as np
from cold_heads_monitor import *
import pickle
import threading

#-----------------------------------------------------------------------------------------------------------------
def acquire_data(stop_event):

    vectors = []
    filename = 'dataset_06_04_2023.pkl'
    counter = 0

    try:
        coldHeadsMonitor = ColdHeadsMonitor()
        coldHeadsMonitor.settimeout(1)
        coldHeadsMonitor.connect(("192.168.150.94", 1666))
        print ('')
        print ('==================================================')
        print ('SUCCESS, TCP connection created with CHM')
        print ('==================================================')
        print (f'Writing in file {filename}')
        print ('==================================================')
        print ('Press enter to stop')
        print ('')
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

                vectors.append([ch1_vector, ch2_vector, ch3_vector]) #total shape is (n_element, 3, 128)
                
                with open('dataset_06_04_2023.pkl', 'wb') as f:
                    pickle.dump(vectors, f, protocol=pickle.HIGHEST_PROTOCOL)
    
        print(f"\rAcquisizione del campione n. {counter}", end="")
        pass

# Funzione per interrompere il loop
def interrupt_loop(stop_event):
    input()
    print("Acquisizione interrotta")
    stop_event.set()

# Crea una variabile di controllo per interrompere il thread
stop_event = threading.Event()

# Esegue l'acquisizione dei dati in un thread separato
acquisition_thread = threading.Thread(target=acquire_data, args=(stop_event,))
acquisition_thread.start()

# Esegue la funzione per interrompere il loop in un altro thread
interrupt_thread = threading.Thread(target=interrupt_loop, args=(stop_event,))
interrupt_thread.start()

# Attende che l'utente prema il tasto "Invio"
interrupt_thread.join()

# Interrompe l'acquisizione dei dati in modo sicuro
stop_event.set()
acquisition_thread.join()