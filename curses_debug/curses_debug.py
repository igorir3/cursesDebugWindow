import curses
import multiprocessing as mp
import time
import atexit
from datetime import datetime
import sys
import traceback
from random import randint
import json

def create_debug_window(q, colors, min_buffer_size, max_buffer_size, max_buffer_size_treshold):
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

        curses.init_color(curses.COLOR_GREEN,   int((colors["INFO"][0] / 255) * 1000),          int((colors["INFO"][1] / 255) * 1000),          int((colors["INFO"][2] / 255) * 1000))
        curses.init_color(curses.COLOR_YELLOW,  int((colors["WARN"][0] / 255) * 1000),          int((colors["WARN"][1] / 255) * 1000),          int((colors["WARN"][2] / 255) * 1000))
        curses.init_color(curses.COLOR_RED,     int((colors["ERRO"][0] / 255) * 1000),          int((colors["ERRO"][1] / 255) * 1000),          int((colors["ERRO"][2] / 255) * 1000))
        curses.init_color(curses.COLOR_MAGENTA, int((colors["CRIT"][0] / 255) * 1000),          int((colors["CRIT"][1] / 255) * 1000),          int((colors["CRIT"][2] / 255) * 1000))
        curses.init_color(curses.COLOR_WHITE,   int((colors["SELECTION"][0] / 255) * 1000),     int((colors["SELECTION"][1] / 255) * 1000),     int((colors["SELECTION"][2] / 255) * 1000))
        curses.init_color(curses.COLOR_BLACK,   int((colors["UNSELECTION"][0] / 255) * 1000),   int((colors["UNSELECTION"][1] / 255) * 1000),   int((colors["UNSELECTION"][2] / 255) * 1000))


        curses.init_pair(1, curses.COLOR_GREEN,     curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_YELLOW,    curses.COLOR_WHITE) 
        curses.init_pair(3, curses.COLOR_RED,       curses.COLOR_WHITE) 
        curses.init_pair(4, curses.COLOR_GREEN,     curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW,    curses.COLOR_BLACK) 
        curses.init_pair(6, curses.COLOR_RED,       curses.COLOR_BLACK) 

        times = 0
        qsize_holder = 0
        EXIT_HEDLER = False
        while True:
            x = 0
            timer = time.time()
            while True:
                if q.qsize() < max_buffer_size_treshold:
                    if x > min_buffer_size:
                        break
                else:
                    if x > max_buffer_size:
                        break
                try:
                    if len(messages) > 0:
                        if messages[-1][3]:
                            messages[-1] = q.get(block=True, timeout=0.0001)
                        else:
                            messages.append(q.get(block=True, timeout=0.0001))
                    else:
                        messages.append(q.get(timeout=0.0001))
                except:
                    pass

                if len(messages) > 0:
                    if messages[-1][2] == "WAIT":
                        Commandtimeout = messages[-1][0]
                        del messages[-1]
                        try:
                            while True:
                                messages.append(q.get(block=True, timeout=float(Commandtimeout)))
                                if messages[-1][2] == "CLEAR":
                                    del messages[-1]
                                    messages.clear()
                                    break

                                elif messages[-1][2] == "JSON":
                                    Name = messages[-1][0]
                                    del messages[-1]
                                    with open(Name, "+w", encoding="utf-8") as f:
                                        json.dump(messages, f, indent=4 )

                        except Exception as e:
                            break
                    
                    elif messages[-1][2] == "CLEAR":
                        del messages[-1]
                        messages.clear()
                        break

                    elif messages[-1][2] == "JSON":
                        Name = messages[-1][0]
                        del messages[-1]
                        with open(Name, "+w", encoding="utf-8") as f:
                            json.dump(messages, f, indent=4 )

                x = x + 1

            qsize_holder = str(time.time() - timer)[:3]

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
            else:
                outputtext.clear()
                desctext.clear()
                outputtext.box()
                desctext.box()

            if len(messages) > 0:
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
                        else:
                            if choosen not in range(start_index, start_index+(lines - 2)):
                                start_index = choosen - (lines - 2) + 1
                            autoscroll = False

            for count_x, x in enumerate(messages[start_index:start_index+(lines - 2)]):
                if start_index + count_x == choosen and choosen != None:
                    if x[2] == 0:   outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(1))
                    elif x[2] == 1 or x[2] == "CALL": outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(2))
                    elif x[2] == 2: outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(3))
                    elif x[2] == 3: outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(3))
                    elif x[2] == "EX":
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(1))
                        EXIT_HEDLER = True
                    elif x[2] == "RICK":
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(randint(1, 3)))
                else:
                    if x[2] == 0:   outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(4))
                    elif x[2] == 1 or x[2] == "CALL": outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(5))
                    elif x[2] == 2: outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(6))
                    elif x[2] == 3: outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(6))
                    elif x[2] == "EX":
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(4))
                        EXIT_HEDLER = True
                    elif x[2] == "RICK":
                        outputtext.addstr(count_x + 1, 1, str(x[0])[:(int((cols / 100) * 70) - 7)], curses.color_pair(randint(4, 6)))
                    

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

            if len(messages) != 0: 
                a_str = str(time.time() - messages[-1][-1])[:6]
                stdscr.addstr(0, 3, f"OUT\t{qsize_holder} | {a_str[:5] if "." in a_str else " " }    ")
            else:
                stdscr.addstr(0, 3, f"OUT\t{qsize_holder}")
            stdscr.addstr(0, int((cols / 100) * 70) + 8, "DESC")
            stdscr.refresh()

            times = times + 1
            time.sleep(0.01)

        curses.endwin()

