import logging

log = logging.getLogger(__name__)

from rhombus.lib.utils import random_string, silent_remove
from rhombus.lib.roles import SYSADM, DATAADM, SYSVIEW, DATAVIEW

from genaf_base.lib.utils import detect_buffer

from genaf_base.views import *
from genaf_base.lib.dictfmt import csv2dict
#from genaf_base.views import uploadmgr

from genaf_base.views.sample import format_sampleinfo

import os, json, yaml, sys
from io import StringIO
import sqlalchemy.exc


class BatchViewer(object):

    def __init__(self, request):
        self.request = request
        self.dbh = get_dbhandler()
        self.batch = None

    @m_roles( PUBLIC )
    def index(self):

        group_id = int(self.request.params.get('group_id', 0))
        if group_id:
            if self.request.user.in_group(group_id):
                batches = self.dbh.get_batches( groups = [(None, group_id)] )
            else:
                return error_page('You do noh have access to view batches that belong to this group.')
          
        elif self.request.user.has_roles( SYSADM, DATAADM, SYSVIEW, DATAVIEW ):
            batches = self.dbh.get_batches( groups = None )
        else:
            batches = self.dbh.get_batches( groups = self.request.user.groups )

        html, code = generate_batch_table(batches, self.request)

        return render_to_response('genaf_base:templates/generics/page.mako',
            {   'content': str(html),
                'code': code,
            },  request = self.request)

    def action(self):
        
        return "Whoi?"

    def edit(self):
        pass

    def save(self):
        pass

    @m_roles( PUBLIC )
    def view(self):

        objid = int(self.request.matchdict.get('id'))
        if objid <= 0:
            return error_page('Please provide batch ID')

        batch = self.dbh.get_batch_by_id(objid)
        html = div()[
            h2('Batch: %s' % batch.code),
            table()[
                tr()[ td('Group: '), td( batch.group.name)
                    ],
                tr()[ td('No of sample: '), td('%d' % batch.samples.count())
                    ],
            ]
        ]
        jscode = ''

        return render_to_response( "genaf_base:templates/generics/page.mako",
            {   'batch': batch,
                'html': html,
                'jscode': jscode
            },
            request = self.request )



    def get_batch(self):

        if self.batch is None:
            batch_id = int(self.request.matchdict.get('id'))
            if batch_id <= 0:
                return error_page('Please provide batch ID')

            self.batch = self.dbh.get_batch_by_id(batch_id)
        return self.batch




def generate_batch_table(batches, request):

    table_body = tbody()

    not_guest = not request.user.has_roles( GUEST )

    for batch in batches:
        table_body.add(
            tr(
                td(literal('<input type="checkbox" name="batch-ids" value="%d" />' % batch.id)
                    if not_guest else ''),
                td( a(batch.code, href=request.route_url('genaf.batch-view', id=batch.id)) ),
                td( batch.description or '-' ),
                td( a(batch.samples.count(),
                        href=request.route_url('genaf.sample', _query = {'q': '%d[batch_id]' % batch.id}))),
                td( a(batch.group.name,
                        href=request.route_url('genaf.batch', _query = {'group_id': batch.group.id}))),
                td( 'public' if batch.public else 'private'),
            )
        )

    batch_table = table(class_='table table-condensed table-striped')[
        thead(
            tr(
                th('', style="width: 2em"),
                th('Batch code'),
                th('Description'),
                th('Sample size'),
                th('Group'),
                th('Status'),
            )
        )
    ]

    batch_table.add( table_body )

    if not_guest:
        add_button = ( 'New batch',
                        request.route_url('genaf.batch-edit', id=0)
        )

        bar = selection_bar('batch-ids', action=request.route_url('genaf.batch-action'),
                    add = add_button)
        html, code = bar.render(batch_table)

    else:
        html = div(batch_table)
        code = ''

    return html, code


@roles( PUBLIC )
def view(request):
    """ shows batch information """

    objid = int(request.matchdict.get('id'))
    if objid <= 0:
        return error_page('Please provide batch ID')

    dbh = get_dbhandler()

    batch = dbh.get_batch_by_id(objid)

    return render_to_response( "genaf:templates/batch/view.mako",
        {   'batch': batch,
        },
        request = request )


