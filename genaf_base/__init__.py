from pyramid.config import Configurator
from pyramid.events import BeforeRender
from sqlalchemy import engine_from_config

from rhombus import init_app, add_route_view, add_route_view_class
from rhombus.lib.utils import cerr, cout

# set configuration and dbhandler
from genaf_base.scripts import run

from genaf_base.lib import helpers as h

# initialize view
from genaf_base.views import *


def includeme( config ):
    """ this configuration must be included as the last order
    """

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



    # subscriber
    config.add_subscriber( add_genaf_global, BeforeRender )

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    cerr('genaf-base main() is running...')

    # attach rhombus to /mgr url, include custom configuration
    config = init_app(global_config, settings, prefix='/mgr'
                    , include = includeme, include_tags = [ 'genaf_base.includes' ])

    return config.make_wsgi_app()

def add_genaf_global(event):
    event['h'] = h
