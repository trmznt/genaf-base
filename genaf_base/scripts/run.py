
import sys, os
import argparse

from rhombus.scripts.run import main as rhombus_main, set_config
from rhombus.lib.utils import cout, cerr, cexit

from genaf_base.models.handler import DBHandler

def greet():
    cerr('command line utility for genaf-base')


def usage():
    cerr('genaf_base-run - command line utility for genaf-base')
    cerr('usage:')
    cerr('\t%s scriptname [options]' % sys.argv[0])
    sys.exit(0)


set_config( environ='RHOMBUS_CONFIG',
            paths = ['genaf_base.scripts.'],
            greet = greet,
            usage = usage,
            dbhandler_class = DBHandler
)

main = rhombus_main



