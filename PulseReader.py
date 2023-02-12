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
                mov osr ~null       ;Copy 0xffffffff to output shift register (OSR)
                out x, {}           ;Shift n number of bits to X register - n is determined by the timeout value passed in as a parameter
                                    ;to PulseReader. 2**12 - 1 => 2047 => 0b11111111111 => 11bits
                mov y x             ;Copy value that is now in the x register over to the y register
            wait_low:
                jmp pin wait_low    ;Default state of IR receiver is HIGH. If the value of the pin stays high, loop back to beginning
                                    ;of wait_low subroutine. If it goes LOW, move to next instruction
                jmp while_low       ;Jump to while_low subroutine
            while_low:
                jmp pin while_high  ;The pin connected to IR Receiver is now LOW indicating it has received a signal from the remote.
                                    ;Once pin goes HIGH, we move to the while_high subroutine otherwise we continue to next instruction
                jmp x-- while_low   ;If the X register is not zero, decrement 1 from its value and jump back to top of while_low subroutine.
                                    ;The timeout is reached once the value in the X register reaches 0. If the X register reaches 0, move 
                                    ;to next instruction
                jmp timeout         ;Jump to the timeout subroutine
            while_high:
                jmp pin still_high  ;While the pin is HIGH, jump to still_high subroutine. Once it goes back to LOW, go to next instruction
                jmp write           ;Jump to write subroutine
            still_high:
                jmp y-- while_high  ;While the Y register is not 0, decrement the Y register by 1 and jump to while_high subroutine. Once it
                                    ;hits zero, jump to the timeout subroutine
                jmp timeout         ;Jump to timeout
            write:
                in x, 32            ;Shift all the bits in the X register to the Input Shift Register (ISR)
                push                ;Push the contenst of the ISR to the RX FIFO so the main program can receive it. PUSH clears the ISR
                in y, 32            ;Shift all the bits in the Y register to the Input Shift Register (ISR)
                push                ;Push the contenst of the ISR to the RX FIFO so the main program can receive it. PUSH clears the ISR
                                    ;This duration of the HIGH and LOW puslses are now in the RX FIFO. The program can determine if those pulses
                                    ;represent a start of code, a zero, a one, or a timeout indicating the IR receiver is not receiving any more
                                    ;pulses from the remote control.
                jmp setup           ;Jump back to setup subroutine to reset the X and Y registers
            timeout:
                mov isr ~null       ;This sets the value of ISR to 0xffffffff
                push                ;Push the ISR to the RX FIFO so the user knows that the code is done
                jmp setup           ;Jump back to setup subroutine to reset the X and Y registers
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
