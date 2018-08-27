
from rhombus.scripts import setup_settings, arg_parser
from rhombus.lib.utils import cout, cerr, cexit, get_dbhandler
from genaf_base.lib.taskqueue import init_taskcache

from rq import Connection, Worker


def init_argparser(p = None):

	if p is None:
		p = arg_parser('genaf-base rq-worker')

	return p

def init_taskqueue( settings ):
	pass


def main(args):

	# initialize database
	cerr('initialize ')
	settings = setup_settings( args )
	get_dbhandler( settings )

	# init taskqueue here
	cerr('initialize taskcache')
	init_taskcache( settings )

	# running working

	with Connection():

		cerr('running worker')
		w = Worker(settings['genaf.taskqueue.name'])
		w.work()
