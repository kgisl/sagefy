from framework.routes import get, post, abort
from framework.session import get_current_user
from database.my_recently_created import get_my_recently_created_subjects
from database.entity_base import list_by_entity_ids, get_latest_accepted, \
    get_versions, get_version
from config import config
from database.entity_facade import list_units_in_subject
from database.subject import deliver_subject, insert_subject
from database.unit import deliver_unit
from modules.util import extend
from copy import deepcopy
from modules.sequencer.next import go_next


@get('/s/subjects/recommended')
def get_recommended_subjects(request):
    db_conn = request['db_conn']
    entity_ids = ('JAFGYFWhILcsiByyH2O9frcU',)
    if config['debug']:
        entity_ids = ('subjectAll',)
    subjects = list_by_entity_ids('subjects', db_conn, entity_ids)
    if not subjects:
        return abort(404)
    return 200, {
        'subjects': [deliver_subject(subject) for subject in subjects]
    }


@get('/s/subjects/{subject_id}')
def get_subject_route(request, subject_id):
    """
    Get a specific subject given an ID.
    """

    db_conn = request['db_conn']
    subject = get_latest_accepted('subjects', db_conn, subject_id)
    if not subject:
        return abort(404)
    # TODO-2 SPLITUP create new endpoints for these instead
    units = list_units_in_subject(subject, db_conn)
    return 200, {
        'subject': deliver_subject(subject),
        # TODO-3 subject parameters
        'units': [deliver_unit(unit) for unit in units],
    }


@get('/s/subjects')
def list_subjects_route(request):
    """
    Return a collection of subjects by `entity_id`.
    """

    db_conn = request['db_conn']
    entity_ids = request['params'].get('entity_ids')
    if not entity_ids:
        return abort(404)
    entity_ids = entity_ids.split(',')
    subjects = list_by_entity_ids('subjects', db_conn, entity_ids)
    if not subjects:
        return abort(404)
    return 200, {
        'subjects': [deliver_subject(subject, 'view') for subject in subjects]
    }


@get('/s/subjects/{subject_id}/versions')
def get_subject_versions_route(request, subject_id):
    """
    Get subject versions given an ID. Paginates.
    """

    db_conn = request['db_conn']
    versions = get_versions(
        'subjects', db_conn, entity_id=subject_id, **request['params'])
    return 200, {
        'versions': [
            deliver_subject(version, access='view')
            for version in versions
        ]
    }


@get('/s/subjects/versions/{version_id}')
def get_subject_version_route(request, version_id):
    """
    Get a subject version only knowing the `version_id`.
    """

    db_conn = request['db_conn']
    subject_version = get_version(db_conn, 'subjects', version_id)
    if not subject_version:
        return abort(404)
    return 200, {'version': subject_version}


@get('/s/subjects/{subject_id}/tree')
def get_subject_tree_route(request, subject_id):
    """
    Render the tree of units that exists within a subject.

    Contexts:
    - Search subject, preview units in subject
    - Pre diagnosis
    - Learner view progress in subject
    - Subject complete

    TODO-2 merge with get_subject_units_route
    TODO-2 simplify this method
    """

    db_conn = request['db_conn']
    subject = get_latest_accepted('subjects', db_conn, entity_id=subject_id)
    if not subject:
        return abort(404)
    units = list_units_in_subject(subject, db_conn)
    # For the menu, it must return the name and ID of the subject
    output = {
        'subjects': deliver_subject(subject),
        'units': [deliver_unit(unit) for unit in units],
    }
    current_user = get_current_user(request)
    if not current_user:
        return 200, output
    return 200, output


@get('/s/subjects/{subject_id}/units')
def get_subject_units_route(request, subject_id):
    """
    Present a small number of units the learner can choose from.
    """

    db_conn = request['db_conn']
    # TODO-3 simplify this method. should it be part of the models?
    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    # TODO-3 Time estimates per unit for mastery.
    if not go_next(current_user, name='choose_unit'):
        return 400, {}
    return 200, {
        'units': [deliver_unit(unit) for unit in units],
        # For the menu, it must return the name and ID of the subject
        'subject': deliver_subject(subject),
        'current_unit_id': context.get('unit', {}).get('entity_id'),
    }


@post('/s/subjects/{subject_id}/units/{unit_id}')
def choose_unit_route(request, subject_id, unit_id):
    """
    Updates the learner's information based on the unit they have chosen.
    """

    # TODO-3 simplify this method. should it be broken up or moved to model?
    db_conn = request['db_conn']
    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    unit = get_latest_accepted('units', db_conn, unit_id)
    if not unit:
        return abort(404)
    if not go_next(current_user, name='engage_unit', unit_id=unit_id):
        return 400, {}
    return 200, {}


# TODO-1 move to /s/users/{user_id}/subjects (?)
@get('/s/subjects:get_my_recently_created')
def get_my_recently_created_subjects_route(request):
    """
    Get the subjects the user most recently created.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    db_conn = request['db_conn']
    subjects = get_my_recently_created_subjects(current_user, db_conn)
    return 200, {
        'subjects': [deliver_subject(subject) for subject in subjects],
    }


@post('/s/subjects/versions')
def create_new_subject_version_route(request):
    """
    Create a new subject version for a brand new subject.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    db_conn = request['db_conn']
    data = deepcopy(request['params'])
    if 'entity_id' in data:
        return abort(403)
    data['user_id'] = current_user['id']
    subject, errors = insert_subject(db_conn, data)
    if len(errors):
        return 400, {
            'errors': errors,
            'ref': 'VBXxZqIzq5Tui8MVmaz8JsIM',
        }
    return 200, {'version': deliver_subject(subject, 'view')}


@post('/s/subjects/{subject_id}/versions')
def create_existing_subject_version_route(request, subject_id):
    """
    Create a new subject version for an existing subject.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    db_conn = request['db_conn']
    next_data = deepcopy(request['params'])
    next_data['entity_id'] = subject_id
    next_data['user_id'] = current_user['id']
    current_subject = get_latest_accepted(
        'subjects', db_conn, entity_id=subject_id)
    if not current_subject:
        return abort(404)
    subject_data = extend({}, current_subject, next_data)
    subject, errors = insert_subject(db_conn, subject_data)
    if len(errors):
        return 400, {
            'errors': errors,
            'ref': 'IrwkwrwhIfRHchkbeerGHX5V',
        }
    return 200, {'version': deliver_subject(subject, 'view')}
