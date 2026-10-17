"""CLI entry point for cron-explain."""
import sys
from cron_explain import explain


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cron-explain <cron-expression>")
        print("Example: cron-explain '0 9 * * 1-5'")
        print("         cron-explain '*/5 * * * *'")
        sys.exit(0 if len(sys.argv) > 1 else 1)

    expr = sys.argv[1]
    try:
        print(explain(expr))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
