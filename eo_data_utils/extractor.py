import pathlib
import shutil
from typing import Union


class ArchiveModifiedError(Exception):
    pass


class OpenArchive:
    """Context manager for working with compressed archives.

    Upon entry, the archive is extracted into a temporary directory, and an
    iterator of pathlib.Path objects pointing to the extracted files is returned.
    Upon exit, the temporary directory is deleted.

    Parameters
    ----------
    archive: Union[str, pathlib.Path]
        Path to archive.
    tmpdir: Union[str, pathlib.Path] (optional)
        Path to temporary directory into which archive is to be extracted.
        Must not already exist!

    Raises
    ------
    FileExistsError
        Upon entry, if `tmpdir` already exists.
    ArchiveModifiedError
        If the contents of `tmpdir` have been modified while inside the context
        manager. This is a fail-safe in case something useful has been saved into
        the temporary directory.
    """

    tol = 1

    def __init__(
        self,
        archive: Union[str, pathlib.Path],
        tmpdir: Union[str, pathlib.Path] = "_tmp",
    ):
        self._archive = pathlib.Path(archive)
        self._tmpdir = pathlib.Path(tmpdir)

    def __enter__(self):
        if self._tmpdir.exists():
            raise FileExistsError(
                f"Tried to create temporary directory, {self._tmpdir}, but it already exists"
            )

        shutil.unpack_archive(self._archive, extract_dir=self._tmpdir)

        files = [f for f in self._tmpdir.glob("**/*") if f.is_file()]
        self._num_at_enter = len(files)
        self._size_at_enter = sum([f.stat().st_size for f in files])

        return iter(files)

    def __exit__(self, type, value, traceback):
        files = [f for f in self._tmpdir.glob("**/*") if f.is_file()]
        num_at_exit = len(files)
        size_at_exit = sum([f.stat().st_size for f in files])

        # TODO log these as errors for investigation
        if not num_at_exit == self._num_at_enter:
            raise ArchiveModifiedError(
                f"Number of files in temporary directory, {self._tmpdir} has changed since archive was extracted."
            )
        if not abs(size_at_exit - self._size_at_enter) < self.tol:
            raise ArchiveModifiedError(
                f"Size of temporary directory, {self._tmpdir}, has changed since archive was extracted."
            )

        shutil.rmtree(self._tmpdir)
