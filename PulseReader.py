import board
import rp2pio
import adafruit_pioasm
import array

class PulseReader:
    
    def __init__(self, _sm_freq=256000, _timeout=2**12, _IR_Pin=board.GP22):
        self.name = "Pulse Reader"
        self.smFrequency = _sm_freq
        self.pulse_timeout = _timeout-1
        self.pulse_code = test = """
            setup:
                mov osr ~null
                out x, {}
                mov y x
            wait_low:
                jmp pin wait_low
                jmp while_low
            while_low:
                jmp pin while_high
                jmp x-- while_low
                jmp timeout
            while_high:
                jmp pin still_high
                jmp write
            still_high:
                jmp y-- while_high
                jmp timeout
            write:
                in x, 32
                push
                in y, 32
                push
                jmp setup
            timeout:
                mov isr ~null
                push
                jmp setup
            """.format(len(bin(self.pulse_timeout))-2)

        self.sm = rp2pio.StateMachine(
            adafruit_pioasm.assemble(self.pulse_code),
            frequency=self.smFrequency,
            jmp_pin=_IR_Pin
        )
                    
        self.pulseBuffer = array.array("L", [0])
        self.__codeReady = False
        self.codeBuffer = []
        
    def convertToMS(self, code):
        
        return [int(i * 2 * 1000000 / self.smFrequency) for i in code]
        
    def getPulses(self):
        if self.sm.in_waiting:
            self.sm.readinto(self.pulseBuffer)
            if self.pulseBuffer[0] == 0xffffffff and len(self.codeBuffer):
                rawCode = self.codeBuffer.copy()
                self.codeBuffer = []
                return self.convertToMS(rawCode)
            else:
                self.codeBuffer.append(self.pulse_timeout - self.pulseBuffer[0])
        
        return None

if __name__ == "__main__":
    
    
    reader = PulseReader()
    
    while True:
        
        raw_pulses = reader.getPulses()
        
        if not raw_pulses == None:
            print(raw_pulses)