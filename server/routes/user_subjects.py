from framework.routes import get, post, put, delete, abort
from framework.session import get_current_user
from database.user import get_user
from database.user_subjects import insert_user_subjects, get_user_subjects, \
    append_user_subjects, remove_user_subjects, \
    list_user_subjects_entity
from database.entity_base import get_latest_accepted
from database.subject import deliver_subject
from modules.sequencer.next import go_next


@get('/s/users/{user_id}/subjects')
def get_user_subjects_route(request, user_id):
    """
    Get the list of subjects the user has added.
    """

    db_conn = request['db_conn']
    current_user = get_current_user(request)
    if not current_user or current_user['id'] != user_id:
        user = get_user({'id': user_id}, db_conn)
        if not user:
            return abort(404)
        if (user != current_user and
                user['settings']['view_subjects'] != 'public'):
            return abort(403)
    else:
        user = current_user
        if not current_user:
            return abort(401)
    user_subjects = list_user_subjects_entity(
        user_id, request['params'], db_conn)
    response = {
        'subjects': [
            deliver_subject(subject)
            for subject in user_subjects
        ]
    }
    if current_user == user:
        go_next(current_user, name='choose_subject')
    return 200, response


@post('/s/users/{user_id}/subjects/{subject_id}')
def add_subject_route(request, user_id, subject_id):
    """
    Add a subject to the learner's list of subjects.
    """

    db_conn = request['db_conn']
    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    if user_id != current_user['id']:
        return abort(403)
    subject = get_latest_accepted('subjects', db_conn, entity_id=subject_id)
    if not subject:
        return abort(404)
    user_subject = get_user_subjects(user_id, db_conn)
    if user_subject and subject_id in user_subject['subject_ids']:
        return 400, {
            'errors': [{
                'name': 'subject_id',
                'message': 'Subject is already added.',
            }],
            'ref': 'kPZ95zM3oxFDGGl8vBdR3J3o',
        }
    # TODO-2 move some of this logic to the database file
    if user_subject:
        user_subject, errors = append_user_subjects(
            user_id, subject_id, db_conn)
    else:
        user_subject, errors = insert_user_subjects({
            'user_id': user_id,
            'subject_ids': [subject_id],
        }, db_conn)
    if errors:
        return 400, {
            'errors': errors,
            'ref': 'zCFUbLBTg9n2DnTkQYbqO4X9'
        }
    return 200, {'subjects': user_subject['subject_ids']}


@put('/s/users/{user_id}/subjects/{subject_id}')
def select_subject_route(request, user_id, subject_id):
    """
    Select the subject to work on.
    """

    db_conn = request['db_conn']
    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    subject = get_latest_accepted('subjects', db_conn, subject_id)
    if go_next(
        current_user,
        name='engage_subject',
        subject_id=subject['entity_id']
    ):
        return 200, {}
    return 400, {'errors': [{
        'message': 'Not a valid subject.',
    }]}


@delete('/s/users/{user_id}/subjects/{subject_id}')
def remove_subject_route(request, user_id, subject_id):
    """
    Remove a subject from the learner's list of subjects.
    """

    db_conn = request['db_conn']
    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    if user_id != current_user['id']:
        return abort(403)
    user_subject = get_user_subjects(user_id, db_conn)
    if not user_subject:
        return 404, {
            'errors': [{'message': 'User does not have subjects.'}],
            'ref': '8huZbvEAYOP8LcZb2sXbqNOC'
        }
    if subject_id not in user_subject['subject_ids']:
        return abort(404)
    user_subject, errors = remove_user_subjects(user_id, subject_id, db_conn)
    if errors:
        return 400, {
            'errors': errors,
            'ref': 'qIfll1e7dbP9V9jmC8FkCwsa'
        }
    return 200, {'subjects': user_subject['subject_ids']}
