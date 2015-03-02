from flask import Blueprint, abort
# , jsonify, request
# from models.set import Set
from flask.ext.login import current_user

# Nota Bene: We use `set_` because `set` is a type in Python
set_routes = Blueprint('set_', __name__, url_prefix='/api/sets')


@set_routes.route('/<set_id>/', methods=['GET'])
def get_set(set_id):
    """TODO
    Get a specific set given an ID.
    """
    pass


@set_routes.route('/<set_id>/tree/', methods=['GET'])
def get_set_tree(set_id):
    """TODO
    Render the tree of units that exists within a set.
    """
    pass

    # TODO For the menu, it must return the name and ID of the set


@set_routes.route('/<set_id>/units/', methods=['GET'])
def get_set_units(set_id):
    """TODO
    Render the units that exist within the set.
    Specifically, present a small number of units the learner can choose
    from.
    """

    if not current_user.is_authenticated():
        return abort(401)

    # TODO For the menu, it must return the name and ID of the set


@set_routes.route('/<set_id>/units/<unit_id>/', methods=['POST', 'PUT'])
def choose_unit(set_id, unit_id):
    """TODO
    Updates the learner's information based on the unit they have chosen.
    """

    if not current_user.is_authenticated():
        return abort(401)
