import pytest
from database.entity_base import get_versions, get_latest_accepted, \
    list_requires, list_required_by
import rethinkdb as r


xfail = pytest.mark.xfail


def test_latest_accepted_card(db_conn, cards_table):
    """
    Expect to get the latest accepted card version.
    """

    cards_table.insert([{
        'id': 'A1',
        'entity_id': 'A',
        'created': r.time(2004, 11, 3, 'Z'),
        'status': 'accepted',
    }, {
        'id': 'B2',
        'entity_id': 'A',
        'created': r.time(2005, 11, 3, 'Z'),
        'status': 'accepted',
    }, {
        'id': 'C3',
        'entity_id': 'B',
        'created': r.time(2006, 11, 3, 'Z'),
        'status': 'accepted',
    }]).run(db_conn)

    card = get_latest_accepted('cards', db_conn, 'A')
    assert card['id'] == 'B2'


def test_latest_accepted(db_conn, units_table):
    """
    Expect to get the latest accepted unit version.
    """

    units_table.insert([{
        'id': 'A1',
        'entity_id': 'A',
        'created': r.time(2004, 11, 3, 'Z'),
        'status': 'accepted',
    }, {
        'id': 'B2',
        'entity_id': 'A',
        'created': r.time(2005, 11, 3, 'Z'),
        'status': 'accepted',
    }, {
        'id': 'C3',
        'entity_id': 'B',
        'created': r.time(2006, 11, 3, 'Z'),
        'status': 'accepted',
    }]).run(db_conn)

    unit = get_latest_accepted('units', db_conn, 'A')
    assert unit['id'] == 'B2'


def test_latest_accepted_subject(db_conn, subjects_table):
    """
    Expect to get the latest accepted subject version.
    """

    subjects_table.insert([{
        'id': 'A1',
        'entity_id': 'A',
        'created': r.time(2004, 11, 3, 'Z'),
        'status': 'accepted',
    }, {
        'id': 'B2',
        'entity_id': 'A',
        'created': r.time(2005, 11, 3, 'Z'),
        'status': 'accepted',
    }, {
        'id': 'C3',
        'entity_id': 'B',
        'created': r.time(2006, 11, 3, 'Z'),
        'status': 'accepted',
    }]).run(db_conn)

    subject = get_latest_accepted('subjects', db_conn, 'A')
    assert subject['id'] == 'B2'


def test_get_versions(db_conn, cards_table):
    """
    Expect to get the latest versions of the card.
    """

    cards_table.insert([{
        'id': 'A1',
        'entity_id': 'A',
        'created': r.time(2004, 11, 3, 'Z'),
        'status': 'accepted',
    }, {
        'id': 'B2',
        'entity_id': 'A',
        'created': r.time(2005, 11, 3, 'Z'),
    }, {
        'id': 'C3',
        'entity_id': 'B',
        'created': r.time(2006, 11, 3, 'Z'),
        'status': 'accepted',
    }]).run(db_conn)

    card_versions = get_versions('cards', db_conn, 'A')

    assert len(card_versions) == 2


def test_list_requires(db_conn, cards_table):
    """
    Expect to list all the prereqs for the entity.
    """

    cards_table.insert([{
        'entity_id': 'abcd',
        'unit_id': 'zytx',
        'created': r.now(),
        'modified': r.now(),
        'status': 'accepted',
        'kind': 'video',
        'require_ids': ['zxyz'],
    }, {
        'entity_id': 'abcd',
        'unit_id': 'zytx',
        'created': r.time(1986, 11, 3, 'Z'),
        'modified': r.time(1986, 11, 3, 'Z'),
        'status': 'accepted',
        'kind': 'video',
    }, {
        'entity_id': 'zxyz',
        'unit_id': 'zytx',
        'created': r.now(),
        'modified': r.now(),
        'status': 'accepted',
        'kind': 'video',
    }, {
        'entity_id': 'qwer',
        'unit_id': 'zytx',
        'created': r.now(),
        'modified': r.now(),
        'status': 'accepted',
        'kind': 'choice',
        'require_ids': ['abcd'],
    }]).run(db_conn)

    cards = list_requires('cards', db_conn, 'abcd')

    assert len(cards) == 1
    assert cards[0]['entity_id'] == 'zxyz'


def test_list_required_by(db_conn, cards_table):
    """
    Expect to list all the entity that require the given one.
    """

    cards_table.insert([{
        'entity_id': 'abcd',
        'unit_id': 'zytx',
        'created': r.now(),
        'modified': r.now(),
        'status': 'accepted',
        'kind': 'video',
        'require_ids': ['zxyz'],
    }, {
        'entity_id': 'abcd',
        'unit_id': 'zytx',
        'created': r.time(1986, 11, 3, 'Z'),
        'modified': r.time(1986, 11, 3, 'Z'),
        'status': 'accepted',
        'kind': 'video',
    }, {
        'entity_id': 'zxyz',
        'unit_id': 'zytx',
        'created': r.now(),
        'modified': r.now(),
        'status': 'accepted',
        'kind': 'video',
    }, {
        'entity_id': 'qwer',
        'unit_id': 'zytx',
        'created': r.now(),
        'modified': r.now(),
        'status': 'accepted',
        'kind': 'choice',
        'require_ids': ['abcd'],
    }]).run(db_conn)

    cards = list_required_by('cards', db_conn, 'abcd')

    assert len(cards) == 1
    assert cards[0]['entity_id'] == 'qwer'
