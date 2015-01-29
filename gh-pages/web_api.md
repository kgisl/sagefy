---
layout: default
title: Sagefy Web API
---

This document outlines the endpoints for Sagefy and their specifications.

Errors will appear in the following format, along with the appropriate status code (400, 401, 403, 404):

```json
{
    "errors": [{
        "name": "field",
        "message": "The reason for the error."
    }]
}
```

Here I use _Request Parameters_ for GET and DELETE and _Request Format_ for POST, PATCH, and PUT.

Public
======

Not much to see here, move along.

Welcome
-------

`GET https://sagefy.org/api/`

Welcome the developer to the API.

### Request Parameters

None

### Response Format

```json
{
    "message": "Welcome to Sagefy."
}
```

Users
=====

The users endpoints are largely around CRUD operations for the users table, and additionally account related activities like log in and forgot password.

Get User By ID
--------------

`GET https://sagefy.org/api/users/{id}/`

Get the user information given a user ID.

### Request Parameters

None

### Response Format (200)

```json
{
    "user": {
        "name": "test",
        "email": "test@example.com",
        "email_frequency": "immediate"
    }
}
```

`email` and `email_frequency` are private and only available to the self user.

Returns a 404 if user is not found.

Get Current User
----------------

`GET https://sagefy.org/api/users/current/`

Get the current user's information, if available.

### Request Parameters

None

### Response Format (200)

```json
{
    "user": {
        "name": "test",
        "email": "test@example.com",
        "email_frequency": "immediate"
    }
}
```

`email` and `email_frequency` are private and only available to the self user.

Returns a 401 if a user is not logged in.

Create User
-----------

`POST https://sagefy.org/api/users/`

Create a new user account.

### Request Format

```json
{
    "name": "test",
    "email": "test@example.com",
    "password": "abcd1234"
}
```

### Response Format (200)

```json
{
    "user": {
        "name": "test",
        "email": "test@example.com",
        "email_frequency": "immediate"
    }
}
```

Returns a 400 if there are errors, such as email already used or password too short.

Log In User
-----------

`POST https://sagefy.org/api/users/login/`

Log in as an existing user.

### Request Format

```json
{
    "name": "test",
    "password": "abcd1234"
}
```

### Response Format (200)

```json
{
    "user": {
        "name": "test",
        "email": "test@example.com",
        "email_frequency": "immediate"
    }
}
```

Returns 404 if the user by name is not found. Returns a 400 if the password is not valid.

Log Out User
------------

`POST https://sagefy.org/api/users/logout/`

Log out of the current user.

### Request Format

None

### Response Format (204)

None

Update User
-----------

`PUT https://sagefy.org/api/users/{id}/`

Update the user. Must be the current user.

### Request Format

```json
{
    "name": "test",
    "email": "test@example.com",
    "password": "abcd1234"
}
```

### Response Format (200)

```json
{
    "user": {
        "name": "test",
        "email": "test@example.com",
        "email_frequency": "immediate"
    }
}
```

Return a 404 if no user matching that ID. Return 401 if not the current user. Return 400 for parameter issues.

Create Password Token
---------------------

`POST https://sagefy.org/api/users/token/`

Email a token to be able to reset the password.

### Request Format

```json
{
    "email": "test@example.com"
}
```

### Response Format (204)

None

Return a 404 if it cannot find the user's email.

Create Password
---------------

`POST https://sagefy.org/api/users/password/`

Update the user's password. Must have a matching and timely token.

### Request Format

```json
{
    "id": "ABCD1234",
    "token": "JFDN32JL29af",
    "password": "abcd1234"
}
```

### Response Format (200)

```json
{
    "user": {
        "name": "test",
        "email": "test@example.com",
        "email_frequency": "immediate"
    }
}
```

200 also logs in user. 404 if not a valid user ID. 403 if the token doesn't match.

Get User Menu
-------------

`GET https://sagefy.org/api/users/{id}/menu/`

...

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Get User Sets
-------------

`GET https://sagefy.org/api/users/{id}/sets/`

...

### Request Parameters

```json

```

### Response Format

```json

```

