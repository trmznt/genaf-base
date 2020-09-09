from rhombus.lib.utils import cerr, get_dbhandler
from rhombus.scripts import setup_settings, arg_parser
from genaf_base.scripts import run
import sys

def greet():
    cerr('genaf-base-shell - shell for genaf-base')


def usage():
    cerr('genaf-base-shell - shell for genaf-base')
    cerr('usage:')
    cerr('\t%s scriptname [options]' % sys.argv[0])
    sys.exit(0)


def main():
    greet()

    # preparing everything
    p = arg_parser('genaf-base-shell')
    args = p.parse_args(sys.argv[1:])

    settings = setup_settings( args )
    dbh = get_dbhandler(settings)

    from IPython import embed
    import transaction
    embed()
