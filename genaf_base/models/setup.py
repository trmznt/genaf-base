
from genaf_base.models import *

def setup( dbh ):

    dbh.EK.bulk_update( ek_initlist, dbsession=dbh.session() )


# add additional initial data here


ek_initlist = [
    (   '@SYSNAME', 'System names',
        [
            ( 'genaf_base'.upper(), 'genaf_base' ),
        ]
    ),
]
