
# the mixin contains method that does not directly deals with database

class LocationMixIn(object):
	pass

class NoteMixIn(object):
	pass

class BatchMixIn(object):
	pass

class SampleMixIn(object):

	def __repr__(self):
		return '<%s|%d|%s>' % (self.__class__.__name__, self.id, self.code)

