# http://www.cnblogs.com/MnCu8261/p/6527360.html
import queue


class Task(object):
	'''
	warpper of generator
	'''
	tid = 0
	def __init__(self, target):
		'''
		:param target: a instance of generator
		'''
		Task.tid += 1
		self.tid = Task.tid # to mark an unique task
		self.target = target
		self.sendval = None

	def run(self):
		return self.target.send(self.sendval)		T


class Scheduler(object):
	"""
	def __init__(self):
		self.task_map = {}
		self.ready = queue.Queue()"""

	def __init__(self):
		self.task_map = {}
		self.ready = queue.Queue()
		self.exit_waiting = {}

	def new(self, target):
		'''
		create a task
		:param target: generator instance
		:return: tid of created task
		'''
		task = Task(target)
		self.task_map[task.tid] = task
		self.schedule(task)
		return task.id

	def schedule(self, task):
		'''
		put task into ready queue
		:param task: Task instatnce
		:return ;
		'''
		self.ready.put(task)
	"""
	def exit(self, tid):
		'''
		process finished task
		:param task: Task instance
		:return:
		'''
		del self.task_map[tid]"""
	def exit(self, tid):
		''' process finished task
		'''
		del self.task_map[tid]
		waiting_tasks = self.exit_waiting.pop(tid, None)
		if waiting_tasks:
			for task in waiting_tasks:
				self.schedule(task)

	def wait_for_exit(self, wait_tid, waiting_task):
		if self.task_map.get(wait_tid, None):
			self.exit_waiting.setdefault(wait_tid, []).append(waiting_task)
			return True
		else:
			return False

	"""def main_loop(self):
		'''start loop
		:return:
		'''
		while True:
			task = self.ready.get()
			try:
				result = task.run()
			except StopIteration:
				self.exit(task.tid)
				continue
			self.schedule(task)"""

	def main_loop(self):
		''' start loop
		:return :
		'''
		while True:
			task = self.ready.get()
			try:
				result = task.run()
				if isinstance(result, SystemCall):
					result.task = task
					result.scheduler = self
					result.handler()
					continue
			except StopIteration:
				self.exit(task.tid)
				continue
			self.schedule(task)



def laundry():
	for i in range(5):
		yield
		print('I am doing the laundry')


def cook():
	for i in range(10):
		yield
		print('I am cooking')


s = Scheduler()
s.new(cook())
s.new(laundry())
s.main_loop()



class SystemCall(object):
	def __init__(self):
		self.task = None
		self.Scheduler = None

	def handler(self):
		pass


class GetTid(SystemCall):
	def __init__(self):
		super().__init__()

	def handler(self):
		self.task.sendval = self.task.tid
		self.scheduler.ready.put(self.task)


def laundry():
	while True:
		tid = yield GetTid()
		print('I am doing the laundry, my tid is ', tid)


def cook():
	for i in range(10):
		tid = yield GetTid()
		print('I am cooking, my tid is ', tid)


s = Scheduler()
s.new(laundry())
s.new(cook())
s.main_loop()


class New(SystemCall):
	def __init__(self, target):
		super().__init__()
		self.target = target

	def handler(self):
		tid = self.scheduler.new(self.target)
		self.task.sendval = tid
		self.scheduler.schedule(self.task)


def foo():
	for i in range(5):
		tid = yield GetTid()
		print('I am foo, my tid is ', tid)


def bar():
	for i in range(10):
		tid = yield GetTid()
		print('I am bar, my tid is ', tid)
	r = yield New(foo())
	if r:
		print('create a new task, the tid is ', r)


s = Scheduler()
s.new(bar())
s.main_loop()


class Kill(SystemCall):
	def __init__(self, tid):
		super().__init__()
		self.kill_tid = tid

	def handler(self):
		target_task = self.scheduler.task_map.get(self.kill_tid, None)
		if target_task:
			target_task.target.close()
			self.task.sendval = True
			self.scheduler.schedule(self.task)


def foo():
	for i in range(5):
		tid = yield GetTid()
		print('I am foo, my tid is ', tid)


def bar():
	for i in range(10):
		tid = yield GetTid()
		print('I am bar, my tid is ', tid)
	r = yield new(foo())
	if r:
		print('create a new task, the tid is', tid)
	yield
	r = yield Kill(r)
	if r:
		print('killed success')


s = Scheduler()
s.new(bar())
s.main_loop()



class TaskWait(SystemCall):
	def __init__(self, wait_tid):
		super().__init__()
		self.wait_tid = wait_tid

	def handler(self):
		r = self.scheduler.wait_for_exit(self.wait_tid, self.task)
		if not r:
			self.scheduler.schedule(self.task)


def foo():
	for i in range(5):
		tid = yield GetTid()
		print('I am foo, my tid is ', tid)


def bar():
	for i in range(10):
		tid = yield GetTid()
		print('I am bar, my tid is ', tid)
	r = yield New(foo())
	if r:
		print('Create a new task, the tid is ', r)
	yield
	r = yield TaskWait(r)
	yield
	if r:
		print('stop bar')


