import logging

log = logging.getLogger(__name__)

from concurrent import futures
import threading, multiprocessing, functools, traceback
import attr

from rhombus.lib.utils import random_string, cerr

@attr.s
class ProcUnit(object):
	taskid = attr.ib(default=-1)
	proc = attr.ib(default=None)	# future object
	uid = attr.ib(default=0)		# user uid
	pid = attr.ib(default=-1)		# process id (or multiproc id)
	wd = attr.ib(default='')		# proc working directory
	time_queue = attr.ib(default=None)
	time_start = attr.ib(default=None)
	time_stop = attr.ib(default=None)
	status = attr.ib(default='Q')	# Q - queue, R - running, S - stopped, F - finished
	main_url = attr.ib(default='')	# main url
	next_url = attr.ib(default='')	# next url
	cerr = attr.ib(default=None)
	ns = attr.ib(default=None)		# multiprocessing namespace



class ProcQueue(object):

    def __init__(self, settings, max_workers, max_queue):
        self._manager = multiprocessing.Manager()
        self.pool = futures.ProcessPoolExecutor(max_workers=max_workers)
        self.pool._adjust_process_count()

        self.procs = {}
        self.queue = 0
        self.max_queue = max_queue
        self.lock = threading.Lock()

        self.settings = settings


    def submit(self, uid, wd, func, *args, **kwargs):

    	# submit a process
    	# func at least has ns and cerr, ie: f(ns=None, cerr=None)

        with self.lock:  # can use with self.lock.acquire() ???
            if self.queue >= self.max_queue:
                raise MaxQueueError(
                    "Queue reached maximum number. Please try again in few moments")

            while True:
                procid = random_string(16)
                if procid not in self.procs:
                    break

            procunit = ProcUnit(taskid = procid, uid = uid, wd = wd)
            procunit.ns = self.prepare_namespace()
            procunit.cerr = self.manager().list()
            kwargs['ns'] = procunit.ns
            kwargs['cerr'] = procunit.cerr
            proc = self.pool.submit( func, *args, **kwargs )
            procunit.proc = proc
            self.procs[procid] = procunit
            self.queue += 1
            proc.add_done_callback( lambda x: self.callback(x, procid) )

        return procunit


    def callback(self, proc, procid):
        print('callback(): procid = %s' % procid)
        status = 'F' if proc.done() else 'S'
        exc = proc.exception()
        result = proc.result() if exc is None else None

        with self.lock:  # can use with self.lock.acquire() ???
            self.queue -= 1
            procunit = self.procs[procid]
            if procunit.proc != proc:
                raise RuntimeError('FATAL PROG/ERR!')
            procunit.status = status     # set status to Stop
            procunit.exc = exc
            procunit.result = result


    def get(self, procid):
        return self.procs[procid]

    def clear(self, procid):
        del self.procs[procid]

    def manager(self):
        return self._manager

    def prepare_namespace(self):
        ns = self.manager().Namespace()
        ns.msg = None
        ns.start_time = 0
        ns.finish_time = 0
        return ns


class PoolExecuter(futures.ProcessPoolExecutor):

    def __del__(self):
        print("DELETE THIS POOL, HOW?")
        self.__del__()


_PROC_QUEUE_ = None

def init_queue( settings, max_workers = 2, max_queue = 10 ):
    global _PROC_QUEUE_, _MANAGER_
    if _PROC_QUEUE_ is None:
        if 'genaf.concurrent.workers' in settings:
            max_workers = int( settings['genaf.concurrent.workers'])
        _PROC_QUEUE_ = ProcQueue( settings, max_workers, max_queue )
        log.info("Multiprocessing queue has been setup with %d process" % max_workers)
    else:
        raise RuntimeError("PROC_QUEUE has been defined!!")


def get_queue():
    global _PROC_QUEUE_
    if _PROC_QUEUE_ is None:
        raise RuntimeERror("PROG/ERR - PROC_QUEUE has not been initialized")
    return _PROC_QUEUE_


def subproc( uid, wd, func, *args, **kwargs ):
    return get_queue().submit( uid, wd, func, *args, **kwargs )


def getproc( procid ):
    return get_queue().get(procid)


def clearproc( procid ):
    return get_queue().clear(procid)


def getmanager():
    return get_queue().manager()


def estimate_time(start_time, current_time, processed, unprocessed):
    """ return string of '2d 3h 23m' """
    used_time = current_time - start_time   # in seconds
    if processed == 0:
        return 'undetermined'
    average_time = used_time / processed
    estimated = average_time * unprocessed
    cerr('Average time: %3.6f sec' % average_time)
    cerr('Estimated remaining time: %3.6f sec' % estimated)

    text = ''
    if estimated > 86400:
        text += '%dd ' % int( estimated / 86400 )
        estimated = estimated % 86400
    if estimated > 3600:
        text += '%dh ' % int( estimated / 3600 )
        estimated = estimated  % 3600
    text += '%dm' % (int( estimated / 60) + 1)

    return text