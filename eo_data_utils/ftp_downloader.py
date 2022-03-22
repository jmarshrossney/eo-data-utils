from __future__ import annotations

import logging
import os
import pathlib
from typing import Callable

import ftputil
import jsonargparse

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

Path: TypeAlias = pathlib.Path


class FTPDataDownloader:
    """Class which downloads files over an FTP connection.

    Parameters
    ----------
    host: str
        Address of the remote server containing the data to be downloaded.
    source: str
        Server-side path to the base directory containing the data to be downloaded.
    target: str (optional)
        Client-side path to directory where data will be downloaded. Default: '.'
    exclude: list[str] (optional)
        List of directories to exclude from the download. Default: []
    """

    def __init__(
        self,
        host: str,
        source: str | Path,
        *,
        target: str | Path = ".",
        exclude: list[str] = [],
    ):

        self._host = host
        self._source = pathlib.Path(source)
        self._target = pathlib.Path(target)
        self._exclude = exclude  # [pathlib.Path(d) for d in exclude]
        self._filters = []

    def __iter__(self):
        return self

    def __next__(self):
        try:
            rel_path_to_source = next(self._iter_files)
        except AttributeError:
            raise AttributeError("A dry run is required before downloading can begin.")
        except StopIteration:
            raise StopIteration("No more files to download.")

        source = self.source / rel_path_to_source
        target = self.target / rel_path_to_source

        if target.exists():
            raise FileExistsError(f"{target} already exists.")

        if not target.parent.exists():
            log.info(f"Creating local directory at: {target.parent}")
            target.parent.mkdir(parents=True)

        log.info(f"Attempting download: {rel_path_to_source} -> {target}")
        with ftputil.FTPHost(
            self.host, self.get_user(), self.get_password(),
        ) as ftp_host:
            # ftp_host.chdir(self.source)
            # TODO Maybe catch exceptions here, log and continue
            ftp_host.download(source, target)

        return target

    @property
    def host(self) -> str:
        """The server we would like to connect to."""
        return self._host

    @property
    def source(self) -> pathlib.Path:
        """The server-side directory containing data to be downloaded."""
        return self._source

    @property
    def target(self) -> pathlib.Path:
        """The client-side directory containing the downloaded data."""
        return self._target

    @property
    def exclude(self) -> list[str]:
        """Server-side directories to exclude during download."""
        return self._exclude

    @property
    def file_list(self) -> list[str]:
        """List containing all files to be downloaded."""
        return self._file_list

    @property
    def filters(self) -> list[Callable[list, list]]:
        """Functions for excluding files."""
        return self._filters

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

    def _is_nonempty_string(self, s) -> bool:
        """Return True if input is a non-empty string of length > 1."""
        return type(s) is str and len(s) > 0

    def _build_file_list(self):
        """Accesses server and compiles list of files to be downloaded."""
        file_list = []
        total_size = 0

        log.info(f"Connecting to host: {self.host}")
        with ftputil.FTPHost(
            self.host, self.get_user(), self.get_password()
        ) as ftp_host:

            log.info(f"Moving to directory: {self.source}")
            ftp_host.chdir(self.source)

            for root, _, files in ftp_host.walk(ftp_host.curdir):
                root = pathlib.Path(root)

                relative_root = root.relative_to(".")
                if str(relative_root) in self.exclude or any(
                    [str(p) in self.exclude for p in relative_root.parents]
                ):
                    log.info(f"Skipping directory: {root}")
                    continue

                if len(files) == 0:
                    log.info(f"No files found in directory: {root}")
                    continue

                # Apply custom filters to files
                local_file_list = [root / file for file in files]
                for filter_ in self.filters:
                    local_file_list = filter_(local_file_list)

                size = sum([ftp_host.path.getsize(file) for file in local_file_list])
                log.info(
                    f"Added {len(local_file_list)} files ({int(size/1e6)} MB) from directory: {root}"
                )

                file_list += [str(file) for file in local_file_list]
                total_size += size

        log.info(
            f"Total: {len(file_list)} files to be downloaded ({int(total_size/1e6)} MB)"
        )
        self._file_list = file_list
        self._iter_files = iter(file_list)  # points to same object!

    def check_credentials(self):
        """Attempts to construct an FTP connection using the provided credentials."""
        if not self._is_nonempty_string(
            self.get_user()
        ) or not self._is_nonempty_string(self.get_password()):
            log.warning(
                "Failed to acquire valid (non-empty string) user and/or password."
            )
        log.info(f"Attempting to connect to host: {self.host}")
        with ftputil.FTPHost(self.host, self.get_user(), self.get_password()) as _:
            pass
        log.info("No exceptions raised!")

    def register_filter(self, filter_func):
        # TODO run some checks
        self._filters.append(filter_func)

    def dry_run(self):
        """Do a dry-run of the download."""
        log.info("Performing dry run...")
        self._build_file_list()


_parser = jsonargparse.ArgumentParser()
_parser.add_argument("--config", action=jsonargparse.ActionConfigFile)
_parser.add_argument("--host")
_parser.add_argument("--source")
_parser.add_argument("--target")
_parser.add_argument("--exclude")

if __name__ == "__main__":
    """Do a dry-run."""
    config = _parser.parse_args()
    print(config)
    downloader = FTPDataDownloader(
        config.host, config.source, target=config.target, exclude=config.exclude
    )
    downloader.check_credentials()
    downloader.dry_run()