@roles( PUBLIC )
def edit(request):
    """ edit batch information """

    batch_id = int(request.matchdict.get('id'))
    if batch_id < 0:
        return error_page(request, 'Please provide batch ID')

    dbh = get_dbhandler()

    if request.method == 'GET':
        # return a form

        if batch_id == 0:
            batch = dbh.new_batch()
            batch.id = 0

        else:
            batch = dbh.get_batch_by_id(batch_id)
            if not batch:
                return error_page(request, 'Batch with ID: %d does not exist!' % objid)

            # check permission
            if not batch.is_manageable(request.user):
                return error_page(request, 'Current user is not part of Batch group')

        editform = edit_form(batch, dbh, request)

        return render_to_response( "genaf:templates/batch/edit.mako",
            {   'batch': batch,
                'editform': editform,
            },
            request = request )

    elif request.POST:

        batch_d = parse_form( request.POST )
        if batch_d['id'] != batch_id:
            return error_page(request, "Inconsistent data")

        try:
            if batch_id == 0:
                batch = dbh.new_batch()
                dbh.session().add( batch )
                batch.update( batch_d )
                dbh.session().flush()
                request.session.flash(
                    (   'success',
                        'Batch [%s] has been created' % batch.code )
                )

            else:
                batch = dbh.get_batch_by_id( batch_id )
                # check security
                if not request.user.in_group( batch.group ):
                    return error_page(request,
                        'User is not a member of batch primary group!')
                batch.update( batch_d )
                dbh.session().flush()
                request.session.flash(
                    (   'success',
                        'Batch [%s] has been updated' % batch.code )
                )
        except RuntimeError as err:
            return error_page(request, str(err))
        except sqlalchemy.exc.IntegrityError as err:
            dbh.session().rollback()
            detail = err.args[0]
            if not batch.id: batch.id = batch_id
            editform = edit_form(batch, dbh, request)
            if 'UNIQUE' in detail:
                field = detail.split()[-1]
                print(field)
                if field == 'batches.code':
                    editform.get('genaf-batch_code').add_error('The batch code: %s is '
                        'already being used. Please use other batch code!'
                        % batch.code)
                return render_to_response( "genaf:templates/batch/edit.mako",
                    {   'batch': batch,
                        'editform': editform,
                    },
                    request = request )
            return error_page(request, str(dir(err)))

        return HTTPFound(location = request.route_url('genaf.batch-view', id = batch.id))

    return error_page(request, "Unknown HTTP method!")



@roles( PUBLIC )
def save(request):

    if not request.user.has_roles( PUBLIC ):
        return not_authorized()

    if not request.POST:
        return error_page("Need a POST form submission")

    dbh = get_dbhandler()

    batch_id = int(request.matchdict.get('id'))
    batch_d = parse_form( request.POST )
    if batch_d['id'] != batch_id:
        return error_page(request, "Inconsistent data")

    if batch_id < 0:
        return error_page(request, "Need a reasonable batch ID")

    # check permission
    batch_group = dbh.get_group_by_id( batch_d['group_id'] )
    if not request.user.in_group( batch_group ):
        return error_page(request,
                "Users can only assign their groups to batch primary group!")

    try:
        if batch_id == 0:
            batch = dbh.new_batch()
            dbh.session().add( batch )
            batch.update( batch_d )
            dbh.session().flush()
            request.session.flash(
                (   'success',
                    'Batch [%s] has been created' % batch.code )
            )

        else:
            batch = dbh.get_batch_by_id( batch_id )
            # check security
            if not request.user.in_group( batch.group ):
                return error_page(request,
                    'User is not a member of batch primary group!')
            batch.update( batch_d )
            dbh.session().flush()
            request.session.flash(
                (   'success',
                    'Batch [%s] has been updated' % batch.code )
            )
    except RuntimeError as err:
        return error_page(request, str(err))
    except sqlalchemy.exc.IntegrityError as err:
        detail = err.args[0]
        if 'UNIQUE' in detail:
            field = detail.split()[-1]
            print(field)
            if field == 'batches.code':
                return error_page(request,
                    'The batch code: %s is already being used. Please use other batch code!'
                    % batch.code)
        return error_page(request, str(dir(err)))

    return HTTPFound(location = request.route_url('genaf.batch-view', id = batch.id))


