from pathlib import Path

import signal_parsers as sp


def data_file(name):
    return Path(Path(__file__).parent, 'data', name)


def test_rsrq():
    moni_string = data_file('test_moni_5g.txt').read_text()
    assert sp.get_rsrp(moni_string) is None
    assert sp.get_nr_rsrp(moni_string) == -71
