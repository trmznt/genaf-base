from pyramid.config import Configurator
from pyramid.events import BeforeRender
from sqlalchemy import engine_from_config
import dogpile.cache

from rhombus import init_app as rhombus_init_app, add_route_view, add_route_view_class
from rhombus.lib.utils import cerr, cout, cexit, generic_userid_func
from rhombus.lib.fsoverlay import fsomount
from rhombus.models.core import set_func_userid

# set configuration and dbhandler
from genaf_base.scripts import run
from genaf_base.lib import helpers as h
from genaf_base.lib.configs import set_temp_path, get_temp_path, TEMP_TOOLS
from genaf_base.lib.taskqueue import init_taskqueue, init_taskcache

# initialize view
from genaf_base.views import *

def includeme( config ):
    """ this configuration must be included as the last order
    """
    print('genaf_base:', config)

    config.add_static_view('genaf_static', 'genaf_base:static/', cache_max_age=3600)

    # override assets here
    #config.override_asset('rhombus:templates/base.mako', 'genaf_base:templates/base.mako')
    #config.override_asset('rhombus:templates/plainbase.mako', 'genaf_base:templates/plainbase.mako')

    # add route and view for home ('/'), /login and /logout
    config.add_route('home', '/')
    config.add_view('genaf_base.views.home.index', route_name='home')

    config.add_route('login', '/login')
    config.add_view('genaf_base.views.home.login', route_name='login')

    config.add_route('logout', '/logout')
    config.add_view('genaf_base.views.home.logout', route_name='logout')

    # add additional routes and views here

    add_route_view( config, 'rhombus.views.fso', 'rhombus.fso',
        '/fso{path:.*}@@view',
        '/fso{path:.*}@@edit',
        '/fso{path:.*}@@save',
        '/fso{path:.*}@@action',
        ('/fso{path:.*}', 'index'),
    )


    add_route_view_class( config, 'genaf_base.views.batch.BatchViewer', 'genaf.batch',
        '/batch',
        '/batch/@@action',
        '/batch/{id}@@edit',
        '/batch/{id}@@save',
        ('/batch/{id}', 'view')

    )

    add_route_view_class( config, 'genaf_base.views.sample.SampleViewer', 'genaf.sample',
        '/sample',
        '/sample/@@action',
        '/sample/{id}@@edit',
        '/sample/{id}@@save',
        ('/sample/{id}', 'view')

    )

    # ANALYSIS PART

    config.add_route('analysis-samplesummary', '/analysis/samplesummary')
    config.add_view('genaf_base.views.analysis.samplesummary.SampleSummary', route_name='analysis-samplesummary')


    # subscriber
    config.add_subscriber( add_genaf_global, BeforeRender )


def init_app(global_config, settings, prefix='/mgr', include=None, include_tags=None):

    # global, shared settings

    temp_path = settings['genaf.temp_directory']
    set_temp_path( temp_path )

    fsomount(TEMP_TOOLS, get_temp_path('', TEMP_TOOLS))
    set_func_userid( generic_userid_func)

    # preparing for multiprocessing
    #init_queue(settings)

    # init taks cache, which provides a rudimentary caching for result coming
    # from worker process.
    # note that this mechanism is ony suitable for single wsgi worker - multiple
    # proc workers
    init_taskcache( settings )
    init_taskqueue( settings )



    # attach rhombus to /mgr url, include custom configuration
    config = rhombus_init_app(global_config, settings, prefix
                    , include = include, include_tags = include_tags)

    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    cerr('genaf-base main() is running...')

    # attach rhombus to /mgr url, include custom configuration
    config = init_app(global_config, settings, prefix='/mgr')

    return config.make_wsgi_app()


def add_genaf_global(event):
    event['h'] = h
