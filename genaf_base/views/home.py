
from genaf_base.views import *

from rhombus.views.home import login as rb_login, logout as rb_logout

def index(request):

    if request.user:
        return render_to_response('genaf_base:templates/home.mako',
                {
                    'html': '',
                }, request = request
        )

    return render_to_response('genaf_base:templates/cover.mako',
            {}, request = request )


def login(request):
    return rb_login(request)


def logout(request):
    return rb_logout(request)
