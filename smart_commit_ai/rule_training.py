"""Command-line entry point for training local learned rules."""

from __future__ import annotations

from .learned_rules import DEFAULT_RULES_PATH, train_default_rules


def main() -> None:
    path = train_default_rules(DEFAULT_RULES_PATH)
    print(f"Wrote learned rules to {path}")


if __name__ == "__main__":
    main()
