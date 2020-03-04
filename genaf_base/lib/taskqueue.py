
from redis import Redis
from rq import Queue
from threading import Lock
from time import time
import dogpile.cache
from rhombus.lib.utils import cerr

_TASKCACHE_ = None
_TASKQUEUE_ = None


def set_taskcache( region ):
	global _TASKCACHE_
	_TASKCACHE_ = region


def get_taskcache():
	assert _TASKCACHE_
	return _TASKCACHE_ 


def set_taskqueue( queue ):
    global _TASKQUEUE_
    _TASKQUEUE_ = queue
    return _TASKQUEUE_


def get_taskqueue():
    assert _TASKQUEUE_
    return _TASKQUEUE_


def init_taskcache( settings ):

    taskcache = dogpile.cache.make_region(
        key_mangler = dogpile.cache.util.sha1_mangle_key
    )

    taskcache.configure_from_config(settings, "genaf.taskcache.")
    set_taskcache(taskcache)

    return taskcache


def init_taskqueue( settings ):

    return set_taskqueue(TaskQueue(settings))


class CachedNameSpace(object):

    def __init__(self, user, args, ident):
        self.user = user
        self.args = args
        self.ident = ident
        self.cerr = []
        self.result = None
        self.msg = None


    def cerr(self, text):
        self.cerr.append( text )
        self.commit()


    def set_result(self, result):
        self.result = result
        self.commit()


    def set_msg(self, msg):
        self.msg = msg
        self.commit()


    def commit(self):
        tc = get_taskcache()
        tc.set(self.key, self)


class TaskQueue(object):

    def __init__(self, settings):
        self.settings = settings
        redis_conn = Redis()
        self.queue = Queue(settings['genaf.taskqueue.name'], connection=redis_conn)

    def submit_task(self, ident, func, *args):
        job = self.queue.enqueue_call(
                func = task_func,
                args = (self.settings, ident, ),
                job_id = self.random_job_id()
            )
        return job

    def random_job_id(self):
        # to prevent collision, use time as well
        return random_string(6) + hex(int(time()))[2:]


def task_func(settings, ident, callback, user, *args):

    # this is the main function that will be called by remote process
    # to set up result cache, database connection and cleaning-up stuff

    ns = CachedNameSpace(ident, user, args)

    # get dbhandler by remote process
    ns.cerr('I: Connecting to database')
    dbh = get_dbhandler_notsafe()
    if dbh is None:
        dbh = get_dbhandler(settings)

    # result
    result = callback(user, *args, ** { 'namespace': ns })

    return result


class DummyNS(object):
    """ dummy namespace """

    def cerr(self, text):
        cerr(text)
