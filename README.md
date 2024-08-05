
Python Example : 

``` Python
from curses_debug import curses_debug

if __name__ == '__main__':
    dprint = curses_debug()
    dprint.send("TEST") # Displaying a message
    dprint.send("TEST", desc="DESC") # Displaying a message with a description (str, list, dict)
    dprint.send("TEST", status=1) # Displaying a message with a special status (0 - INFO, 1 - WARN, 2 - ERRO, 3 - CRIT)
    dprint.send("TEST \", replace_prev = True) # Displaying a temporary message. If you use this command again, this message will be deleted
```
