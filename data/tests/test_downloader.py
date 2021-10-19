import pathlib
import shutil
import sys
from types import SimpleNamespace

import pytest
import yaml

sys.path.append(str(pathlib.Path(__file__).parents[1]))

from ftp_downloader import FTPDataDownloader

_CONFIG = pathlib.Path(__file__).parent / "rebex.yml"
_TARGET_DIR = pathlib.Path(__file__).parent / "_tmp_test_downloader"

assert not _TARGET_DIR.exists()


@pytest.fixture()
def downloader():
    with open(_CONFIG, "r") as file:
        config = SimpleNamespace(**yaml.safe_load(file))
    downloader = FTPDataDownloader(
        config.host,
        config.source,
        exclude_dirs=config.exclude,
        target_dir=str(_TARGET_DIR),
    )
    downloader.get_user = lambda: "demo"
    downloader.get_password = lambda: "password"
    yield downloader
    if _TARGET_DIR.exists():
        # TODO maybe a module or session-level teardown?
        shutil.rmtree(_TARGET_DIR)


@pytest.fixture()
def primed_downloader(downloader):
    downloader.check_credentials()
    downloader.dry_run()
    assert downloader.file_list == [
        "readme.txt"
    ], f"Test server {downloader.host} have made changes. Exiting since there is no way of knowing what will be downloaded."
    return downloader


@pytest.mark.xfail(raises=AttributeError)
def test_dry_run_requirement(downloader):
    _ = next(downloader)


@pytest.mark.xfail(raises=FileExistsError)
def test_existing_file(primed_downloader):
    target = primed_downloader.target_dir / "readme.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open(mode="w") as file:
        file.write("dog")
    _ = next(primed_downloader)


def test_file_downloads(primed_downloader):
    # Download readme.txt
    file = next(primed_downloader)
    assert pathlib.Path(file).is_file()


@pytest.mark.xfail(raises=StopIteration)
def test_no_more_files(primed_downloader):
    # Modify protected attr so we don't have to go through the download again :)
    try:
        _ = next(primed_downloader._iter_files)
    except StopIteration:
        assert False, "Something has gone really wrong. Should not fail here!"
    _ = next(primed_downloader)  # should fail here!
