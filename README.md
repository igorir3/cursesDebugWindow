# CursesDebug

Does your print slow down the program? It doesn't give enough information, and if it does, then it's not really readable?

Use this library!

With it, you can make a beautiful-looking terminal for logs or\and debug!

And one of the main features! All messages are processed through a parallel process, so that no one will slow down your code!

For example, here is an example, the 1st time to output 10,000 messages using print, and the second, the same output, only using curses-debug

```JSON
Print            : 0.23720622062683105 s
dprint.send()    : 0.05412912368774414 s
Just pass        : 0.0009999275207519531 s 
```

## Installation
```
pip install curses-debug
```
## Description
This is a simple library that extends the work of a typical console through curses and multiprocessing *(I was surprised that this bundle works 3 times faster than the usual print XD)*

There are many functions, but I'll start in order: 

To begin with, I declare the debug window class:

`dprint = curses_debug()`

Let's talk about the arguments right away:
>`colors` - accepts a dict with a description of all colors 
>```Python
>{
>"INFO" : (0, 153, 0),
>"WARN" : (204, 192, 0),
>"ERRO" : (153, 0, 0),
>"CRIT" : (255, 0, 0),
>"SELECTION" : (255, 255, 255),
>"UNSELECTION" : (0, 0, 0)
>}
>```
>`default` - the default code status value
> 
> The next step is more complicated: by default, the system of monitors freezes (When the console freezes for a long time) have two mods: lite and burn. It is determined which type should be included by the number of elements in the buffer. The differences in the modes are only in the number of messages that will be processed.
>
> `min_buffer_size` - number of messages to be processed at a time in lite mode
>
> `max_buffer_size` - number of messages to be processed at a time in burn mode
>
>`max_buffer_size_threshold` - the number of messages in the buffer needed to enable burn mode
>
>
>`time_function` - A function for writing time. The default value is: `lambda : time.strftime("%H:%M:%S", time.localtime()))`

This is used to send messages:
```Python
dprint.send("Hello World")
```
Arguments:
> 1st positional - text for output, if you do not enter the text, then it will become
>
> `status` - status code. If it is not assigned or is not correctly equal to the default value (see `default'). 0 - INFO; 1 - WARN; 2 - ERRO; 3 - CRIT
>
> `desc` - description of the output.
>
>If you enter `str`, it will simply output it (Use `\n` to split into several lines).
>
>If you enter `dict` it will output in the format *KEY : VALUE*
>
>If you enter `list`, it will simply list all the values through Enter
>
>`replaceable` - If set to True, then after the next message is output, it will be deleted (Similar to `print("", end="\r")`)

This command sets a temporary timeout:
```Python
dprint.waitforend(1)
```

After you have entered this command, the console will ONLY receive messages (Without updates of the GUI), and as soon as there are no messages for the specified time (in seconds), the program will continue its execution as if nothing had happened.

To clear the console:
```Python
dprint.clear()
```

To get the buffer size, you can use one of the methods:
```Python
dprint.buffer_size()
len(dprint)
```

To generate "logs" in the form of json files, use this:
```Python
dprint.genJson()
```
> Accepts only `Name` as an argument in the form of a `str` string (By default, `Log.json`)

The script also has a couple of Easter eggs that you can look for for fun (>o<)

## Control
Стрелки вверх/вниз - выбор
Стрелки в сторону - включение auto-scroll
После появления сообщения типа `[XX:XX:XX DONE] DONE!` нажмите Enter для выхода