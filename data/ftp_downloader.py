import argparse
import ftputil
import logging
import os
import pathlib
from types import SimpleNamespace

import yaml

log = logging.getLogger(__name__)

# TODO goe
# logging.basicConfig(filename="download.log", level=logging.INFO)


class FTPDataDownloader:
    """Class which downloads files over an FTP connection.

    Parameters
    ----------
    host: str
        Address of the remote server containing the data to be downloaded.
    source_dir: str
        Server-side path to the base directory containing the data to be downloaded.
    target_dir: str (optional)
        Client-side path to directory where data will be downloaded. Default: '.'
    exclude_dirs: list[str] (optional)
        List of directories to exclude from the download. Default: []
    preserve_structure: bool (optional)
        Flag indicating whether or not to preserve directory structure during download.
        If False, all files will be downloaded to `target_dir`. Default: False
    """

    def __init__(
        self,
        host: str,
        source_dir: str,
        *,
        target_dir: str = ".",
        exclude_dirs: list[str] = [],
        preserve_structure: bool = False,
    ):

        self._host = host
        self._source_dir = pathlib.Path(source_dir)
        self._target_dir = pathlib.Path(target_dir)
        self._exclude_dirs = exclude_dirs  # [pathlib.Path(d) for d in exclude_dirs]
        self._preserve_structure = preserve_structure

    def __iter__(self):
        return self

    def __next__(self):
        try:
            rel_path_to_source = next(self._iter_files)
        except AttributeError:
            print("A dry run is required before downloading can begin.")
            return
        except StopIteration:
            raise StopIteration("No more files to download.")

        source = self.source_dir / rel_path_to_source

        if self.preserve_structure:
            target = self.target_dir / rel_path_to_source
        else:
            target = self.target_dir / source.name

        if target.exists():
            raise FileExistsError(f"{target} already exists.")

        if not target.parent.exists():
            log.info(f"Creating local directory at: {target.parent}")
            target.parent.mkdir(parents=True)

        log.info(f"Attempting download: {rel_path_to_source} -> {target}")
        with ftputil.FTPHost(
            self.host,
            self.get_user(),
            self.get_password(),
        ) as ftp_host:
            # ftp_host.chdir(self.source_dir)
            # TODO Maybe catch exceptions here, log and continue
            ftp_host.download(source, target)

        return target

    @property
    def host(self) -> str:
        """The server we would like to connect to."""
        return self._host

    @property
    def source_dir(self) -> pathlib.Path:
        """The server-side directory containing data to be downloaded."""
        return self._source_dir

    @property
    def target_dir(self) -> pathlib.Path:
        """The client-side directory containing the downloaded data."""
        return self._target_dir

    @property
    def exclude_dirs(self) -> list[str]:
        """Server-side directories to exclude during download."""
        return self._exclude_dirs

    @property
    def preserve_structure(self) -> bool:
        """Whether directory structure is preserved upon download."""
        return self._preserve_structure

    @property
    def file_list(self) -> list[str]:
        """List containing all files to be downloaded."""
        return self._file_list

    @staticmethod
    def get_user() -> str:
        """Returns the client's username.

        By default, this returns the output of ``os.getenv(FTP_USER)``, where
        ``FTP_USER`` is an environment variable containing the username.

        This may be overridden by a user-defined method.
        """
        return os.getenv("FTP_USER")

    @staticmethod
    def get_password() -> str:
        """Returns the client's password.

        By default, this returns the output of ``os.getenv(FTP_PASS)``, where
        ``FTP_PASS`` is an environment variable containing the username.

        This may be overridden by a user-defined method.
        """
        return os.getenv("FTP_PASS")

    def check_credentials(self):
        """Attempts to construct an FTP connection using the provided credentials."""
        print(f"Attempting to connect to host: {self.host}.", end=".. ")
        with ftputil.FTPHost(self.host, self.get_user(), self.get_password()) as _:
            pass
        print("No exceptions raised!")

    def dry_run(self):
        """Do a dry-run of the download."""
        file_list = []
        total_size = 0

        print("Performing dry run...")
        with ftputil.FTPHost(
            self.host, self.get_user(), self.get_password()
        ) as ftp_host:

            print(f"Moving to directory: {self.source_dir}")
            ftp_host.chdir(self.source_dir)

            for root, _, files in ftp_host.walk(ftp_host.curdir):
                root = pathlib.Path(root)

                if str(root.relative_to(".")) in self.exclude_dirs:
                    print(f"Skipping directory: {root}")
                    continue

                if len(files) == 0:
                    print(f"No files found in directory: {root}")
                    continue

                size = sum([ftp_host.path.getsize(root / file) for file in files])
                print(
                    f"Found {len(files)} files ({int(size/1e6)} MB) in directory: {root}"
                )

                file_list += [f"{root}/{file}" for file in files]
                total_size += size

        print(
            f"Total: {len(file_list)} files to be downloaded ({int(total_size/1e6)} MB)"
        )
        self._file_list = file_list
        self._iter_files = iter(file_list)  # points to same object!


_parser = argparse.ArgumentParser()
_parser.add_argument(
    "-c",
    "--config",
    type=str,
    required=True,
    help="path to yaml configuration file",
)

if __name__ == "__main__":

    args = _parser.parse_args()

    with open(args.config, "r") as file:
        config = SimpleNamespace(**yaml.safe_load(file))

    downloader = FTPDataDownloader(
        config.host, config.source, exclude_dirs=config.exclude
    )

    downloader.check_credentials()
    downloader.dry_run()
    _ = next(downloader)
