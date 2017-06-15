"""
Determine the next view for the user.
"""
import json
from modules.util import compact_dict, json_serial
from framework.redis import redis

"""
State transitions:
------------------
GET Choose Subject
    -> POST Choose Subject
POST Choose Subject
    -> GET Choose Unit    ...when in learn or review mode
    -> GET Learn Card     ...when in diagnosis (Unit auto chosen)
GET Choose Unit
    -> POST Choose Unit
POST Chosen Unit
    -> GET Learn Card
GET Learn Card
    -> POST Respond Card
POST Respond Card
    -> GET Learn Card      ...when not ready
    -> GET Choose Unit     ...when ready, but still units
    -> GET Choose Subject  ...when ready and done
"""


def retrieve_next():
    """
    Show where the user should go next.
    """

    # TODO translate to URL path & method


def go_next(user, **current):
    """
    Update the context of where the learner should go next.
    Given the user and the current path called.
        current || next = {
            name =
                choose_subject
                engage_subject
                choose_unit
                engage_unit
                learn_card
                respond_to_card
            ...
            subject_id
            unit_id
            card_id
        }
    Returns next dict if good, or None if error.
    """

    if False:
        next_ = after_choose_subject(user, current)
    elif False:
        next_ = after_engage_subject(user, current)
    elif False:
        next_ = after_choose_unit(user, current)
    elif False:
        next_ = after_engage_unit(user, current)
    elif False:
        next_ = after_learn_card(user, current)
    elif False:
        next_ = after_respond_to_card(user, current)
    else:
        next_ = go_next_to_my_subjects(user, current)

    return next_


def after_choose_subject(user, current):
    """
    Choose subject always precedes engage subject.
    """

    return {'name': 'engage_subject'}


def after_engage_subject(user, current):
    """

    """

    # Is the chosen subject valid?


def after_choose_unit(user, current):
    """

    """


def after_engage_unit(user, current):
    """

    """


def after_learn_card(user, current):
    """

    """


def after_respond_to_card(user, current):
    """

    """


def go_next_to_my_subjects(user, current):
    """

    """

"""
def get_learning_context(user):

    Get the learning context of the user.


    key = 'learning_context_{id}'.format(id=user['id'])
    try:
        context = json.loads(redis.get(key).decode())
    except:
        context = {}
    return context


def set_learning_context(user, **d):

    Update the learning context of the user.

    Keys: `card`, `unit`, `subject`
        `next`: `method` and `path`


    context = get_learning_context(user)
    d = pick(d, ('card', 'unit', 'subject', 'next'))
    context.update(d)
    context = compact_dict(context)
    key = 'learning_context_{id}'.format(id=user['id'])
    redis.setex(key, 10 * 60, json.dumps(context, default=json_serial))
    return context
"""

