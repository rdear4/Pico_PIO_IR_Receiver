# Raspberry Pi Pico PIO IR Receiver

---
### Description

***Note: Due to constraints of other parts of the main project, I wrote this in CircuitPython. I plan to go back at some point and write a version MicroPython to take advantage of multiple cores and then upate the CircuitPython version when multicore threading is added.***

Two classes for working with NEC protocol IR codes. One is responsible for getting pulses from the IR Receiver via a PIO state machine.

The other takes those pulses and converts them to binary and returns the 32bit binary string

Each class has some a small example in the `main` section to show how to use them outside of another program if needed. This could be done for inspecting the pulses directly from the IR receiver or also inspecting the binary string that's returned from a set of pulses. Could be used for getting the raw binary for each button on a remote.

### Background

I'm currently working on an LED strip isntallation for underneath my son's lofted bed. In the interest of using existing components and learning something new, I decided to make it so that the colors, brightness and patterns could be controlled using an old TV remote control.

I started by using an existing Adafruit library for CircuitPython, which I found from this [guide](https://learn.adafruit.com/ir-sensor/circuitpython) on their Learn site.

I foudn out that the basic implementation demoed in the example code blocks the main loop until it gets pulses from the IR receiver. That means that any other code (Web server, LED animations, other external inputs) would be halted until pulses came in.

> Turns out that there is a constructor that returns a non-blocking pulse decoder, but I didn't find that until I had already got it in my head to use the PIO on the Pico receive the pulses.

I also wanted to abstract away most of the logic for decoding pulses so my son can work on coding up what he wants the LEDs to do and not have to worry about working with the IR receiver or the decoding class.

### Usage

In the main loop of you code, you must call the `getCode()` method of the `PulseDecoder` isntance to always check if a new code is available. If one is, it will return a binary string. If one is not available, it will return `None`.

Here is a very simple example:

```python
import PulseDecoder
import time

decoder = PulseDecoder.PulseDecoder()

while True:
    
    decodedCode = decoder.getCode()
    
    if not decodedCode == None:
        print(decodedCode)
```

The state machine assumes the IR receiver is connected to GP22, the state machine's frequency is 256000, and the timeout for assuming a code has ended is 2047. These can be changed by using named parameters when instantiating the `PulseDecoder` like this: 

```python
PulseDecoder(_IR_Pin=board.GP12, _sm_freq=128000, _timeout=2**12)
```

**NOTE:** The timeout of `2**12` or `2048` is equal to half the max number of clock cycles allowed to read a high or low signal. The `PulseReader` will assume once a sinal has been high or low for more than that number of clock cylces, that the code is either complete or something else has gone wrong and returns `0xffffffff` to indicate that the code has ended. At the point, the state machine resets and waits for the next code.