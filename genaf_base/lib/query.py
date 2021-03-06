
#from spatools.lib.analytics import query
from spatools.lib.analytics import selector
from spatools.lib.analytics.sampleset import SampleSet, SampleSetContainer

from rhombus.lib.utils import get_dbhandler

from sqlalchemy import extract, and_
from pandas import DataFrame, pivot_table

from collections import OrderedDict
from itertools import cycle
import yaml


def load_yaml(yaml_text):

    d = yaml.load( yaml_text )
    return load_params( d )


def load_params( d ):
    instances = {}
    options = d.get('options', {'colour_scheme': 'hue20'})
    for k in d:
        if k == 'selector':
            instances['selector'] = _SELECTOR_CLASS_.from_dict( d[k], options )
            print(instances['selector'])
        elif k == 'filter':
            instances['filter'] = _FILTER_CLASS_.from_dict( d[k], options )
        elif k == 'differentiator':
            instances['differentiator'] = _DIFFERENTIATOR_CLASS_.from_dict( d[k], options )
        elif k == 'options':
            instances['options'] = options
        else:
            raise RuntimeError()

    return instances


class Query(object):
    """ Query translate specs into actual selector, filter and differentiator
    """

    def __init__(self, specs, dbhandler, **kwargs):
        self.specs = load_params(specs)     # create instances of selector, filter and differentiator
        self.dbhandler = dbhandler
        self.kwargs = kwargs
        self._initial_sample_sets = None

    def get_sample_sets(self, sample_ids = None):
        if self._initial_sample_sets is None or sample_ids:
            #self._initial_sample_sets = super().get_initial_sample_sets(sample_ids)
            selector = self.specs['selector']
            self._sample_sets = selector.get_sample_sets(
                                                        self.dbhandler, sample_ids )
            differentiator = self.specs.get('differentiator', None)
            if differentiator:
                self._sample_sets = differentiator.get_sample_sets(
                                                        self._sample_sets,
                                                        self.dbhandler )
        return self._sample_sets


class FieldBuilder(object):

    def __init__(self, dbh):
        self._dbh = dbh


    def _eval_arg(self, arg, field):

        if type(arg) == str:
            if '|' in arg:
                arg = [ x.strip() for x in arg.split('|') ]
            elif ',' in arg:
                arg = [ x.strip() for x in arg.split(',') ]

        if type(arg) == list:
            return field.in_(arg)

        if type(arg) == str:
            arg = arg.strip()

        if type(arg) == str and arg.startswith('!'):
            return field != arg[1:].strip()
        return field == arg


    def _eval_ek_arg(self, arg, field_id):

        if '|' in arg:
            arg = [ x.strip() for x in arg.split('|') ]
        elif ',' in arg:
            arg = [ x.strip() for x in arg.split(',') ]

        if type(arg) == list:
            ek_ids = [ self._dbh.EK._id(x) for x in arg ]
            return field_id.in_( ek_ids )

        arg = arg.strip()

        if arg.startswith('!'):
            return field_id != self._dbh.EK._id( arg[1:].strip() )
        return field_id == self._dbh.EK._id( arg )


    def _get_dbh(self):
        return self._dbh


    # fields

    def query(self, arg):
        from genaf.lib.querytext import parse_querytext
        return ( self._dbh.Sample.id.in_( parse_querytext(self, arg )),
                None )

    def batch_id(self, arg):
        return ( self._eval_arg(arg, self._dbh.Sample.batch_id),
                None )

    def batch(self, arg):
        return ( self._eval_arg(arg, self._dbh.Batch.code),
                self._dbh.Batch )

    def code(self, arg):
        return ( self._eval_arg(arg, self._dbh.Sample.code),
                None )

    def category(self, arg):
        return ( self._eval_arg(arg, self._dbh.Sample.category),
                None )

    def int1(self, arg):
        return ( self._eval_arg(arg, self._dbh.Sample.int1),
                None )

    def int2(self, arg):
        return ( self._eval_arg(arg, self._dbh.Sample.int2),
                None )

    def string1(self, arg):
        return ( self._eval_arg(arg, self._dbh.Sample.string1),
                None )

    def string2(self, arg):
        return ( self._eval_arg(arg, self._dbh.Sample.string2),
                None )

    def country(self, arg):
        return ( self._eval_ek_arg(arg, self._dbh.Location.country_id),
                self._dbh.Location )

    def adminl1(self, arg):
        return ( self._eval_ek_arg(arg, self._dbh.Location.level1_id),
                self._dbh.Location )

    def adminl2(self, arg):
        return ( self._eval_ek_arg(arg, self._dbh.Location.level2_id),
                self._dbh.Location )

    def adminl3(self, arg):
        return ( self._eval_ek_arg(arg, self._dbh.Location.level3_id),
                self._dbh.Location )

    def adminl4(self, arg):
        return ( self._eval_ek_arg(arg, self._dbh.Location.level4_id),
                self._dbh.Location )

    # sample access control

    def group_ids(self, arg):
        return ( self._dbh.Batch.group_id.in_( arg ), self._dbh.Batch )

    def public(self, arg):
        return ( self._dbh.Batch.public == True, self._dbh.Batch )