Add User Set
------------

`POST https://sagefy.org/api/users/{id}/sets/`

...

### Request Format

```json

```

### Response Format


```json

```

Remove User Set
---------------

`DELETE https://sagefy.org/api/users/{id}/sets/{id}/`

...

### Request Parameters

None

### Response Format

```json

```

Cards
=====

...

Get Card Information
--------------------

`GET https://sagefy.org/api/cards/{id}/`

Get a specific card given an ID. Show all relevant data, but
not used for the learning interface.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Render Card for Learner
-----------------------

`GET https://sagefy.org/api/cards/{id}/learn/`

Render the card's data, ready for learning.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Respond to Card
---------------

`POST https://sagefy.org/api/cards/{id}/responses/`

Record and process a learner's response to a card.

### Request Format

```json

```

### Response Format


```json

```

Units
=====

...

Get Unit Information
--------------------

`GET https://sagefy.org/api/units/{id}/`

Get a specific unit given an ID.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Sets
====

...

Get Set Information
-------------------

`GET https://sagefy.org/api/sets/{id}/`

Get a specific set given an ID.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Get Set Tree
------------

`GET https://sagefy.org/api/sets/{id}/tree/`

Render the tree of units that exists within a set.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Show Available Units from Set
-----------------------------

`GET https://sagefy.org/api/sets/{id}/units/`

Render the units that exist within the set.
Specifically, present a small number of units the learner can choose
from.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Choose Unit
-----------

`POST https://sagefy.org/api/sets/{id}/units/{id}/`

Updates the learner's information based on the unit they have chosen.

### Request Format

```json

```

### Response Format


```json

```

Sequencer
=========

...

Next
----

`GET https://sagefy.org/api/sequencer/next/`

Tell the learner where to go next.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Search
======

...

Search
------

`GET https://sagefy.org/api/search/`

Search for entities.

### Request Parameters

Name | Default | Description
-----|---------|------------
... | ... | ...

### Response Format

```json

```

Topic
=====

Topics, or threads, are the entity that hold a conversation, a list of posts. The Topic API handles both topics and posts, as posts always belong to a single topic.

Create Topic
------------

`POST https://sagefy.org/api/topics/`

Create a new topic. The first post (proposal, flag) must be provided.
Flag: if a flag for the same reason exists for the entity, create a vote there instead.

### Request Format

```json
{
    "topic": {
        "name": "Lorem ipsum.",
        "entity": {
            "kind": "card",
            "id": "fj204lasZ"
        }
    },
    "post": {
        "body": "Lorem ipsum.",
        "kind": "post",
        "replies_to_id": "a42lf9"
    }
}
```

When creating a topic, you must also submit information for a valid post. There are four post kinds. All require the "kind" field filled out. Replies to ID is optional. Proposals also require an entity version ID, name, status, and action. Votes have optional bodies, but require "replies_to_id" and "response". Flag requires entity version ID, name, reason, and status.

### Response Format

```json
{
    "topic": {
        "id": "fjkls234",
        "name": "Lorem ipsum.",
        "entity": {
            "kind": "card",
            "id": "fj204lasZ"
        }
    },
    "post": {
        "user_id": "ajfkl234",
        "body": "Lorem ipsum.",
        "kind": "post",
        "replies_to_id": "a42lf9",
        "topic_id": "fjkls234"
    }
}
```

Returns 400 if missing or invalid topic or post information. Return 401 if not logged in as a user.

Update Topic Name
-----------------

`PUT https://sagefy.org/api/topics/{id}/`

Update the topic. Only the name can be changed. Only by original author.

### Request Format

```json
{
    "name": "Neo name."
}
```

### Response Format


```json
{
    "topic": {
        "id": "fjkls234",
        "name": "Neo name.",
        "entity": {
            "kind": "card",
            "id": "fj204lasZ"
        }
    }
}
```

401 if not logged in. 404 if topic by ID not found. 403 if not user's own topic. 400 if there's issues with the name field.

Get Posts
---------

`GET https://sagefy.org/api/topics/{id}/posts/`

Get a reverse chronological listing of posts for given topic.
Includes topic meta data and posts (proposals, votes, flags).
Paginates.