def edit_form(batch, dbh, request):

    if request.user.has_roles( SYSADM, DATAADM):
        group_opts = [ (g.id, g.name) for g in dbh.get_groups() if not g.name.startswith('_') ]
    else:
        group_opts = [ (x[1], x[0]) for x in request.user.groups if not x[0].startswith('_') ]

    eform = form( name='genaf/batch', method=POST,
                action=request.route_url('genaf.batch-edit', id=batch.id))
    eform.add(
        fieldset(
            input_hidden(name='genaf-batch_id', value=batch.id),
            input_text('genaf-batch_code', 'Batch code', value=batch.code),
            input_text('genaf-batch_desc', 'Description', value=batch.description),
            input_select('genaf-batch_group_id', 'Primary group', value=batch.group_id,
                options = group_opts),
            input_select('genaf-batch_assay_provider_id', 'Assay provider group',
                value = batch.assay_provider_id,
                options = [ (g.id, g.name) for g in dbh.get_groups() ]),
            input_select('genaf-batch_bin_batch_id', 'Batch for bins setting',
                value = batch.bin_batch_id,
                options = [ (b.id, b.code) for b in dbh.get_batches(None) ]),
            input_select_ek('genaf-batch_species_id', 'Species', batch.species_id,
                    dbh.get_ekey('@SPECIES')),
            input_textarea('genaf-batch_remark', 'Remarks', value=batch.remark),
            submit_bar(),
        )
    )

    return eform


def parse_form( f ):
    """ parse and sanitize inputs """

    d = dict()
    d['id'] = int(f['genaf-batch_id'])
    d['code'] = f['genaf-batch_code'][:16]
    d['group_id'] = int(f['genaf-batch_group_id'])
    d['assay_provider_id'] = int(f['genaf-batch_assay_provider_id'])
    d['bin_batch_id'] = int(f['genaf-batch_bin_batch_id'])
    d['species_id'] = int(f['genaf-batch_species_id'])
    d['description'] = f['genaf-batch_desc'][:256]
    d['remark'] = f['genaf-batch_remark'][:2048]

    return d