class Selector(selector.Selector):

    """
        selector specs:

            group_ids:  [current group ids of users]
            samples:
                '*' :
                    - { batch_id: 20,  }
                    - { batch_id: 30, }

        AND operator works in each spec list
        OR operator works when combining list

    """

    def __init__(self, private=False, group_ids = None):
        super().__init__()
        self.private = private      # applying to both private and public samples
        self.group_ids = group_ids  # current user's group ids for sample authorization
        self.samples = {}
        self.options = None

    def update_samples(self):
        pass


    def get_fieldbuilder(self, dbh):
        return FieldBuilder(dbh)

    def filter_sample(self, spec, dbh, q):
        """ return the query after being built with YAML spec """

        builder = self.get_fieldbuilder(dbh)

        joined_classes = set()
        expressions = []

        for key in spec:
            if key.startswith('_'):
                continue

            try:
                func = getattr(builder, key)

            except AttributeError:
                raise RuntimeError('ERR: unknown field: %s' % key)

            expr, class_ = func( spec[key] )
            if class_:
                joined_classes.add( class_ )

            expressions.append( expr )

        for class_ in joined_classes:
            q = q.join( class_ )

        q = q.filter( and_( *expressions ))

        return q


    def spec_to_samples(self, spec_list, dbh, sample_ids=None):

        q = dbh.Sample.query(dbh.session())

        results = self.spec_to_sql( q, spec_list, dbh, sample_ids )

        samples = set()
        for r in results:
            samples.update( set(r) )

        return samples


    def spec_to_sample_ids(self, spec_list, dbh, sample_ids=None):
        
        q  = dbh.session().query(dbh.Sample.id)

        results = self.spec_to_sql( q, spec_list, dbh, sample_ids )

        sample_ids = set()
        for r in results:
            sample_ids.update( set( x.id for x in r) )

        return sample_ids


    def spec_to_sql(self, initial_query, spec_list, dbh, sample_ids=None):

        results = []

        for spec in spec_list:

            q = initial_query
            spec_copy = spec.copy()

            if self.group_ids:
                spec_copy['group_ids'] = self.group_ids

            elif not self.private:
                spec_copy['public'] = True

            q = self.filter_sample(spec_copy, dbh, q)

            results.append( q.all() )

        return results


    def add_class(self, q, class_list, class_):
        if class_ not in class_list:
            class_list.append(class_)
            return q.join(class_)
        return q


    def eval_ek_arg(self, arg, identifier, dbh):
        if arg[0] == '!':
            return identifier != dbh.EK._id( arg[1:].strip() )
        else:
            return identifier == dbh.EK._id( arg.strip() )

    @classmethod
    def from_dict(cls, d, opts):
        print(d)
        selector = cls( private = d.get('private', False),
                        group_ids = d.get('group_ids', None))
        selector.options = opts
        selector.samples = d.get('samples', {})
        return selector

        

