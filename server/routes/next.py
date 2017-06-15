from framework.routes import get, abort
from framework.session import get_current_user


@get('/s/next')
def next_route(request):
    """
    Tell the learner where to go next.
    TODO-3 should we move all `next` data from individual endpoints
           to this one, and have the UI call this endpoint each time
           to get the next state?
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    return 200, ...