@roles( PUBLIC )
def action(request):


    method = request.params.get('_method', None)
    dbh = get_dbhandler()

    if method == 'add-sample-info':

        if not request.POST:
            return error_page(request, 'Only accept POST request!')

        batch_id = request.POST.get('batch_id')
        batch = get_dbhandler().get_batch_by_id( batch_id )

        # check security
        if not request.user.in_group( batch.group ):
            return error_page(request, 'Forbidden')

        sampleinfo_file = request.POST.get('sampleinfo_file')
        if not hasattr(sampleinfo_file, 'file'):
            return error_page(request, 'Please provide sample info file')


        retval = add_sample_info(batch, sampleinfo_file, request)
        if type(retval) == tuple:
            path, errlog = retval
        else:
            return retval

        if not path:
            return error_page(request,
                    'Error parsing input file. Please verify the input file manually.<br/>'
                    + '<br/>\n'.join( errlog ) )


        return render_to_response('genaf:templates/batch/verify-sampleinfo.mako',
                    {   'batch': batch,
                        'path': path,
                        'errlog': '<br />\n'.join( errlog ),
                    },
                    request = request
                )


    elif method == 'verify-sample-info':

        batch_id = request.params.get('batch_id')
        path = request.params.get('_path')

        batch = get_dbhandler().get_batch_by_id(batch_id)

        # check security
        if not request.user.in_group( batch.group ):
            return error_page(request, 'Forbidden')


        (exists, not_exists, error_msgs) = verify_sample_info(batch, path )

        return render_to_response('genaf:templates/batch/submit-sampleinfo.mako',
                    {   'existing_samples': len(exists),
                        'new_samples': len(not_exists),
                        'batch': batch,
                        'path': path,
                        'option_params': [
                            ( 'Add new samples and update existing samples', 'A', True ),
                            ( 'Add only new samples to database', 'N', False ),
                            ( 'Update only existing samples to database', 'U', False),
                        ]
                    },
                    request = request
                )


    elif method == 'new-assay-upload-session':

        batch_id = request.params.get('batch_id')
        batch = get_dbhandler().get_batch_by_id(batch_id)

        sesskey = uploadmgr.new_session(request, batch)

        return HTTPFound(location=request.route_url('genaf.uploadmgr-view', id=sesskey))


    elif method == 'list-assay-upload-session':

        batch_id = request.params.get('batch_id')
        batch = get_dbhandler().get_batch_by_id(batch_id)

        return HTTPFound(location=request.route_url('genaf.uploadmgr',
                        _query = dict( batch_id = batch.id )) )


    elif method == 'process-sample-info':

        if not request.POST:
            return error_page(request, 'Only accept POST request!')

        batch_id = request.POST.get('batch_id')
        path = request.POST.get('_path')
        option = request.POST.get('options')

        batch = get_dbhandler().get_batch_by_id(batch_id)

        # check permission
        if not request.user.in_group( batch.group ):
            return error_page(request, 'Forbidden')

        try:
            (retcode, msg) = process_sample_info( batch, path, option )
        except RuntimeError as err:
            return error_page(request, str(err))
        except KeyError as err:
            return error_page(request,
                "%s -- Please add the missing key or ask the administrator to add one."
                % str(err))
        except sqlalchemy.exc.IntegrityError as err:
            return error_page(request,
                'Possibly missing a mandatory value, please check your input file -- %s'
                % str(err))
        except:
            exc = sys.exc_info()
            return error_page(request,
                'Unspecific error -- please contact the administrator! '
                'Error message from system: %s - %s' % (str(exc[0]), str(exc[1])))

        return render_to_response('genaf:templates/batch/process-sampleinfo.mako',
                    {   'msg': msg,
                        'batch': batch,
                    },
                    request = request )

    elif method == 'add-assay-info':

        if not request.POST:
            return error_page(request, 'Only accept POST request!')

        batch_id = request.POST.get('batch_id')

        # check permission
        if not request.user.in_group( batch.group ):
            return error_page(request, 'Forbidden')

        assayinfo_file = request.POST.get('assayinfo_file')
        assaydata_file = request.POST.get('assaydata_file')

        (path, errlog) = add_assay_info( batch, assayinfo_file, assaydata_file )

        return render_to_response('genaf:templates/batch/verify-assayinfo.mako',
                    {   'batch': batch,
                        'path': path,
                        'errlog': '<br />\n'.join( errlog ),
                    },
                    request = request
                )

    elif method == 'delete':
        batch_ids = request.POST.getall('batch-ids')
        batches = [ dbh.get_batch_by_id(batch_id) for batch_id in batch_ids ]

        if len(batches) == 0:
            return Response(modal_error)

        return Response( modal_delete %
            ''.join( '<li>%s | %s</li>' % (b.code, b.description) for b in batches ) )


    elif method == 'delete/confirm':
        batch_ids = request.POST.getall('batch-ids')

        for batch_id in batch_ids:
            batch = dbh.get_batch_by_id(batch_id)
            if not batch:
                request.session.flash( ('error',
                    'Batch with ID [%d] does not exists' % batch_id) )
                continue
            if not batch.is_manageable( request.user ):
                request.session.flash( ('error',
                    'You are not authorized to delete batch [%s]' % batch.code) )
                continue

            code = batch.code
            #batch.reset_samples()
            dbh.session().delete( batch )
            request.session.flash(
                ('success', 'Batch [%s] has been deleted' % code ) )


        return HTTPFound( location = request.referrer or
            request.route_url( 'genaf.batch' ) )

    else:
        raise RuntimeError('unknown method')



def lookup(request):
    raise NotImplementedError



## helper

def add_sample_info( batch, ifile, request):
    """ parse file and save it to temporary file as YAML file """


    name, ext = os.path.splitext( ifile.filename )

    if ext in [ '.csv', '.tab', '.tsv', '.txt' ]:
        # convert to JSON first
        # consistency checks
        #if ext == '.csv':
        #    delim = ','
        #else:
        #    delim = '\t'

        buf, delim = detect_buffer( ifile.file.read().decode('UTF-8') )

        try:
            ## the csv2dict function has to be sample-specific method
            ## use batch.Sample.csv2dict() ??
            dict_samples, errlog, sample_codes = batch.get_sample_class().csv2dict(
                            StringIO(buf),
                            with_report=True,
                            delimiter = delim )
        except ValueError as err:
            return error_page(request,  'ValueError: {0}'.format(err) )

        if dict_samples is None:
            return render_to_response( "msaf:templates/upload/error.mako",
                { 'report_log': '<br/>'.join(errlog) }, request = request )

        dict_text = yaml.dump( dict(codes = sample_codes, samples = dict_samples) )

    elif ext in ['.json', '.yaml']:
        dict_text = yaml.dump( yaml.load( ifile.file.read().decode('UTF-8') ) )
        errlog = ''

    else:

        return error_page(request, 'Unrecognized format')

    pathname = random_string(16) + '.yaml'

    temppath = get_temp_path( pathname )
    with open(temppath, 'w') as f:
        f.write( dict_text )

    return (pathname, errlog)



