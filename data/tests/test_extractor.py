import pathlib
import shutil
import sys

import pytest

# NOTE: worth making this a package to improve imports? Or overkill..
sys.path.append(str(pathlib.Path(__file__).parents[1]))

from extractor import OpenArchive, ArchiveModifiedError

_TARFILE = pathlib.Path(__file__).parent / "random.tar.gz"
_TMPDIR = pathlib.Path(__file__).parent / "_tmp"


@pytest.fixture()
def tmpdir():
    if _TMPDIR.exists():
        shutil.rmtree(_TMPDIR)
    yield _TMPDIR
    shutil.rmtree(_TMPDIR)

    """Catch cases where archive is modified while inside context manager."""


@pytest.mark.xfail(raises=ArchiveModifiedError)
def test_num_files_changes(tmpdir):
    with OpenArchive(_TARFILE, tmpdir) as files:
        f = next(files)
        f.unlink()  # deletes f


@pytest.mark.xfail(raises=ArchiveModifiedError)
def test_size_changes(tmpdir):
    with OpenArchive(_TARFILE, _TMPDIR) as files:
        f = next(files)
        f.unlink()  # deletes f
        g = next(files)
        shutil.copy(g, f)  # copies g (different size) -> f
