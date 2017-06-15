from framework.session import get_current_user
from framework.routes import get, post, abort
from database.response import deliver_response
from database.card_parameters import get_card_parameters, \
    get_card_parameters_values
from database.entity_base import get_latest_accepted, get_versions, \
    list_requires, list_required_by, list_by_entity_ids, get_version
from database.card import deliver_card, insert_card
from database.unit import deliver_unit
from modules.util import extend
from copy import deepcopy
from modules.sequencer.next import go_next

# from modules.sequencer.params import max_learned


@get('/s/cards/{card_id}')
def get_card_route(request, card_id):
    """
    Get a specific card given an ID. Show all relevant data, but
    not used for the learning interface.
    """

    db_conn = request['db_conn']
    card = get_latest_accepted('cards', db_conn, card_id)
    if not card:
        return abort(404)
    unit = get_latest_accepted('units', db_conn, entity_id=card['unit_id'])
    if not unit:
        return abort(404)
    # TODO-2 SPLITUP create new endpoints for these instead
    requires = list_requires('cards', db_conn, entity_id=card_id)
    required_by = list_required_by('cards', db_conn, entity_id=card_id)
    params = get_card_parameters({'entity_id': card_id}, db_conn)
    return 200, {
        'card': deliver_card(card, access='view'),
        'card_parameters': (get_card_parameters_values(params)
                            if params else None),
        'unit': deliver_unit(unit),
        'requires': [deliver_card(require) for require in requires],
        'required_by': [deliver_card(require) for require in required_by],
    }


@get('/s/cards')
def list_cards_route(request):
    """
    Return a collection of cards by `entity_id`.
    """

    db_conn = request['db_conn']
    entity_ids = request['params'].get('entity_ids')
    if not entity_ids:
        return abort(404)
    entity_ids = entity_ids.split(',')
    cards = list_by_entity_ids('cards', db_conn, entity_ids)
    if not cards:
        return abort(404)
    return 200, {'cards': [deliver_card(card, 'view') for card in cards]}


@get('/s/cards/{card_id}/learn')  # TODO-3 merge with main GET route
def learn_card_route(request, card_id):
    """
    Render the card's data, ready for learning.
    """

    db_conn = request['db_conn']
    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    card = get_latest_accepted('cards', db_conn, card_id)
    if not card:
        return abort(404)
    if not go_next(current_user, name='learn_card', card_id=card_id):
        return 400, {}
    return 200, {
        'card': deliver_card(card, access='learn'),
    }


@get('/s/cards/{card_id}/versions')
def get_card_versions_route(request, card_id):
    """
    Get versions card given an ID. Paginates.
    """

    db_conn = request['db_conn']
    versions = get_versions(
        'cards',
        db_conn,
        entity_id=card_id,
        **request['params']
    )
    return 200, {
        'versions': [
            deliver_card(version, access='view')
            for version in versions
        ]
    }


@get('/s/cards/versions/{version_id}')
def get_card_version_route(request, version_id):
    """
    Get a card version only knowing the `version_id`.
    """

    db_conn = request['db_conn']
    card_version = get_version(db_conn, 'cards', version_id)
    if not card_version:
        return abort(404)
    return 200, {'version': card_version}


@post('/s/cards/{card_id}/responses')
def respond_to_card_route(request, card_id):
    """
    Record and process a learner's response to a card.
    """

    # TODO-3 simplify this method.
    #      perhaps smaller methods or move to model layer?
    db_conn = request['db_conn']
    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    card = get_latest_accepted('cards', db_conn, card_id)
    if not card:
        return abort(404)
    go_next(current_user, name='respond_to_card', card_id=card_id)
    return 200, {
        'response': deliver_response(response),
        'feedback': feedback,
    }


@post('/s/cards/versions')
def create_new_card_version_route(request):
    """
    Create a new card version for a brand new card.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    db_conn = request['db_conn']
    data = deepcopy(request['params'])
    if 'entity_id' in data:
        return abort(403)
    data['user_id'] = current_user['id']
    card, errors = insert_card(db_conn, data)
    if len(errors):
        return 400, {
            'errors': errors,
            'ref': 'xenjJt51AO3wJysZsuOPOe0h',
        }
    return 200, {'version': deliver_card(card, 'view')}


@post('/s/cards/{card_id}/versions')
def create_existing_card_version_route(request, card_id):
    """
    Create a new card version for an existing card.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)
    db_conn = request['db_conn']
    next_data = deepcopy(request['params'])
    next_data['entity_id'] = card_id
    next_data['user_id'] = current_user['id']
    current_card = get_latest_accepted('cards', db_conn, entity_id=card_id)
    if not current_card:
        return abort(404)
    card_data = extend({}, current_card, next_data)
    card, errors = insert_card(card_data, db_conn)
    if len(errors):
        return 400, {
            'errors': errors,
            'ref': '0njH71xtw8mQ9xHVftLvaZWe',
        }
    return 200, {'version': deliver_card(card, 'view')}