def verify_sample_info( batch, path ):
    """ return tuple of (exists, not_exists, err_msgs) """

    temppath = get_temp_path( path )
    err_msgs = []

    # open YAML

    with open(temppath) as f:
        payload = yaml.load( f )
        samples = payload['samples']
        codes = payload['codes']


    dbh = get_dbhandler()
    session = dbh.session()
    exists, not_exists = [], []
    for (sample_code, sample) in samples.items():
        if session.query(dbh.Sample).filter(dbh.Sample.batch_id == batch.id).filter(dbh.Sample.code == sample_code).count():
            exists.append( sample_code )
        else:
            not_exists.append(sample_code)

    return (exists, not_exists, err_msgs)


    raise RuntimeError(samples)

    ticket = request.get_ticket( { 'dict.path': temppath } )
    #                'replace_allele': opt_replace_existing } )

    return render_to_response( "msaf:templates/upload/verify.mako",
            { 'report_log': report_log.getvalue(), 'ticket': ticket,
                'filename': input_file.filename },
            request = request )


    buf = istream.read()
    raise RuntimeError

    return (True, "sucessfull reading %d bytes" % len(buf) )


def process_sample_info( batch, path, option ):

    temppath = get_temp_path( path )

    with open(temppath) as f:
        payload = yaml.load( f )
        samples = payload['samples']
        codes = payload['codes']

    inserts = 0
    updates = 0

    # updating location first
    null_location = get_dbhandler().search_location(auto=True)

    session = get_dbhandler().session()

    with session.no_autoflush:

      #for (sample_code, dict_sample) in samples.items():
      for sample_code in codes:
        dict_sample = samples[sample_code]
        # check sanity
        #if sample_code != sample['code']:
        #    pass

        db_sample = batch.search_sample( sample_code )

        if option == 'A':
            if not db_sample:
                db_sample = batch.add_sample( sample_code )
                db_sample.location = null_location
                inserts += 1
            else:
                updates += 1

        elif option == 'U':
            if not db_sample:
                continue
            updates += 1

        elif option == 'N':
            if db_sample: continue
            db_sample = batch.add_sample( sample_code )
            db_sample.location = null_location
            inserts += 1

        else:
            return error_page('Invalid option')
        db_sample.update( dict_sample )
        print('Flushing sample: %s' % db_sample.code)
        session.flush([db_sample])

    # remove the yaml/json file
    silent_remove( temppath )

    return (True, "Updating %d samples, inserting %d samples" % (updates, inserts))


## assay info processing

def add_assay_info(assayinfo_file, assaydata_file):

    assayinfo_name, assayinfo_ext = os.path.splitext( ifile.filename )
    assaydata_name, assaydata_ext = os.path.splitext( assaydata_file.filename )

    pathname = random_string(16) + '.yaml'

    temppath = get_temp_path( pathname )
    os.mkdir( temppath )
    with open( '%s/%s.%s' % (temppath, assaydata_name, assaydata_ext)) as f:
        f.write()


modal_delete = '''
<div class="modal-dialog" role="document"><div class="modal-content">
<div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3 id="myModalLabel">Deleting Batch(es)</h3>
</div>
<div class="modal-body">
    <p>You are going to delete the following Batch(es):
        <ul>
        %s
        </ul>
    </p>
</div>
<div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button>
    <button class="btn btn-danger" type="submit" name="_method" value="delete/confirm">Confirm Delete</button>
</div>
</div></div>
'''

modal_error = '''
<div class="modal-dialog" role="document"><div class="modal-content">
<div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3 id="myModalLabel">Error</h3>
</div>
<div class="modal-body">
    <p>Please select Batch(es) to be removed</p>
</div>
<div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
</div>
</div></div>
'''