s = Scheduler()
s.new(bar())
s.main_loop()


def handle_client(client, addr):
	while True:
		data = client.recv(65536)
		if not data:
			break
		client.send(data)
	client.close()
	print('client closed')
	yield 


def server(port):
	s = socket.socket()
	s.bind('', port)
	s.listen(5)
	print('server start')
	while True:
		client, addr = s.accept()
		yield New(handle_client(client, addr))


def alive():
	while True:
		print('I\'m alive')
		yield


scheduler = Scheduler()
schedule.new(alive())
schedule.new(server(54000))
schedule.main_loop()


class Scheduler(object):
	"""
	def __init__(self):
		self.task_map = {}
		self.ready = queue.Queue()"""

	def __init__(self):
		self.task_map = {}
		self.ready = queue.Queue()
		self.exit_waiting = {}
		self.read_waiting = {} # fd readable
		self.write_waiting = {} # fd writable

	def wait_for_read(self, fd, task):
		self.read_waiting[fd] = task

	def wait_for_write(self, fd, task):
		self.write_waiting[fd] = task

	def new(self, target):
		'''
		create a task
		:param target: generator instance
		:return: tid of created task
		'''
		task = Task(target)
		self.task_map[task.tid] = task
		self.schedule(task)
		return task.id

	def schedule(self, task):
		'''
		put task into ready queue
		:param task: Task instatnce
		:return ;
		'''
		self.ready.put(task)
	"""
	def exit(self, tid):
		'''
		process finished task
		:param task: Task instance
		:return:
		'''
		del self.task_map[tid]"""
	def exit(self, tid):
		''' process finished task
		'''
		del self.task_map[tid]
		waiting_tasks = self.exit_waiting.pop(tid, None)
		if waiting_tasks:
			for task in waiting_tasks:
				self.schedule(task)

	def wait_for_exit(self, wait_tid, waiting_task):
		if self.task_map.get(wait_tid, None):
			self.exit_waiting.setdefault(wait_tid, []).append(waiting_task)
			return True
		else:
			return False

	"""def main_loop(self):
		'''start loop
		:return:
		'''
		while True:
			task = self.ready.get()
			try:
				result = task.run()
			except StopIteration:
				self.exit(task.tid)
				continue
			self.schedule(task)"""

	def ioloop(self, timeout):
	if self.write_waiting or self.read_waiting:
		r, w, e = select.select(self.read_waiting, self.write_waiting, [], timeout)
		for i in r:
			task = self.read_waiting.pop(i, None)
			if task: 
				self.schedule(task)
		for i in w:
			task = self.write_waiting.pop(i, None)
			if task:
				self.schedule(task)

	def io_task(self):
		while True:
			if self.ready.empty():
				self.ioloop(None)
			else:
				self.ioloop(0)
			yield

	def main_loop(self):
		''' start loop
		:return :
		'''
		self.new(self.io_task())
		while True:
			task = self.ready.get()
			try:
				result = task.run()
				if isinstance(result, SystemCall):
					result.task = task
					result.scheduler = self
					result.handler()
					continue
			except StopIteration:
				self.exit(task.tid)
				continue
			self.schedule(task)


class ReadWait(SystemCall):
	def __init__(self, fd):
		super().__init__()
		self.fd = fd.fileno() or fd

	def handler(self):
		self.scheduler.wait_for_read(self.fd, self.task)


class WriteWat(SystemCall):
	def __init__(self, fd):
		super().__init__()
		self.fd = fd.fileno() or fd

	def handler(self):
		self.scheduler.wait_for_read(self.fd, self.task)



'http://python.jobbole.com/87431/'
"""
操作系统切换线程有很多种原因：
1.另一个优先级更高的线程需要马上被执行（比如处理硬件中断的代码）
2.线程自己想要被挂起一段时间(比如 sleep)
3.线程已经用完了自己时间片，这个时候线程就不得不'再次'进入队列，供调度器调度
"""


"""
Python中 yield 是一个关键词，它可以用来创建协程。
1.当调用 yield value 的时候，这个 value 就被返回出去了，CPU控制权就交给了协程的调用方。调用 yield 之后，如果想要重新返回协程，需要调用Python中内置的 next 方法。
2.当调用 y = yield x 的时候，x被返回给调用方。要继续返回协程上下文，调用方需要再执行协程的 send 方法。在这个列子中，给send方法的参数会被传入协程作为这个表达式的值(本例中，这个值会被y接收到)。
"""

'''
那么，与线程类似，要实现一个协程的库，我们需要这几样东西：

    事件循环 (event loop)。一方面，它类似于 CPU ，顺序执行协程的代码;另一方面，它相当于操作系统，完成协程的调度，即一个协程“暂停”时，决定接下来执行哪个协程。
    上下文的表示。在 Python 中，我们使用 Python 本身支持的生成器 Generator 来代表基本的上下文，但协程链是如何工作的呢?
    上下文的切换。最基础的切换也是通过 Python 生成器的 yeild 加强版语法来完成的，但我们还要考虑协程链的情况。

'''