class Filter(object):
    pass


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Differentiator(object):

    def __init__(self):
        self.spatial = None
        self.temporal = None
        self.int1 = None
        self.int2 = None
        self.string1 = None
        self.string2 = None
        self.options = None

        #helpers
        self.location_renderer = None
        self.location_cache = {}

        #handler
        self.dbh = None


    @classmethod
    def from_dict(cls, d, opts):
        diff = cls()
        diff.spatial = d['spatial']
        diff.temporal = d['temporal']
        diff.options = opts
        return diff


    def get_sample_sets(self, sample_sets, dbh):

        diff_sample_sets = self.do_differentiation( sample_sets, dbh )

        return self.generate_sample_sets( diff_sample_sets )


    def do_differentiation(self, sample_sets, dbh):
        """ return a dict of { tag: sample_ids } """

        curr_sample_sets = [ (s.label, s.sample_ids) for s in sample_sets ]

        #bh = self.dbh

        new_sample_sets = OrderedDict()

        for (label, sample_ids) in curr_sample_sets:
            rows = []
            for partial_sample_ids in chunks(list(sample_ids), 500):
                q = dbh.session().query( dbh.Sample.id, dbh.Sample.location_id,
                        extract('year', dbh.Sample.collection_date),
                        extract('month', dbh.Sample.collection_date),
                        dbh.Sample.int1, dbh.Sample.int2,
                        dbh.Sample.string1, dbh.Sample.string2
                        ).filter( dbh.Sample.id.in_(partial_sample_ids))

                rows.extend(
                    (int(s_id), self.render_location(loc_id, dbh), yr, mo,
                        int1, int2, str1, str2)
                    for (s_id, loc_id, yr, mo, int1, int2, str1, str2) in q
                )

            if not len(rows) > 0:
                continue

            # create tag for each sample
            for (s_id, loc, yr, mo, int1, int2, str1, str2) in rows:
                tag = [ label ]
                if self.spatial >= 0:
                    tag.append( loc )
                if self.temporal > 0:
                    if self.temporal == 1:
                        tag.append( '%d' % yr )
                    elif self.temporal == 2:
                        half = 'H2' if mo >= 6 else 'H1'
                        tag.append( '%d %s' % (yr, half) )
                    elif self.temporal == 3:
                        quarter = 'Q4' if mo >= 9 else ( 'Q3' if mo >= 6
                                        else ('Q2' if mp >= 3 else 'Q1'))
                        tag.append( '%d %s'% (yr, quarter) )
                    else:
                        raise RuntimeError('ERR - unknown temporal setting')
                if self.int1:
                    tag.append( str(int1) )
                if self.int2:
                    tag.append( str(int2) )
                if self.string1:
                    tag.append(str1)
                if self.string2:
                    tag.append(str2)
                tag = tuple(tag)

                try:
                    new_sample_sets[tag].append( s_id )
                except KeyError:
                    new_sample_sets[tag] = [ s_id ]

        return new_sample_sets

        curr_sample_sets = self.do_spatial_differentiation(curr_sample_sets)
        curr_sample_sets = self.do_temporal_differentiation(curr_sample_sets)

        return curr_sample_sets


    def generate_sample_sets(self, sample_set_dict):
        """ given a dict of sample sets, create proper SampleSet """

        colours = cycle(selector.colour_scheme[self.options['colour_scheme']])
        sample_sets = SampleSetContainer()

        for (tag, sample_ids) in sample_set_dict.items():
            sample_sets.append(
                        SampleSet(label = ' | '.join(tag),
                            colour = next(colours),
                            sample_ids = set(sample_ids))
                    )

        return sample_sets


    def render_location(self, location_id, dbh):
        if self.spatial < 0:
            return ''

        try:
            return self.location_cache[location_id]
        except KeyError:
            pass

        location = dbh.get_location_by_id(location_id)
        render = location.render(self.spatial)
        self.location_cache[location_id] = render
        return render


# selector and differentiator are common for all type of data (MS and SNP)
# filter class is specific for the type of data
_SELECTOR_CLASS_ = Selector
_FILTER_CLASS_ = Filter
_DIFFERENTIATOR_CLASS_ = Differentiator


def set_query_class( selector_class=None, filter_class=None, differentiator_class=None ):
    global _SELECTOR_CLASS_, _FILTER_CLASS_, _DIFFERENTIATOR_CLASS_
    if selector_class:
        _SELECTOR_CLASS_ = selector_class
    if filter_class:
        _FILTER_CLASS_ = filter_class
    if differentiator_class:
        _DIFFERENTIATOR_CLASS_ = differentiator_class

