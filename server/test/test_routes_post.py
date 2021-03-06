import pytest
from conftest import create_user_in_db
import rethinkdb as r
import routes.post

xfail = pytest.mark.xfail


def create_topic_in_db(topics_table, db_conn, user_id='abcd1234'):
    topics_table.insert({
        'id': 'wxyz7890',
        'created': r.now(),
        'modified': r.now(),
        'user_id': user_id,
        'name': 'A Modest Proposal',
        'entity': {
            'id': 'efgh5678',
            'kind': 'unit'
        }
    }).run(db_conn)


def create_post_in_db(posts_table, db_conn, user_id='abcd1234'):
    posts_table.insert({
        'id': 'jklm',
        'created': r.now(),
        'modified': r.now(),
        'user_id': user_id,
        'topic_id': 'wxyz7890',
        'body': '''A Modest Proposal for Preventing the Children of Poor
            People From Being a Burthen to Their Parents or Country, and
            for Making Them Beneficial to the Publick.''',
        'kind': 'post',
    }).run(db_conn)


def create_proposal_in_db(posts_table, units_table, db_conn):
    posts_table.insert({
        'id': 'jklm',
        'created': r.now(),
        'modified': r.now(),
        'user_id': 'abcd1234',
        'topic_id': 'wxyz7890',
        'body': '''A Modest Proposal for Preventing the Children of Poor
            People From Being a Burthen to Their Parents or Country, and
            for Making Them Beneficial to the Publick.''',
        'kind': 'proposal',
        'name': 'New Unit',
        'replies_to_id': None,
        'entity_versions': [{
            'id': 'slash-1',
            'kind': 'unit',
        }],
    }).run(db_conn)

    units_table.insert({
        'id': 'slash-1',
        'created': r.time(2014, 1, 1, 'Z'),
        'modified': r.time(2014, 1, 1, 'Z'),
        'entity_id': 'slash',
        'previous_id': None,
        'language': 'en',
        'name': 'Dividing two numbers.',
        'status': 'accepted',
        'available': True,
        'tags': ['math'],
        'body': 'The joy and pleasure of dividing numbers.',
        'require_ids': ['plus', 'minus', 'times'],
    }).run(db_conn)


def test_get_posts(db_conn, users_table, topics_table, posts_table):
    """
    Expect to get posts for given topic.
    """

    create_user_in_db(users_table, db_conn)
    create_topic_in_db(topics_table, db_conn)
    posts_table.insert([{
        'id': 'jklm',
        'created': r.now(),
        'modified': r.now(),
        'user_id': 'abcd1234',
        'topic_id': 'wxyz7890',
        'body': '''A Modest Proposal for Preventing the Children of Poor
            People From Being a Burthen to Their Parents or Country, and
            for Making Them Beneficial to the Publick.''',
        'kind': 'post',
    }, {
        'id': 'tyui',
        'created': r.now(),
        'modified': r.now(),
        'user_id': 'abcd1234',
        'topic_id': 'wxyz7890',
        'body': 'A follow up.',
        'kind': 'post',
    }]).run(db_conn)

    request = {
        'params': {},
        'db_conn': db_conn
    }
    code, response = routes.post.get_posts_route(request, 'wxyz7890')
    assert code == 200
    assert ('Beneficial to the Publick' in response['posts'][0]['body']
            or 'Beneficial to the Publick' in response['posts'][1]['body'])


def test_get_posts_not_topic(db_conn, users_table, topics_table,
                             posts_table):
    """
    Expect 404 to get posts for a nonexistant topic.
    """

    request = {
        'params': {},
        'db_conn': db_conn
    }
    code, response = routes.post.get_posts_route(request, 'wxyz7890')
    assert code == 404


