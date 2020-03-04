
from genaf_base.views.analysis import *
from rhombus.lib.roles import *


def do_sample_summary(*args, **kwargs): #q, user, ns=None):

    raise RuntineError()

    if not ns:
        ns = DummyNS()


class SampleSummary(AnalyticViewer):

    title = 'Sample Summary'
    info = ''

    callback = do_sample_summary


    def get_callback(self):
        return do_sample_summary


    def parse_form(self, params):

        d = super().parse_form(params)

        d['batch_ids'] = params.get('genaf-query.batch_ids')
        # XXX: we need to check batch_ids here

        return d


    def get_form(self, jscode="", params={}):
        qform, jscode = super().get_form(jscode, params)

        if self.request.user.has_roles( SYSADM, DATAADM, SYSVIEW, DATAVIEW ):
            batches = self.dbh.get_batches( groups = None )
        else:
            batches = self.dbh.get_batches( groups = self.request.user.groups )

        qform.get('genaf-query.sample-source').add(

            input_select('genaf-query.batch_ids', 'Batch(es)', offset=1, size=2,
                value=params.get('genaf-query.batches', None),
                options = [ (b.id, b.code) for b in batches ],
                multiple=True,
            ),

            # 
        )

        return qform, jscode