### Request Parameters

Name     | Default | Description
---------|---------|------------
limit    | null    | Maximum number of posts to return.
skip     | 0       | Offset the return by count.

### Response Format

```json
{
    "posts": [{
        "user_id": "ajfkl234",
        "body": "Lorem ipsum.",
        "kind": "post",
        "replies_to_id": "a42lf9",
        "topic_id": "fjkls234"
    }]
}
```

Returns 404 if topic not found. Posts can be one of post, proposal, vote, or flag. The kind changes the field available.

Create Post
-----------

`POST https://sagefy.org/api/topics/{id}/posts/`

Create a new post on a given topic.
Accounts for posts, proposals, votes, and flags.
Proposal: must include entity (card, unit, set) information.
Vote: must refer to a proposal.

### Request Format

```json
{
    "body": "Lorem ipsum.",
    "kind": "post",
    "replies_to_id": "a42lf9"
}
```

### Response Format


```json
{
    "user_id": "ajfkl234",
    "body": "Lorem ipsum.",
    "kind": "post",
    "replies_to_id": "a42lf9",
    "topic_id": "fjkls234"
}
```

401 if not logged in. 404 if topic not found. 400 if issue presented with content.

Update Post
-----------

`PUT https://sagefy.org/api/topics/{id}/post/{id}/`

Update an existing post. Must be one's own post.
For proposals:
The only field that can be updated is the status;
the status can only be changed to declined, and only when
the current status is pending or blocked.

### Request Format

```json
{
    "body": "Neo body."
}
```

### Response Format


```json
{
    "user_id": "ajfkl234",
    "body": "Neo body.",
    "kind": "post",
    "replies_to_id": "a42lf9",
    "topic_id": "fjkls234"
}
```

401 if not logged in. 403 if not own post. 400 if issues with content.

Follow
======

Follows allow users to subscribe to updates on cards, units, and sets.

Follow
------

`POST https://sagefy.org/api/follows/`

Current user follows an entity, topic, or proposal.

### Request Format

```json

```

### Response Format


```json

```

Unfollow
--------

`DELETE https://sagefy.org/api/follows/{id}/`

Remove a follow. Must be current user's own follow.

### Request Format

None

### Response Format


```json

```

Notices
=======

Notices provide updates to users on cards, units, and sets they follow.

List Notices
------------

`GET https://sagefy.org/api/notices/`

List notices for current user.

### Request Parameters

Name  | Default | Description
------|---------|------------
limit | null    | Maximum number of notices to return.
skip  | 0       | Offset in returned set.
tag   | ''      | Filter by a specific tag.
read  | null    | Filter by read or unread notices.

### Response Format

```json
{
    "notices": [{
        "id": "abcd1234",
        "user_id": "fjskl234",
        "kind": "new_proposal",
        "read": false,
        "tags": ["analyze"]
    }]
}
```

Returns a 401 if there's no user currently logged in.

Mark Notice as Read
-------------------

`PUT https://sagefy.org/api/notices/{id}/read/`

Mark notice as read.
Must be logged in as user, provide a valid ID, and own the notice.
Return notice.

### Request Format

None

### Response Format


```json
{
    "notice": {
        "id": "abcd1234",
        "user_id": "fjskl234",
        "kind": "new_proposal",
        "read": false,
        "tags": ["analyze"]
    }
}
```

Returns 401 if not logged in. Returns 404 if notice not found. Returns 403 if not user's own notice. Returns 400 if issues saving to the database.

Mark Notice as Unread
---------------------

`PUT https://sagefy.org/api/notices/{id}/unread/`

Mark notice as unread.
Must be logged in as user, provide a valid ID, and own the notice.
Return notice.

### Request Format

None

### Response Format


```json
{
    "notice": {
        "id": "abcd1234",
        "user_id": "fjskl234",
        "kind": "new_proposal",
        "read": false,
        "tags": ["analyze"]
    }
}
```

Returns 401 if not logged in. Returns 404 if notice not found. Returns 403 if not user's own notice. Returns 400 if issues saving to the database.