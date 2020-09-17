
from genaf_base.lib.taskqueue import TaskQueue, DummyNS
from genaf_base.lib.query import Selector, Query
from genaf_base.lib.configs import get_temp_path, TEMP_TOOLS

from rhombus.lib.tags import *
from rhombus.lib.utils import get_dbhandler
from rhombus.views import m_roles, roles
from rhombus.lib.roles import *
from rhombus.lib import fsoverlay

from pyramid.renderers import render_to_response


def get_fso_temp_dir(userid, rootdir = TEMP_TOOLS):
    """ return a fileoverlay object on temporary directory
    """

    absrootdir = get_temp_path('', rootdir)
    fso_dir = fsoverlay.mkranddir(absrootdir, userid)
    return fso_dir

def do_analysis(query, userinstance, ns, *args, **kwargs):
    """
        this analysis method has to be performed and detached from viewer
        classes as it might be executed in other process through
        multiprocessing pipeline where all local instances might not be
        available anymore.
    """

    dbh = get_dbhandler()

    ns.result['title'] = 'Dummy Analysis Result'

    return True


class AnalyticViewer(object):

    """ this a basic viewer for analysis tasks """

    title = 'Analytic Viewer'

    callback = None

    def __init__(self, root, request):
        self.root = root
        self.request = request
        self.dbh = get_dbhandler()

    @m_roles( PUBLIC )
    def __call__(self):

        if self.request.params.get('_method', None) == 'execute':
            # perform execute task
            params = self.parse_form(self.request.params)
            # probably need to convert params to spec
            # eg: specs = params2spec(params)
            if self.is_async():
                taskid = self.submit_task(params2specs(params))
                html, jscode = self.format_taskid(taskid)
            else:
                ns = DummyNS()
                ok = analysis_task(self.get_callback(), self.request.user,
                            self.params2specs(params), ns
                            )
                html, jscode = self.format_result(ns.result)

            return render_to_response( 'genaf_base:templates/generics/page.mako',
                        {   'html': html,
                            'jscode': jscode,
                        }, request = self.request
                )

        elif self.request.params.get('taskid', None) != None:
            # find a task and check its status
            pass

        else:
            form, jscode = self.get_form( params = self.parse_form(self.request.params) )

        html = div( h2(self.title), form )

        return render_to_response(
            'genaf_base:templates/generics/page.mako',
            {   'html': html,
                'jscode': jscode,
            }, request = self.request
        )

    def is_async(self):
        return False
        

    def get_form(self, jscode="", params=None):
        """ return form, jscode """

        qform = form('genaf-query', method="POST")

        qform.add(

            # hidden fields
            fieldset(name='genaf-query.hidden-fields'),
            fieldset(name='genaf-query.sample-source'),
            fieldset(name='genaf-query.sample-processing'),
            fieldset(name='genaf-query.allele-params'),
            fieldset(name='genaf-query.custom-options'),

            custom_submit_bar(('Execute', 'execute'), ),

        )

        # sample source & processing

        if self.request.user.has_roles( SYSADM, DATAADM, SYSVIEW, DATAVIEW ):
            batches = self.dbh.get_batches( groups = None )
        else:
            batches = self.dbh.get_batches( groups = self.request.user.groups )

        qform.get('genaf-query.sample-source').add(

            input_select('genaf-query.batch_ids', 'Batch code(s)', offset=2, size=3,
                value=params.get('genaf-query.batches', None),
                options = [ (b.id, b.code) for b in batches ],
                multiple=True,
            ),

        )

        qform.get('genaf-query.sample-processing').add(

            input_select('genaf-query.sample_countries', 'Sample origin',
                offset=2, size=3,
                multiple=True,
                value=[],
                options = self.dbh.get_countries(),
                ),

            input_select('genaf-query.sample_selection', 'Sample selection',
                offset=2, size=3,
                value='P',
                options = [ ('F', 'All field samples' ),
                            ('P', 'All population (day-0) samples')
                    ]
                ),

            input_select('genaf-query.sample_filtering', 'Sample filtering',
                offset=2, size=3,
                value='N',
                options = [ ('N', 'No futher sample filtering'),
                            ('M', 'Monoclonal samples'),
                            ('U', 'Unique genotype samples')
                        ]
                ),

            input_text('genaf-query.sample_quality', 'Sample quality threshold',
                offset=2, size=3,
                value=params.get('genaf-query.sample_quality', 0.9)
            ),

            input_select('genaf-query.spatial_differentiation', 'Spatial differentiation',
                offset=2, size=3,
                value=-1,
                options = [ (-1, 'No spatial differentiation'),
                            (0, 'Country level'),
                            (1, '1st Administration level'),
                            (2, '2nd Administration level'),
                            (3, '3rd Administration level'),
                            (4, '4th Administration level') ]
                ),

            input_select('genaf-query.temporal_differentiation', 'Temporal differentiation',
                offset=2, size=3,
                value=0,
                options = [ (0, 'No temporal differentiation'),
                            (1, 'Yearly'),
                            (2, 'Quaterly')]
                ),

            input_select('genaf-query.colour_scheme',  'Colour scheme', offset=2, size=3,
                value='hue20',
                options = [
                                ('ggplot2', 'ggplot2 standard continuous 16 colours'),
                                ('hue20', 'IWantHue categorical 20 colours'),
                                ('vega20', 'Vega categorical 20 colours'),
                                ('cb2', 'ColorBrewer2 categorical 12 colours'),
                ],
                multiple=False,
                ),
        )

        return qform, jscode


    def parse_form(self, params):
        """ return a dict containing all parameters """

        d = {}

        d['batch_ids'] = params.getall('genaf-query.batch_ids')
        d['spatial'] = int(params.get('genaf-query.spatial_differentiation', -1))
        d['colour_scheme'] = params.get('genaf-query.colour_scheme')
        # XXX: we need to check batch_ids here

        return d


    def params2specs_XXX(self, params):
        """ convert params (dictionary) to dictionary-based specs """
        # XXX: not in the right place... because we need to pass to remote process
        return { 'selector': selector }


    def submit_task(self, specs):
        q = get_taskqueue()
        job = q.submit_task( analysis_task, self.get_callback(),
                self.request.register.settings, self.get_callback(),
                    self.request.user, specs,
            )

        return job

    def format_result(self, result):
        """ should return (html, jscode) combination
        """

        return (div('AnalyticViewer: Not implemented!'), '')


    @classmethod
    def get_callback(cls):
        return cls.callback

    def params2specs(self, params, group_ids=None):
        specs = params2specs(params, group_ids)
        specs['options']['colour_scheme'] = params.get('colour_scheme')
        return specs


def params2specs(params, group_ids=None):
    """ convert params (dictionary from web-form) to dict-bases specs """
    selector = {
        # all group_ids where a user belongs to
        'group_ids': group_ids,

        # using private or public samples
        'private': True,

        # all batch_ids where sample will be fetched from
        'samples': {
        }
    }

    # if using forms:
    batch_ids = params.get('batch_ids', None)
    if batch_ids is not None:
        selector['samples']['*'] = [ { 'batch_id': int(d) }
                                            for d in batch_ids
                                    ]


    differentiator = {
            'spatial': params.get('spatial', -1),
            'temporal': params.get('temporal', 0),
    }

    return { 'selector': selector, 'differentiator': differentiator, 'options': {} }


def analysis_task(callback, userinstance, specs, namespace):

    # at this point, get_dbhandler() should have return proper db handler
    # also needs to pass userinstance.groups to sample selector

    dbh = get_dbhandler()
    q = dbh.Query(specs, dbh)
    ok = callback( q, userinstance, namespace )
    return ok
