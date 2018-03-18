from bisect import insort
from collections import deque
from fib import timed_fib
from functools import partial
from time import time
import selectors
import sys
import types
class sleep_for_seconds(object):
    """
    Yield an object of this type from a coroutine to have it "sleep" for the
    given number of seconds.
    """
    def __init__(self, wait_time):
        self._wait_time = wait_time
class EventLoop(object):
    """
    Implements a simplified coroutine-based event loop as a demonstration.
    Very similar to the "Trampoline" example in PEP 342, with exception
    handling taken out for simplicity, and selectors added to handle file IO
    """
    def __init__(self, *tasks):
        self._running = False
        self._selector = selectors.DefaultSelector()
        # Queue of functions scheduled to run
        self._tasks = deque(tasks)
        # (coroutine, stack) pair of tasks waiting for input from stdin
        self._tasks_waiting_on_stdin = []
        # 什么鬼东西未知， 等待输入的tasks？
        # List of (time_to_run, task) pairs, in sorted order
        self._timers = []
        # Register for polling stdin for input to read
        self._selector.register(sys.stdin, selectors.EVENT_READ)
    def resume_task(self, coroutine, value=None, stack=()):
        # 恢复 task， 被 schedule 调用，参数被 schedule 中提供的参数绑定
        # 根据不同的类型，决定如何更好的 schedule♂ 他。
        # 开始先从生成器中获取一个result， 如果result 是 stdin 类型的话
        # 就将 生成器 和 栈 信息放入 _tasks_waiting_on_stdin中 (coro, stack)
        
        result = coroutine.send(value)
        if isinstance(result, types.GeneratorType):
            self.schedule(result, None, (coroutine, stack))
        elif isinstance(result, sleep_for_seconds):
            self.schedule(coroutine, None, stack, time() + result._wait_time)
        elif result is sys.stdin:
            self._tasks_waiting_on_stdin.append((coroutine, stack))
        elif stack:
            self.schedule(stack[0], result, stack[1])
    def schedule(self, coroutine, value=None, stack=(), when=None):
        """
        Schedule a coroutine task to be run, with value to be sent to it, and
        stack containing the coroutines that are waiting for the value yielded
        by this coroutine.
        """
        # 协调一个将要运行的生成器，可以再发个 value 给他。。
        # 栈信息包含将要返回生成器的这个生成器？
        # schedule 接受 4个参数， coro是生成器， value可以与生成器通信，
        # stack 据说为一个 长度为 2 的元祖类型。 when 是用来搞timer的据说。
        # 用 偏函数给 resume_task 绑了三个参数方便用，生成一个task。
        # Bind the parameters to a function to be scheduled as a function with
        # no parameters.
        task = partial(self.resume_task, coroutine, value, stack)
        if when:
            insort(self._timers, (when, task))
        else:
            self._tasks.append(task)
    def stop(self):
        self._running = False
    def do_on_next_tick(self, func, *args, **kwargs):
        self._tasks.appendleft(partial(func, *args, **kwargs))
    def run_forever(self):
        # 起一个无线循环， _tasks_waiting_on_stdin 啥情况。。
        # 至少应该是个 2 长元祖吧。。0是generator，1是stack信息
        # 有task就调用，感觉是 schedule 调用 resume_task
        # 放入 tasks 中。放入 task 中后，调用获取结果，保存generator与stack
        # 再次将其放回 tasks 队列中， 那这个 stopIteration 在哪里捕捉呢...
        self._running = True
        while self._running:
            # First check for available IO input
            for key, mask in self._selector.select(0):
                line = key.fileobj.readline().strip()
                for task, stack in self._tasks_waiting_on_stdin:
                    self.schedule(task, line, stack)
                self._tasks_waiting_on_stdin.clear()
            # Next, run the next task
            if self._tasks:
                task = self._tasks.popleft()
                task()
            # Finally run time scheduled tasks
            while self._timers and self._timers[0][0] < time():
                task = self._timers[0][1]
                del self._timers[0]
                task()
        self._running = False
def print_every(message, interval):
    """
    Coroutine task to repeatedly print the message at the given interval
    (in seconds)
    """
    # 不存在 IO 问题啊，有啥子优势啊
    while True:
        print("{} - {}".format(int(time()), message))
        yield sleep_for_seconds(interval)
def read_input(loop):
    """
    Coroutine task to repeatedly read new lines of input from stdin, treat
    the input as a number n, and calculate and display fib(n).
    """
    # 这个也不太理解，用 while的 sys.stdin会咋样？
    while True:
        line = yield sys.stdin
        if line == 'exit':
            loop.do_on_next_tick(loop.stop)
            continue
        n = int(line)
        print("fib({}) = {}".format(n, timed_fib(n)))
def main():
    loop = EventLoop()
    hello_task = print_every('Hello world!', 3)
    fib_task = read_input(loop)
    loop.schedule(hello_task)
    loop.schedule(fib_task)
    loop.run_forever()

if __name__ == '__main__':
    main()


# 所谓协程就是在一个线程中切换子进程 ... 


# task() --> 假设这个 task 是 print_every 函数-- > 先 coro.send(value) == 
# next(coro) == next(print_every) !!! 这里的 coro.send(value) 就是实际在调用 print_every 并获取 yield 的返回值了, ,执行完后又将 print_every schedule 回 tasks里
'''http://blog.jobbole.com/103290/'''
