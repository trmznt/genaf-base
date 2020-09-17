
from rhombus.models import handler as rhombus_handler
from rhombus.lib.utils import cerr, cout

from genaf_base.models import dbschema
from sqlalchemy import or_

from .setup import setup

class DBHandler(rhombus_handler.DBHandler):

    # add additional class references
    Location = dbschema.Location
    Batch = dbschema.Batch
    Sample = dbschema.Sample


    def initdb(self, create_table=True, init_data=True, rootpasswd=None):
        """ initialize database """
        super().initdb(create_table, init_data, rootpasswd)
        if init_data:
            from .setup import setup
            setup(self)
            cerr('[genaf-base] Database has been initialized')


    # add additional methods here

    def get_batches(self, groups):

        q = self.Batch.query(self.session())
        if groups is not None:
            # enforce security
            q = q.filter( or_( self.Batch.group_id.in_( [ x[1] for x in groups ] ), self.Batch.public == True ) )
        q = q.order_by( self.Batch.code )

        return q.all()


    def get_location_by_id(self, loc_id):
        return self.Location.query(self.session()).get(loc_id)

    def get_countries(self):
        return self.Location.get_countries(self.session())

    # search methods

    def search_location(self, country='', level1='', level2='', level3='', level4='',
                auto=False):
        return self.Location.search(country, level1, level2, level3, level4, auto,
                    dbsession = self.session())
