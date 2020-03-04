
from genaf_base.lib.taskqueue import TaskQueue, DummyNS
from genaf_base.lib.query import Selector, Query
from rhombus.lib.tags import *
from rhombus.lib.utils import get_dbhandler
from rhombus.views import m_roles
from rhombus.lib.roles import PUBLIC
from pyramid.renderers import render_to_response


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
                ok = analysis_task(self.get_callback(), self.request.user, params2specs(params), ns)
                html, jscode = self.format_result(ns.result)

            return render_to_request( 'genaf_base:templates/generics/page.py',
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

            custom_submit_bar(('Execute', 'execute'), ),

        )

        return qform, jscode


    def parse_form(self, params):
        """ return a dict containing all parameters """

        return {}


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


    def get_callback(self):
        return None


def params2specs(params, group_ids=None):
    """ convert params (dictionary from web-form) to dict-bases specs """
    selector = {
        'group_ids': group_ids,
        'batch_ids': params.get('batch_ids', None)
    }
    return { 'selector': selector }


def analysis_task(callback, userinstance, specs, namespace):

    # at this point, get_dbhandler() should have return proper db handler
    # also needs to pass userinstance.groups to sample selector

    dbh = get_dbhandler()
    q = dbh.Query(specs, dbh)
    ok = callback( q, userinstance, namespace )
    return ok


