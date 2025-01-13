"""Print the installed diurnix version without network access."""

from diurnix import __version__


def main() -> None:
    print(f"diurnix {__version__}: offline runtime ready")


if __name__ == "__main__":
    main()
