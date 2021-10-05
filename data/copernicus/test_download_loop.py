import ftplib
import ftputil
import logging
from pathlib import Path
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO call this from yaml input

class FTPDataDownloader:
    def __init__(
        self,
        host: str,
        source_dir: str,
        *,
        target_dir: str = ".",
        exclude_dirs: list[str] = [],
    ):

        self._host = host
        self._source_dir = source_dir
        self._target_dir = target_dir
        self._exclude_dirs = exclude_dirs

    def __iter__(self):
        return self

    def __next__(self):
        source = next(self._iter_files)
        log.info(f"Attempting download: {source}")
        with ftputil.FTPHost(
            host=self.host, user=self._user, passwd=self._password
        ) as ftp_host:
            ftp_host.download(source, self.target_dir)
        yield

    @property
    def host(self) -> str:
        """The FTP host."""
        return self._host

    @property
    def source_dir(self) -> Path:
        """The server-side directory containing data to be downloaded."""
        return self._source_dir

    @property
    def target_dir(self) -> Path:
        """The client-side directory containing the downloaded data."""
        return self._source_dir

    @property
    def exclude_dirs(self) -> list[Path]:
        """Server-side directories to exclude during download."""
        return self._exclude_dirs

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
        with ftputil.FTPHost(self.host, self.get_user(), self.get_password()) as _:
            pass
        print("No exception raised while attempting to access FTP host.")

    def dry_run(self):
        """Do a dry-run of the download."""
        file_list = []
        total_size = 0

        log.info("Performing dry run...")
        with ftputil.FTPHost(
            self.host, self.get_user(), self.get_password()
        ) as ftp_host:

            log.info(f"Moving to directory: {self.source_dir}")
            ftp_host.chdir(self.source_dir)

            for root, _, files in ftp_host.walk(ftp_host.curdir):

                if any([part in self.exclude_dirs for part in Path(root).parts]):
                    log.info(f"Skipping directory: {root}")
                    continue

                if len(files) == 0:
                    log.info(f"No files found in directory: {root}")
                    continue

                size = sum(
                    [
                        ftp_host.path.getsize(ftp_host.path.join(root, file))
                        for file in files
                    ]
                )
                log.info(
                    f"Found {len(files)} files ({int(size/1e6)} MB) in directory: {root}"
                )

                file_list += [f"{root}/{file}" for file in files]
                total_size += size

        log.info(
            f"Total: {len(file_list)} files to be downloaded ({int(total_size/1e6)} MB)"
        )
        self._file_list = file_list
        self._iter_files = iter(file_list)  # points to same object!


if __name__ == "__main__":

    host = "my.cmems-du.eu"
    source_dir = (
        "Core/INSITU_GLO_TS_REP_OBSERVATIONS_013_001_b/CORIOLIS-GLOBAL-EasyCORA-OBS/"
    )
    exclude_dirs = [
        "arctic",
        "baltic",
        "blacksea",
        "mediterrane",
        "northwestshelf",
        "southwestshelf",
    ]

    downloader = FTPDataDownloader(host, source_dir, exclude_dirs=exclude_dirs)

    downloader.check_credentials()
    downloader.dry_run()