def test_get_posts_paginate(db_conn, users_table, topics_table,
                            posts_table):
    """
    Expect get posts for topic to paginate.
    """
    create_user_in_db(users_table, db_conn)
    create_topic_in_db(topics_table, db_conn)
    for i in range(0, 25):
        posts_table.insert({
            'id': 'jklm%s' % i,
            'created': r.now(),
            'modified': r.now(),
            'user_id': 'abcd1234',
            'topic_id': 'wxyz7890',
            'body': 'test %s' % i,
            'kind': 'post',
        }).run(db_conn)

    request = {
        'params': {},
        'db_conn': db_conn
    }
    code, response = routes.post.get_posts_route(request, 'wxyz7890')
    assert code == 200
    assert len(response['posts']) == 10
    request.update({'params': {'skip': 20}})
    code, response = routes.post.get_posts_route(request, 'wxyz7890')
    assert len(response['posts']) == 5


def test_get_posts_proposal(db_conn, users_table, units_table, topics_table,
                            posts_table):
    """
    Expect get posts for topic to render a proposal correctly.
    """

    create_user_in_db(users_table, db_conn)
    create_topic_in_db(topics_table, db_conn)
    create_proposal_in_db(posts_table, units_table, db_conn)

    request = {
        'params': {},
        'db_conn': db_conn,
    }
    code, response = routes.post.get_posts_route(request, 'wxyz7890')
    assert code == 200
    assert response['posts'][0]['kind'] == 'proposal'


def test_get_posts_votes(db_conn, users_table, units_table, topics_table,
                         posts_table):
    """
    Expect get posts for topic to render votes correctly.
    """

    create_user_in_db(users_table, db_conn)
    create_topic_in_db(topics_table, db_conn)
    create_proposal_in_db(posts_table, units_table, db_conn)
    posts_table.insert({
        'id': 'asdf4567',
        'created': r.now(),
        'modified': r.now(),
        'kind': 'vote',
        'body': 'Hooray!',
        'proposal_id': 'jklm',
        'topic_id': 'wxyz7890',
        'response': True,
        'user_id': 'abcd1234',
    }).run(db_conn)

    request = {
        'params': {},
        'db_conn': db_conn
    }
    code, response = routes.post.get_posts_route(request, 'wxyz7890')

    assert code == 200
    assert response['posts'][0]['kind'] in ('proposal', 'vote')
    assert response['posts'][1]['kind'] in ('proposal', 'vote')


def test_create_post(db_conn, users_table, topics_table, posts_table,
                     session):
    """
    Expect create post.
    """

    create_topic_in_db(topics_table, db_conn)
    request = {
        'cookies': {'session_id': session},
        'params': {
            # Should default to > 'kind': 'post',
            'body': '''A Modest Proposal for Preventing the Children of
                Poor People From Being a Burthen to Their Parents or
                Country, and for Making Them Beneficial to the Publick.''',
            'kind': 'post',
            'topic_id': 'wxyz7890',
        },
        'db_conn': db_conn
    }
    code, response = routes.post.create_post_route(request, 'wxyz7890')
    assert code == 200
    assert 'Beneficial to the Publick' in response['post']['body']


def test_create_post_errors(db_conn, users_table, topics_table,
                            posts_table, session):
    """
    Expect create post missing field to show errors.
    """

    create_topic_in_db(topics_table, db_conn)
    request = {
        'cookies': {'session_id': session},
        'params': {
            'kind': 'post',
            'topic_id': 'wxyz7890',
        },
        'db_conn': db_conn
    }
    code, response = routes.post.create_post_route(request, 'wxyz7890')
    assert code == 400
    assert 'errors' in response


def test_create_post_log_in(db_conn, users_table, topics_table,
                            posts_table):
    """
    Expect create post to require log in.
    """

    create_topic_in_db(topics_table, db_conn)
    request = {
        'params': {
            # Should default to > 'kind': 'post',
            'body': '''A Modest Proposal for Preventing the Children of Poor
                People From Being a Burthen to Their Parents or Country, and
                for Making Them Beneficial to the Publick.''',
            'kind': 'post',
            'topic_id': 'wxyz7890',
        },
        'db_conn': db_conn
    }
    code, response = routes.post.create_post_route(request, 'wxyz7890')

    assert code == 401
    assert 'errors' in response


