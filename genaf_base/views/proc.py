

_TASKIDS_ = {}




class ProcRunner(object):

	def __init__(self):
		pass

	def __call__(self, request):

		
		# check for taskid
		taskid - request.GET.get('taskid', None)
		if taskid:

			
			if proc:
				# check if proc is already finish or done
				if proc.status in ['F', 'S']:


			return self.show_status()
