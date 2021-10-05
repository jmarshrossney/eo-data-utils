import pathlib
import shutil


class OpenArchive:
    tol = 1

    def __init__(self, archive: pathlib.Path, tmpdir: str = "tmp"):
        self._archive = archive
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

        assert (
            num_at_exit == self._num_at_enter
        ), f"Number of files in temporary directory, {self._tmpdir} has changed since archive was extracted."
        assert (
            abs(size_at_exit - self._size_at_enter) < self.tol
        ), f"Size of temporary directory, {self._tmpdir}, has changed since archive was extracted."
        # TODO log these as errors for investigation

        shutil.rmtree(self._tmpdir)


# TODO put into test module
def test_num_files_changes():
    p = pathlib.Path("CORA-5.2-global-1950.tgz")
    try:
        with OpenArchive(p) as files:
            f = next(files)
            f.unlink()
    except AssertionError as e:
        print(e)


def test_size_changes():
    p = pathlib.Path("CORA-5.2-global-1950.tgz")
    try:
        with OpenArchive(p) as files:
            f = next(files)
            f.unlink()
            g = next(files)
            shutil.copy(g, f)
    except AssertionError as e:
        print(e)
