import sys


def app():
    import hermes._rust as _rust

    raise SystemExit(_rust.cli.main(list(sys.argv[1:])))


if __name__ == "__main__":
    app()
