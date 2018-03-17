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


