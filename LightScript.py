from rpi_ws281x import PixelStrip, Color
import time

NUM_LEDS = 45
LED_PIN = 10
LED_FREQ_HZ = 800000
LED_DMA = 5
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

strip = PixelStrip(NUM_LEDS, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

print("lights on")

for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(255, 0, 0))  # red

strip.show()

print("Ctrl+C to exit")

try:
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
