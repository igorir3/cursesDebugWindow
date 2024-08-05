import curses
import multiprocessing as mp
import time
import atexit
import sys
import traceback

def create_debug_window(q):
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        stdscr.nodelay(True)
        messages = []
        
        lines, cols = stdscr.getmaxyx()
        lines = lines - 2
        cols = cols - 2

        outputtext = curses.newwin(lines, int((cols / 100) * 70), 1, 1)
        desctext = curses.newwin(lines, int((cols / 100) * 30) - 5, 1, int((cols / 100) * 70) + 5)
        outputtext.box()
        desctext.box()

        choosen = None
        autoscroll = True
        start_index = 0
        DOWN_HOLD = False

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_WHITE) 
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE) 
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK) 

        times = 0
        qsize_holder = 0
        EXIT_HEDLER = False
        while True:
            x = 0
            timer = time.time()
            while True:
                if q.qsize() < 100:
                    if x > 10:
                        break
                else:
                    if x > 1000:
                        break
                try:
                    if len(messages) > 0:
                        if messages[-1][3]:
                            messages[-1] = q.get(block=False)
                        else:
                            messages.append(q.get(block=False))
                    else:
                        messages.append(q.get(block=False))
                        break
                except:
                    break
                    
                x = x + 1

            qsize_holder = round(time.time() - timer, 3) 

            try:
                key = stdscr.getkey()
            except:
                key = None

            if str(key) == "KEY_RESIZE":
                lines, cols = stdscr.getmaxyx()
                curses.resize_term(lines, cols)

                lines = lines - 2
                cols = cols - 2

                del outputtext
                del desctext

                outputtext = curses.newwin(lines, int((cols / 100) * 70), 1, 1)
                desctext = curses.newwin(lines, int((cols / 100) * 30) - 5, 1, int((cols / 100) * 70) + 5)

                stdscr.clear()
                outputtext.clear()
                desctext.clear()
                outputtext.box()
                desctext.box()

                stdscr.addstr(1, 3, f"OUT\t{q.qsize()}      ")
                stdscr.addstr(1, int((cols / 100) * 70) + 8, "DESC")

                stdscr.refresh()
                desctext.refresh()
                outputtext.refresh()

            outputtext.clear()
            desctext.clear()
            outputtext.box()
            desctext.box()

            if str(key) == "KEY_RIGHT" or str(key) == "KEY_LEFT":
                autoscroll = True
                choosen = None
            
            if str(key) == "\n" and EXIT_HEDLER:
                break

            if autoscroll:
                start_index = len(messages) - (lines - 2)
                if start_index < 0: start_index = 0

            if str(key) == "KEY_UP":
                if choosen == None:
                    choosen = len(messages) - 1
                    autoscroll = False
                else:
                    choosen = choosen - 1
                    if choosen < 0: choosen = 0
                    if choosen not in range(start_index, start_index+(lines - 2)):
                        start_index = choosen
            elif str(key) == "KEY_DOWN":
                if choosen != None:
                    choosen = choosen + 1
                    if choosen >= len(messages):
                        choosen = None
                        autoscroll = True
                        DOWN_HOLD = True
                    else:
                        if choosen not in range(start_index, start_index+(lines - 2)):
                            start_index = choosen - (lines - 2) + 1
                        autoscroll = False
                else:
                    if DOWN_HOLD == False:
                        choosen = start_index
            
            if str(key) != "KEY_DOWN":
                DOWN_HOLD = False

            for count_x, x in enumerate(messages[start_index:start_index+(lines - 2)]):
                if start_index + count_x == choosen and choosen != None:
                    if x[2] == 0:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(1))
                    elif x[2] == 1:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(2))
                    elif x[2] == 2:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(3))
                    elif x[2] == 3:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(3))
                    elif x[2] == "EX":
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(1))
                        EXIT_HEDLER = True
                else:
                    if x[2] == 0:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(4))
                    elif x[2] == 1:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(5))
                    elif x[2] == 2:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(6))
                    elif x[2] == 3:
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(6))
                    elif x[2] == "EX":
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(4))
                        EXIT_HEDLER = True

            if choosen is not None:
                if messages[choosen][1] != None:
                    if type(messages[choosen][1]) == str:
                        if len(messages[choosen][1].split("\n")) > 1:
                            for count, x in enumerate(messages[choosen][1].split("\n")):
                                if count + 1 > (lines - 2):
                                    break
                                desctext.addstr(count + 1, 1, str(x)[:(int((cols / 100) * 30) - 7)])
                        else:
                            desctext.addstr(1, 1, str(messages[choosen][1])[:(int((cols / 100) * 30) - 7)])
                    elif type(messages[choosen][1]) == list:
                        for count, x in enumerate(messages[choosen][1]):
                            if count + 1 > (lines - 2):
                                break
                            desctext.addstr(count + 1, 1, str(x)[:(int((cols / 100) * 30) - 7)])
                            
                    elif type(messages[choosen][1]) == dict:
                        for count, x in enumerate(messages[choosen][1].keys()):
                            if count + 1 > (lines - 2):
                                break
                            desctext.addstr(count + 1, 1, f"{x} : {messages[choosen][1][x]}"[:(int((cols / 100) * 30) - 7)])
                            
            desctext.refresh()
            outputtext.refresh()

            stdscr.addstr(0, 3, f"OUT\t{qsize_holder}      ")
            stdscr.addstr(0, int((cols / 100) * 70) + 8, "DESC")
            stdscr.refresh()

            times = times + 1
            time.sleep(0.01)

        curses.endwin()

def exception_def(exc_type, exc_value, tb, q):
    error = traceback.format_exception(exc_type, exc_value, tb)
    while q.full():
        pass
    q.put([f"[{time.strftime("%H:%M:%S", time.localtime())}\tCRIT]  {exc_value}", error, 3, False])

class curses_debug():
    def __init__(self):
        self.queue = mp.Queue()
        sys.excepthook = lambda exc_type, exc_value, tb : exception_def(exc_type, exc_value, tb, self.queue)
        atexit.register(lambda: self.queue.put([f"[{time.strftime("%H:%M:%S", time.localtime())}\tEXIT]  DONE!", "The program has completed its work\nPress Enter for exit", "EX", False]))
        p = mp.Process(target=create_debug_window, args=(self.queue, ))
        p.start()

    def send(self, text, status : int = 0, desc = None, replace_prev = False):
        while self.queue.full():
            pass

        if status == 0:
            self.queue.put([f"[{time.strftime("%H:%M:%S", time.localtime())}\tINFO]  {text}", desc, status, replace_prev])
        if status == 1:
            self.queue.put([f"[{time.strftime("%H:%M:%S", time.localtime())}\tWARN]  {text}", desc, status, replace_prev])
        elif status == 2:
            self.queue.put([f"[{time.strftime("%H:%M:%S", time.localtime())}\tERRO]  {text}", desc, status, replace_prev])
        elif status == 3:
            self.queue.put([f"[{time.strftime("%H:%M:%S", time.localtime())}\tCRIT]  {text}", desc, status, replace_prev])

if __name__ == '__main__':
    pass