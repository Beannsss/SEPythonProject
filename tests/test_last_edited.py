import time
import unittest

timestamps = {}


def update_timestamp(url):
    """ Gets the current date adds/updates dictionary with new date with the key(url)
    """
    now = time.strftime("%m/%d/%Y")
    timestamps[url] = now


def get_timestamp(url):
    """ Given a key(url) this returns the last updated date
    """
    if url in timestamps.keys():
        return "Last updated: " + timestamps[url]
    else:
        return "This page has not been updated since the addition of this feature"


def remove_timestamp(url):
    """ If a page is removed/moved then the key value pair is removed from the dictionary
    """
    if url in timestamps.keys():
        del timestamps[url]


def set_timestamp(url, date):
    timestamps[url] = date


def clear_all_timestamps():
    timestamps.clear()


def get_date(url):
    return timestamps[url]


def timestamps_contains(url):
    return url in timestamps.keys()


class TestLastEdited(unittest.TestCase):

    def test_update_timestamp(self):
        url = 'test url'
        old_date = '10/10/2010'
        set_timestamp(url, old_date)

        now = time.strftime("%m/%d/%Y")
        self.assertEqual(get_date(url), old_date)
        update_timestamp(url)
        self.assertEqual(get_date(url), now)

        clear_all_timestamps()

    def test_get_timestamp(self):
        url = 'test url'
        old_date = '10/10/2010'
        set_timestamp(url, old_date)

        self.assertEqual(get_timestamp(url), 'Last updated: ' + old_date)

        clear_all_timestamps()
        self.assertEqual(get_timestamp(url), 'This page has not been updated since the addition of this feature')

    def test_remove_timestamp(self):
        url = 'test url'
        old_date = '10/10/2010'
        set_timestamp(url, old_date)

        self.assertEqual(timestamps_contains(url), True)
        remove_timestamp(url)
        self.assertEqual(timestamps_contains(url), False)

        clear_all_timestamps()
