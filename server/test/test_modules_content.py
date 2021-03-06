from modules import content
import pytest

xfail = pytest.mark.xfail


def test_get():
    # Expect to get content in the right language
    assert content.get('required') == 'Required.'
    assert content.get('required', 'eo') == 'Postulo.'


def test_get_default():
    # Expect to show English if language isn't available.
    assert (content.get('required') ==
            content.get('required', 'en'))


@xfail
def test_get_no_country():
    # Expect to show base language if missing country-specific.
    assert False