@xfail
def test_create_post_proposal(db_conn, users_table, topics_table,
                              posts_table, session):
    """
    Expect create post to create a proposal.
    """

    create_topic_in_db(topics_table, db_conn)
    request = {
        'params': {
            'kind': 'proposal',
            'name': 'New Unit',
            'body': '''A Modest Proposal for Preventing the Children of
                Poor People From Being a Burthen to Their Parents or
                Country, and for Making Them Beneficial to the Publick.''',
        },
        'db_conn': db_conn
    }
    code, response = routes.post.create_post_route(request, 'wxyz7890')
    assert code == 200
    assert response['post']['kind'] == 'proposal'


@xfail
def test_create_post_vote(db_conn, users_table, topics_table,
                          posts_table, session):
    """
    Expect create post to create a vote.
    """

    create_topic_in_db(topics_table, db_conn)
    request = {
        'params': {
            'kind': 'vote',
            'body': 'Hooray!',
            'proposal_id': 'jklm',
            'response': True,
        },
        'db_conn': db_conn
    }
    code, response = routes.post.create_post_route(request, 'wxyz7890')
    assert code == 200
    assert response['post']['kind'] == 'vote'


def test_update_post_log_in(db_conn, users_table, topics_table,
                            posts_table):
    """
    Expect update post to require log in.
    """

    create_user_in_db(users_table, db_conn)
    create_topic_in_db(topics_table, db_conn)
    create_post_in_db(posts_table, db_conn)
    request = {
        'params': {
            'body': 'Update.'
        },
        'db_conn': db_conn
    }
    code, response = routes.post.update_post_route(
        request, 'wxyz7890', 'jklm')

    assert code == 401
    assert 'errors' in response


def test_update_post_author(db_conn, users_table, topics_table,
                            posts_table, session):
    """
    Expect update post to require own post.
    """

    create_topic_in_db(topics_table, db_conn)
    create_post_in_db(posts_table, db_conn, user_id='1234yuio')
    request = {
        'cookies': {'session_id': session},
        'params': {
            'body': 'Update.'
        },
        'db_conn': db_conn
    }
    code, response = routes.post.update_post_route(
        request, 'wxyz7890', 'jklm')
    assert code == 403
    assert 'errors' in response


def test_update_post_body(db_conn, users_table, topics_table,
                          posts_table, session):
    """
    Expect update post to change body for general post.
    """

    create_topic_in_db(topics_table, db_conn)
    create_post_in_db(posts_table, db_conn)
    request = {
        'cookies': {'session_id': session},
        'params': {
            'body': 'Update.'
        },
        'db_conn': db_conn,
    }
    code, response = routes.post.update_post_route(
        request, 'wxyz7890', 'jklm')
    assert not response.get('errors')
    assert code == 200
    assert 'Update' in response['post']['body']


@xfail
def test_update_proposal(db_conn, users_table, topics_table,
                         posts_table, units_table, session):
    """
    Expect update post to handle proposals correctly.
    """

    create_topic_in_db(topics_table, db_conn)
    create_proposal_in_db(posts_table, units_table, db_conn)

    request = {
        'cookies': {'session_id': session},
        'params': {
            'status': 'declined'
        },
        'db_conn': db_conn,
    }
    code, response = routes.post.update_post_route(
        request, 'wxyz7890', 'jklm')

    assert code == 200
    assert 'declined' in response['post']['status']


@xfail
def test_update_vote(db_conn, users_table, topics_table,
                     posts_table, units_table, session):
    """
    Expect update vote to handle proposals correctly.
    """

    create_user_in_db(users_table, db_conn)
    create_topic_in_db(topics_table, db_conn)
    create_proposal_in_db(posts_table, units_table, db_conn)
    posts_table.insert({
        'id': 'vbnm1234',
        'created': r.now(),
        'modified': r.now(),
        'user_id': 'abcd1234',
        'topic_id': 'wxyz7890',
        'proposal_id': 'jklm',
        'body': 'Boo!',
        'response': False,
        'kind': 'vote',
        'replies_to_id': 'val2345t',
    }).run(db_conn)

    request = {
        'cookies': {'session_id': session},
        'params': {
            'body': 'Yay!',
            'response': True,
        },
        'db_conn': db_conn
    }
    code, response = routes.post.update_post_route(
        request, 'wxyz7890', 'vbnm1234')
    assert code == 200
    assert True is response['post']['response']
