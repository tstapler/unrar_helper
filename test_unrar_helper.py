from pathlib import Path
from typing import List

import py
import pytest

from unrar_helper import needs_unrar, Situation


def prep_tempdir(tmpdir: py.path, layout: List[str]):
    for file in layout:
        tmpdir.join(file).ensure(file=True)


@pytest.mark.parametrize('directory_layout,expected_situation', [
    (["torrent_name.mkv"], Situation.NO_RARS),
    (["torrent_name.rar"], Situation.NEEDS_UNRAR),
    (["torrent_name.r01",
      "torrent_name.r02",
      "torrent_name.r03",
      "torrent_name.r04"], Situation.NEEDS_UNRAR),
    (["torrent_name.mkv",
      "torrent_name.rar",
      "torrent_name.r01",
      "torrent_name.r02",
      "torrent_name.r03",
      "torrent_name.r04"], Situation.NEEDS_CLEANUP),
    (["torrent_name-DISTRO.mkv",
      "torrent_name-distro.rar",
      "torrent_name-distro.r01",
      "torrent_name-distro.r02",
      "torrent_name-distro.r03",
      "torrent_name-distro.r04"], Situation.NEEDS_CLEANUP),
    (["torrent_name-DISTRO.mkv",
      "torrent_name-distro.rar",
      ], Situation.COMPLETE),
    (["torrent_name-DISTRO.mkv",
      "torrent_name-distro.r01",
      "torrent_name-distro.r02",
      ], Situation.COMPLETE),
])
def test_needs_unrar(tmpdir, directory_layout, expected_situation):
    prep_tempdir(tmpdir, directory_layout)
    assert needs_unrar(Path(tmpdir)) == expected_situation

