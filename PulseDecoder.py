import board
import pulseio
import adafruit_irremote
import PulseReader
import time
import PulseReader

class PulseDecoder:

    def __init__(self, _IR_Pin=board.GP22, _maxlen=75, _idle_state=True, _data_pulse_width=560, _sm_freq=256000, _timeout=2**11-1):
        
        self.__DATA_PULSE_WIDTH = _data_pulse_width
        self.reader = PulseReader.PulseReader(_IR_Pin=_IR_Pin, _sm_freq=_sm_freq, _timeout=_timeout)
    
    def deviationMatch(self, val, expectedVal, ALLOWED_DEVIATION=0.2):
        return abs(val-expectedVal) < val * ALLOWED_DEVIATION

    def checkZero(self, p1, p2):
        return self.deviationMatch(p1, self.__DATA_PULSE_WIDTH) and self.deviationMatch(p2, self.__DATA_PULSE_WIDTH)

    def checkOne(self, p1, p2):
        return self.deviationMatch(p1, self.__DATA_PULSE_WIDTH) and self.deviationMatch(p2, self.__DATA_PULSE_WIDTH * 3)
    
    def decodePulse(self, pulse):

        try:
            code = ""

            #Check 2 start pulses
            if len(pulse) == 2:
                if self.deviationMatch(pulse[0], 9000) and self.deviationMatch(pulse[1], 2250):
                    code = "REPEAT"
                    return code
            if not self.deviationMatch(pulse[0], 9000) and not self.deviationMatch(pulse[1], 4500):
                print("invalid code - Starting pulse error")
                return False

            for i in range(2, len(pulse)-1, 2):
                if (pulse[i] + pulse[i+1]) > self.__DATA_PULSE_WIDTH * 3:
                    if self.checkOne(pulse[i], pulse[i+1]):
                        code = code + "1"
                    else:
                        print(f"Invalid Code - One: {pulse[i+1]} {pulse[i+1]}")
                        return False
                else:
                    if self.checkZero(pulse[i], pulse[i+1]):
                        code = code + "0"
                    else:
                        print(f"Invalid Code - Zero: {pulse[i+1]} {pulse[i+1]}")
                        return False
            return code

        except Exception as e:
            print(e)
            return False
            
    def getCode(self):
        
        tempCode = self.reader.getPulses()
        
        if not tempCode == None:
            return self.decodePulse(tempCode)
        
        return None

if __name__ == "__main__":
    
    decoder = PulseDecoder()

    while True:
    
        decodedCode = decoder.getCode()
    
        if not decodedCode == None:
            print(decodedCode)