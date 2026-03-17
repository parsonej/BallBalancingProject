import curses
import time

def main(stdscr):
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.clear()
    stdscr.addstr(0, 0, "Press WASD to move, ESC to quit.")

    xset = 0
    yset = 0

    while True:
        try:
            key = stdscr.getch()
            if key != -1:
                # Map keys
                if key == 27:  # ESC key
                    break
                elif key in [ord('w'), ord('W')]:
                    xset = 10
                elif key in [ord('s'), ord('S')]:
                    xset = -10
                else:
                    xset = 0

                if key in [ord('d'), ord('D')]:
                    yset = 10
                elif key in [ord('a'), ord('A')]:
                    yset = -10
                else:
                    yset = 0

                stdscr.addstr(2, 0, f"xset={xset} yset={yset}   ")
            else:
                xset = 0
                yset = 0

            # Here, you can call your servo.setangle(xPIN, xset), etc.

            stdscr.refresh()
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

curses.wrapper(main)
