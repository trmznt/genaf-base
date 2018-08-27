
from redis import Redis
from rq import Queue
from threading import Lock
import dogpile.cache

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

    redis_conn = Redis()
    q = Queue(settings['genaf.taskqueue.name'], connection=redis_conn)
    set_taskqueue(q)


    return q
