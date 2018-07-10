# coding:utf-8
import random
import threading
import Queue
import time
import traceback


class ThreadPool(object):
    def __init__(self, thread_num):
        self._num = thread_num
        self._todo = Queue.Queue()
        self._workers = []

        for x in range(self._num):
            self.create_worker()

        self._current = 0
        self._c_lock = threading.RLock()

    def new(self, target, args=()):
        self._todo.put((target, args))

    def create_worker(self):
        t = threading.Thread(target=self._work)
        t.start()
        self._workers.append(t)

    def _work(self):
        while True:
            task = self._todo.get()
            if task == 'bye':
                return

            self._one_start()
            try:
                task[0](*task[1])
            except Exception, e:
                print 'thread pool catch exception %s\n%s' % (str(e), traceback.format_exc())
            self._one_end()

    def join(self):
        while not self._todo.empty() or self._current != 0:
            time.sleep(0.1)
        self._close()

    def _one_start(self):
        self._c_lock.acquire()
        self._current += 1
        self._c_lock.release()

    def _one_end(self):
        self._c_lock.acquire()
        self._current -= 1
        self._c_lock.release()

    def _close(self):
        for x in range(self._num):
            self._todo.put('bye')


def test():
    import time

    lk = threading.RLock()

    def test_func(i):
        for x in range(2):
            time.sleep(random.random())
        lk.acquire()
        print i, ' is over'
        lk.release()

    pl = ThreadPool(5)
    for i in range(20):
        pl.new(test_func, (i,))

    pl.join()
    # close this stupid pool to fucking let pyCharm auto end
    # pool.join()


if __name__ == '__main__':
    test()
