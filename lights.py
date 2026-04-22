import board
import neopixel
import time

NUM_LEDS = 45
PIN = board.D10
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(PIN, NUM_LEDS, brightness=0.5, auto_write=False, pixel_order=ORDER)
pixels.fill((80, 150, 150))
pixels.show()

print("Lights ON Please!, Ctrl+C to quit")

try:
	while True:
		time.sleep(1)
except KeyboardInterrupt:
	pixels.fill((0,0,0))
	pixels.show()
	print("Lights OFF")



