def main() -> int:
    try:
        from vl_scanner.ui.app import run_app
    except Exception:
        print("UI scaffold not available.")
        return 0

    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())