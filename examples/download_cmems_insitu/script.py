import jsonargparse

from eo_data_utils.ftp_downloader import FTPDataDownloader

_parser = jsonargparse.ArgumentParser(prog="downloader")
_parser.add_argument("--config", action=jsonargparse.ActionConfigFile)
_parser.add_argument("--host", required=True)
_parser.add_argument("--source", required=True)
_parser.add_argument("--target", required=True)
_parser.add_argument("--exclude", nargs="*", default=[])


def parse_args(cmd_args=None):
    args = _parser.parse_args(cmd_args)
    delattr(args, "config")
    return args


def main(host: str, source: str, target: str, exclude: list[str] = []):
    downloader = FTPDataDownloader(
        host=host, source=source, target=target, exclude=exclude
    )

    downloader.check_credentials()
    downloader.dry_run()
    for _ in downloader.file_list:
        next(downloader)


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
