import re


def get_rsrp(moni_string):
    rsrp = re.search(r' RSRP:(?P<rsrp>-?\d+)', moni_string)

    if rsrp:
        return int(rsrp.group('rsrp'))
    else:
        return None


def get_rsrq(moni_string):
    rsrq = re.search(r' RSRQ:(?P<rsrq>-?\d+)', moni_string)

    if rsrq:
        return int(rsrq.group('rsrq'))
    else:
        return None


def get_nr_rsrp(moni_string):
    rsrp = re.search(r' NR_RSRP:(?P<rsrp>-?\d+)', moni_string)

    if rsrp:
        return int(rsrp.group('rsrp'))
    else:
        return None


def get_nr_rsrq(moni_string):
    rsrq = re.search(r' NR_RSRQ:(?P<rsrq>-?\d+)', moni_string)

    if rsrq:
        return int(rsrq.group('rsrq'))
    else:
        return None