"""

view my subjects
-----------
next_ = {
    'method': 'POST',
    'path': '/s/users/{user_id}/subjects/{subject_id}'
            .format(user_id=current_user['id'],
                    subject_id='{subject_id}'),
}
set_learning_context(current_user, next=next_)
response['next'] = next_



select subject
---------------
next_ = {
    'method': 'GET',
    'path': '/s/subjects/{subject_id}/tree'
            .format(subject_id=subject_id),
}
set_learning_context(current_user, subject=subject, next=next_)



view tree
---------
context = get_learning_context(current_user) if current_user else {}
buckets = traverse(db_conn, current_user, subject)
output['buckets'] = {
    'diagnose': [u['entity_id'] for u in buckets['diagnose']],
    'review': [u['entity_id'] for u in buckets['review']],
    'learn': [u['entity_id'] for u in buckets['learn']],
    'done': [u['entity_id'] for u in buckets['done']],
}
# If we are just previewing, don't update anything
if subject_id != context.get('subject', {}).get('entity_id'):
    return 200, output
# When in diagnosis, choose the unit and card automagically.
if buckets['diagnose']:
    unit = buckets['diagnose'][0]
    card = choose_card(db_conn, current_user, unit)
    next_ = {
        'method': 'GET',
        'path': '/s/cards/{card_id}/learn'
                .format(card_id=card['entity_id']),
    }
    set_learning_context(
        current_user,
        next=next_, unit=unit, card=card)
# When in learn or review mode, lead me to choose a unit.
elif buckets['review'] or buckets['learn']:
    next_ = {
        'method': 'GET',
        'path': '/s/subjects/{subject_id}/units'
                .format(subject_id=subject_id),
    }
    set_learning_context(current_user, next=next_)
# If the subject is complete, lead the learner to choose another subject.
else:
    next_ = {
        'method': 'GET',
        'path': '/s/users/{user_id}/subjects'
                .format(user_id=current_user['id']),
    }
    set_learning_context(current_user, next=next_, unit=None, subject=None)



view choose unit
----------------
context = get_learning_context(current_user)
next_ = {
    'method': 'POST',
    'path': '/s/subjects/{subject_id}/units/{unit_id}'
              .format(
                  subject_id=context.get('subject', {}).get('entity_id'),
                  unit_id='{unit_id}'),
}
set_learning_context(current_user, next=next_)
subject = get_latest_accepted('subjects', db_conn, subject_id)
# Pull a list of up to 5 units to choose from based on priority.
buckets = traverse(db_conn, current_user, subject)
units = buckets['learn'][:5]



choose a unit
-------------
# If the unit isn't in the subject...
context = get_learning_context(current_user)
subject_ids = [
    subject['entity_id']
    for subject in list_subjects_by_unit_id(db_conn, unit_id)]
if context.get('subject', {}).get('entity_id') not in subject_ids:
    return abort(400)
status = judge(db_conn, unit, current_user)
# Or, the unit doesn't need to be learned...
if status == "done":
    return abort(400)
# Choose a card for the learner to learn
card = choose_card(db_conn, current_user, unit)
if card:
    next_ = {
        'method': 'GET',
        'path': '/s/cards/{card_id}/learn'
                .format(card_id=card['entity_id']),
    }
else:
    next_ = {}
set_learning_context(
    current_user,
    unit=unit,
    card=card if card else None,
    next=next_
)


view learn card
---------------
# Make sure the current unit id matches the card
context = get_learning_context(current_user)
if context.get('unit', {}).get('entity_id') != card['unit_id']:
    return abort(400)
next_ = {
    'method': 'POST',
    'path': '/s/cards/{card_id}/responses'
            .format(card_id=card['entity_id'])
}
set_learning_context(current_user, card=card, next=next_)


respond to card
---------------

# Make sure the card is the current one
context = get_learning_context(current_user)
if context.get('card', {}).get('entity_id') != card['entity_id']:
    return abort(400)
r = seq_update(db_conn, current_user, card,
               request['params'].get('response'))
errors, response, feedback = (r.get('errors'), r.get('response'),
                              r.get('feedback'))
if errors:
    return 400, {
        'errors': errors,
        'ref': 'wtyOJPoy4bh76OIbYp8mS3LP',
    }

subject = context.get('subject')
unit = context.get('unit')

status = judge(db_conn, unit, current_user)

# If we are done with this current unit...
if status == "done":
    buckets = traverse(db_conn, current_user, subject)

    # If there are units to be diagnosed...
    if buckets['diagnose']:
        unit = buckets['diagnose'][0]
        next_card = choose_card(db_conn, current_user, unit)
        next_ = {
            'method': 'GET',
            'path': '/s/cards/{card_id}/learn'
                    .format(card_id=next_card['entity_id']),
        }
        set_learning_context(
            current_user,
            card=next_card.data, unit=unit, next=next_)

    # If there are units to be learned or reviewed...
    elif buckets['learn'] or buckets['review']:
        next_ = {
            'method': 'GET',
            'path': '/s/subjects/{subject_id}/units'
                    .format(subject_id=subject['entity_id']),
        }
        set_learning_context(current_user,
                             card=None, unit=None, next=next_)

    # If we are out of units...
    else:
        next_ = {
            'method': 'GET',
            'path': '/s/subjects/{subject_id}/tree'
                    .format(subject_id=subject['entity_id']),
        }
        set_learning_context(current_user,
                             card=None, unit=None, next=next_)

# If we are still reviewing, learning or diagnosing this unit...
else:
    next_card = choose_card(db_conn, current_user, unit)
    if next_card:
        next_ = {
            'method': 'GET',
            'path': '/s/cards/{card_id}/learn'
                    .format(card_id=next_card['entity_id']),
        }
        set_learning_context(current_user, card=next_card, next=next_)
    else:
        next_ = {}
        set_learning_context(current_user, next=next_)

"""
