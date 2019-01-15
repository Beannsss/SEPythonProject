import csv
import time

timestamps = {}
timestamp_filename = "wiki\web\persistent\last_edited"


def update_timestamp(url):
    """ Gets the current date adds/updates dictionary with new date with the key(url)
    """
    now = time.strftime("%m/%d/%Y")
    timestamps[url] = now
    save_timestamps()


def save_timestamps():
    """ Saves the current dictionary into a file so that the last updated dates are saved
        for the next time the system is ran
    """
    out_file = open(timestamp_filename, 'w', newline='')
    writer = csv.writer(out_file)
    for key, val in timestamps.items():
        writer.writerow([key, val])
    out_file.close()


def read_timestamps():
    """ Reads the dictionary of timestamps in from the last time the system was ran for any
        page that gets loaded
    """

    in_file = open(timestamp_filename, 'r')
    reader = csv.reader(in_file)
    for row in reader:
        if len(row) != 0:
            key, value = row
            if key not in timestamps.keys():
                timestamps[key] = value
    in_file.close()


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
        save_timestamps()
