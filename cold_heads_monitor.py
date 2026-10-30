import socket

class ColdHeadsMonitor(socket.socket):

    adcValues = [None] * 3
    adcPpValues = [None] * 3
    adcGains = ["1/3x","2/3x","2/3x"]
    shiftValues = [None] * 3
    healthStatus = ''

    def errorandexit(self):
        print('ERROR: communication failed; exiting.')
        exit()

    def receiveFrame(self, adc_ch=None):
        frame_rx = ""
        expected_terminator = "*"
        max_buffer_size = 4096
        frame_terminator = ""

        while frame_terminator != expected_terminator:
            frame_rx_dummy = self.recv(max_buffer_size)
            if not frame_rx_dummy:
                self.close()
                self.errorandexit()

            frame_rx += frame_rx_dummy.decode()
            frame_terminator = frame_rx[-1]

        return frame_rx.rstrip(expected_terminator)

    def idn(self):
        frame_tx = "#IDN?*"
        self.send(frame_tx.encode())
        frame_rx = self.receiveFrame()

    def acquire(self):
        frame_tx = "#ACQUIRE*"
        self.send(frame_tx.encode())
        frame_rx = self.receiveFrame()
        return frame_rx

    def getshift(self, shift_code):
        frame_tx = "#GETSHIFT {}*".format(shift_code)
        self.send(frame_tx.encode())
        return float(self.receiveFrame(shift_code))

    def getadc(self, adc_ch):
        frame_tx = "#GETADC {}*".format(adc_ch)
        self.send(frame_tx.encode())
        frame_rx = self.receiveFrame(adc_ch)
        frame_rx = frame_rx.replace('*', '').split(' ')
        frame_rx = [float(x) for x in frame_rx]
        return frame_rx

    def calculatePpValue(self, adc_ch, rx):
        if len(rx) > 0 and rx != 'ERROR':
            diffV = max(rx) - min(rx)
            current = diffV / 100
            return f'{diffV:.3f} -> {current:.3f} A'
        else:
            return 'Invalid data'

if __name__ == "__main__":

    try:
        coldHeadsMonitor = ColdHeadsMonitor()
        coldHeadsMonitor.settimeout(1)
        coldHeadsMonitor.connect(("192.168.150.94", 1666))
        print('TCP connection established.')
    except socket.error as errore:
        coldHeadsMonitor.errorandexit()