def exception_def(exc_type, exc_value, tb, q, time_function):
    error = traceback.format_exception(exc_type, exc_value, tb)
    while q.full():
        pass
    q.put([f"[{time_function()}\tCRIT]  {exc_value}", error, 3, False])

class curses_debug():
    def __init__(self, 
                 colors : dict = {
                     "INFO" : (0, 153, 0),
                     "WARN" : (204, 192, 0),
                     "ERRO" : (153, 0, 0),
                     "CRIT" : (255, 0, 0),
                     "SELECTION" : (255, 255, 255),
                     "UNSELECTION" : (0, 0, 0)},
                 default : int = 0,
                 min_buffer_size : int = 10,
                 max_buffer_size : int = 1000,
                 max_buffer_size_threshold : int = 1000,
                 time_function = lambda : time.strftime("%H:%M:%S", time.localtime())):
        
        for x in colors.keys():
            if max(colors[x]) > 255     : raise SyntaxError("RGB can't be >255")
        if min_buffer_size < 1          : raise SyntaxError("'min_buffer_size' can't be <1")
        if max_buffer_size < 1          : raise SyntaxError("'max_buffer_size' can't be <1")
        if max_buffer_size_threshold < 1 : raise SyntaxError("'max_buffer_size_treshold' can't be <1")
        
        try:
            str(time_function())
        except:
            raise SyntaxError("'time_function' can't transformed to str type")
        
        if str(type(time_function)) != "<class 'function'>":
            time_function = lambda : time_function

        self.queue = mp.Queue()
        self.default = default
        self.time_function = time_function
        sys.excepthook = lambda exc_type, exc_value, tb : exception_def(exc_type, exc_value, tb, self.queue, self.time_function)
        atexit.register(lambda: self.queue.put([f"[{self.time_function()}\tEXIT]  DONE!", "The program has completed its work\nPress Enter for exit", "EX", False]))
        p = mp.Process(target=create_debug_window, args=(self.queue, colors, min_buffer_size, max_buffer_size, max_buffer_size_threshold))
        p.start()

    def send(self, text, status : int = -1, desc : dict | list | str  = None, replaceable : bool = False):
        while self.queue.full():
            pass
        if status not in [0, 1, 2, 3]:
            status = self.default

        if status == 0:     self.queue.put([f"[{self.time_function()}\tINFO]  {text}", desc, status, replaceable, time.time()])
        if status == 1:     self.queue.put([f"[{self.time_function()}\tWARN]  {text}", desc, status, replaceable, time.time()])
        elif status == 2:   self.queue.put([f"[{self.time_function()}\tERRO]  {text}", desc, status, replaceable, time.time()])
        elif status == 3:   self.queue.put([f"[{self.time_function()}\tCRIT]  {text}", desc, status, replaceable, time.time()])
    
    def waitforend(self, timeout : int = 0.1):
        self.queue.put([timeout, None, "WAIT", False, time.time()])

    def clear(self):
        self.queue.put([None, None, "CLEAR", False, time.time()])
    
    def buffer_size(self) -> int:
        return self.queue.qsize()
    def __len__(self) -> int:
        return self.queue.qsize()
    
    def genJson(self, Name : str = "Log.json"):
        self.queue.put([Name, None, "JSON", False, time.time()])

    def genLogs(self, Name : str = "Log.txt"):
        self.queue.put([Name, None, "JSON", False, time.time()])
    
    def __call__(self, *args, **kwargs):
        ls = ['Расцветали яблони и груши,', 'Поплыли туманы над рекой.', 'Выходила на берег Катюша,', 'На высокий берег на крутой.', 'Выходила на берег Катюша,', 'На высокий берег на крутой.', '', 'Выходила, песню заводила,', 'Про степного сизого орла.', 'Про того, которого любила,', 'Про того, чьи письма берегла.', 'Про того, которого любила,', 'Про того, чьи письма берегла.', '', 'Ой ты песня, песенка девичья,', 'Ты лети за ясным солнцем вслед', 'и бойцу на дальнем пограничье', 'От катюши передай привет', 'и бойцу на дальнем пограничье', 'От катюши передай привет.', '', 'Пусть он вспомнит девушку простую,', 'Пусть услышит, как она поет,', 'Пусть он землю бережет родную,', 'А любовь Катюша сбережет.', 'Пусть он землю бережет родную,', 'А любовь Катюша сбережет.', '', 'Расцветали яблони и груши,', 'Поплыли туманы над рекой.', 'Выходила на берег Катюша,', 'На высокий берег на крутой.', 'Выходила на берег Катюша,', 'На высокий берег на крутой.']
        for x in ls:
            self.queue.put([f"[{self.time_function()}\tCALL]  {x}", ["DON'T CALL ME" for x in range(32)], "CALL", False, time.time()])

    def __getattr__(self, name):
        ls = [[68, 101, 115, 101, 114, 116, 32, 121, 111, 117], [79, 111, 104, 45, 111, 111, 104, 45, 111, 111, 104, 45, 111, 111, 104], [72, 117, 114, 116, 32, 121, 111, 117], [], [87, 101, 39, 114, 101, 32, 110, 111, 32, 115, 116, 114, 97, 110, 103, 101, 114, 115, 32, 116, 111, 32, 108, 111, 118, 101], [89, 111, 117, 32, 107, 110, 111, 119, 32, 116, 104, 101, 32, 114, 117, 108, 101, 115, 32, 97, 110, 100, 32, 115, 111, 32, 100, 111, 32, 73, 32, 40, 68, 111, 32, 73, 41], [65, 32, 102, 117, 108, 108, 32, 99, 111, 109, 109, 105, 116, 109, 101, 110, 116, 39, 115, 32, 119, 104, 97, 116, 32, 73, 39, 109, 32, 116, 104, 105, 110, 107, 105, 110, 103, 32, 111, 102], [89, 111, 117, 32, 119, 111, 117, 108, 100, 110, 39, 116, 32, 103, 101, 116, 32, 116, 104, 105, 115, 32, 102, 114, 111, 109, 32, 97, 110, 121, 32, 111, 116, 104, 101, 114, 32, 103, 117, 121], [], [73, 32, 106, 117, 115, 116, 32, 119, 97, 110, 110, 97, 32, 116, 101, 108, 108, 32, 121, 111, 117, 32, 104, 111, 119, 32, 73, 39, 109, 32, 102, 101, 101, 108, 105, 110, 103], [71, 111, 116, 116, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 117, 110, 100, 101, 114, 115, 116, 97, 110, 100], [], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 108, 101, 116, 32, 121, 111, 117, 32, 100, 111, 119, 110], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 114, 117, 110, 32, 97, 114, 111, 117, 110, 100, 32, 97, 110, 100, 32, 100, 101, 115, 101, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 99, 114, 121], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 115, 97, 121, 32, 103, 111, 111, 100, 98, 121, 101], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 116, 101, 108, 108, 32, 97, 32, 108, 105, 101, 32, 97, 110, 100, 32, 104, 117, 114, 116, 32, 121, 111, 117], [], [87, 101, 39, 118, 101, 32, 107, 110, 111, 119, 110, 32, 101, 97, 99, 104, 32, 111, 116, 104, 101, 114, 32, 102, 111, 114, 32, 115, 111, 32, 108, 111, 110, 103], [89, 111, 117, 114, 32, 104, 101, 97, 114, 116, 39, 115, 32, 98, 101, 101, 110, 32, 97, 99, 104, 105, 110, 103, 44, 32, 98, 117, 116, 32, 121, 111, 117, 39, 114, 101, 32, 116, 111, 111, 32, 115, 104, 121, 32, 116, 111, 32, 115, 97, 121, 32, 105, 116, 32, 40, 84, 111, 32, 115, 97, 121, 32, 105, 116, 41], [73, 110, 115, 105, 100, 101, 44, 32, 119, 101, 32, 98, 111, 116, 104, 32, 107, 110, 111, 119, 32, 119, 104, 97, 116, 39, 115, 32, 98, 101, 101, 110, 32, 103, 111, 105, 110, 103, 32, 111, 110, 32, 40, 71, 111, 105, 110, 103, 32, 111, 110, 41], [87, 101, 32, 107, 110, 111, 119, 32, 116, 104, 101, 32, 103, 97, 109, 101, 44, 32, 97, 110, 100, 32, 119, 101, 39, 114, 101, 32, 103, 111, 110, 110, 97, 32, 112, 108, 97, 121, 32, 105, 116], [], [65, 110, 100, 32, 105, 102, 32, 121, 111, 117, 32, 97, 115, 107, 32, 109, 101, 32, 104, 111, 119, 32, 73, 39, 109, 32, 102, 101, 101, 108, 105, 110, 103], [68, 111, 110, 39, 116, 32, 116, 101, 108, 108, 32, 109, 101, 32, 121, 111, 117, 39, 114, 101, 32, 116, 111, 111, 32, 98, 108, 105, 110, 100, 32, 116, 111, 32, 115, 101, 101], [], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 108, 101, 116, 32, 121, 111, 117, 32, 100, 111, 119, 110], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 114, 117, 110, 32, 97, 114, 111, 117, 110, 100, 32, 97, 110, 100, 32, 100, 101, 115, 101, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 99, 114, 121], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 115, 97, 121, 32, 103, 111, 111, 100, 98, 121, 101], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 116, 101, 108, 108, 32, 97, 32, 108, 105, 101, 32, 97, 110, 100, 32, 104, 117, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 108, 101, 116, 32, 121, 111, 117, 32, 100, 111, 119, 110], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 114, 117, 110, 32, 97, 114, 111, 117, 110, 100, 32, 97, 110, 100, 32, 100, 101, 115, 101, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 99, 114, 121], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 115, 97, 121, 32, 103, 111, 111, 100, 98, 121, 101], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 116, 101, 108, 108, 32, 97, 32, 108, 105, 101, 32, 97, 110, 100, 32, 104, 117, 114, 116, 32, 121, 111, 117], [], [79, 111, 104, 32, 40, 71, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112, 41], [79, 111, 104, 45, 111, 111, 104, 32, 40, 71, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112, 41], [79, 111, 104, 45, 111, 111, 104], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 44, 32, 110, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 40, 71, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112, 41], [79, 111, 104, 45, 111, 111, 104], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 44, 32, 110, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 40, 71, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112, 41], [], [87, 101, 39, 118, 101, 32, 107, 110, 111, 119, 110, 32, 101, 97, 99, 104, 32, 111, 116, 104, 101, 114, 32, 102, 111, 114, 32, 115, 111, 32, 108, 111, 110, 103], [89, 111, 117, 114, 32, 104, 101, 97, 114, 116, 39, 115, 32, 98, 101, 101, 110, 32, 97, 99, 104, 105, 110, 103, 44, 32, 98, 117, 116, 32, 121, 111, 117, 39, 114, 101, 32, 116, 111, 111, 32, 115, 104, 121, 32, 116, 111, 32, 115, 97, 121, 32, 105, 116, 32, 40, 84, 111, 32, 115, 97, 121, 32, 105, 116, 41], [73, 110, 115, 105, 100, 101, 44, 32, 119, 101, 32, 98, 111, 116, 104, 32, 107, 110, 111, 119, 32, 119, 104, 97, 116, 39, 115, 32, 98, 101, 101, 110, 32, 103, 111, 105, 110, 103, 32, 111, 110, 32, 40, 71, 111, 105, 110, 103, 32, 111, 110, 41], [87, 101, 32, 107, 110, 111, 119, 32, 116, 104, 101, 32, 103, 97, 109, 101, 44, 32, 97, 110, 100, 32, 119, 101, 39, 114, 101, 32, 103, 111, 110, 110, 97, 32, 112, 108, 97, 121, 32, 105, 116], [], [73, 32, 106, 117, 115, 116, 32, 119, 97, 110, 110, 97, 32, 116, 101, 108, 108, 32, 121, 111, 117, 32, 104, 111, 119, 32, 73, 39, 109, 32, 102, 101, 101, 108, 105, 110, 103], [71, 111, 116, 116, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 117, 110, 100, 101, 114, 115, 116, 97, 110, 100], [], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 108, 101, 116, 32, 121, 111, 117, 32, 100, 111, 119, 110], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 114, 117, 110, 32, 97, 114, 111, 117, 110, 100, 32, 97, 110, 100, 32, 100, 101, 115, 101, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 99, 114, 121], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 115, 97, 121, 32, 103, 111, 111, 100, 98, 121, 101], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 116, 101, 108, 108, 32, 97, 32, 108, 105, 101, 32, 97, 110, 100, 32, 104, 117, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 108, 101, 116, 32, 121, 111, 117, 32, 100, 111, 119, 110], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 114, 117, 110, 32, 97, 114, 111, 117, 110, 100, 32, 97, 110, 100, 32, 100, 101, 115, 101, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 99, 114, 121], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 115, 97, 121, 32, 103, 111, 111, 100, 98, 121, 101], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 116, 101, 108, 108, 32, 97, 32, 108, 105, 101, 32, 97, 110, 100, 32, 104, 117, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 103, 105, 118, 101, 32, 121, 111, 117, 32, 117, 112], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 108, 101, 116, 32, 121, 111, 117, 32, 100, 111, 119, 110], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 114, 117, 110, 32, 97, 114, 111, 117, 110, 100, 32, 97, 110, 100, 32, 100, 101, 115, 101, 114, 116, 32, 121, 111, 117], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 109, 97, 107, 101, 32, 121, 111, 117, 32, 99, 114, 121], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 115, 97, 121, 32, 103, 111, 111, 100, 98, 121, 101], [78, 101, 118, 101, 114, 32, 103, 111, 110, 110, 97, 32, 116, 101, 108, 108, 32, 97, 32, 108, 105, 101, 32, 97, 110, 100, 32, 104, 117, 114, 116, 32, 121, 111, 117]]
        for x in ls:
            self.queue.put([f"[{self.time_function()}\tRICK]  {"".join(list(map(chr, x)))}", "DON'T\nMAKE\nMISTAKES\nIN\nFUNCTION\nNAMES\n", "RICK", False, time.time()])
            time.sleep(0.33)
    

if __name__ == '__main__':
    str42 = " ".join(["42" for x in range(0, 16)])
    dprint = curses_debug(min_buffer_size=100, max_buffer_size=10000)
    while True:
        dprint.send(str42)
        time.sleep(0.1)