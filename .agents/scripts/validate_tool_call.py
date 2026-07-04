"""
Mitra Agent Hook — PreToolUse validator.
Intercepts all run_command calls before execution.
Blocks destructive commands and data exfiltration.
"""
import sys
import json
import re


def main():
    """Validates tool calls before agent executes them."""
    try:
        context = json.load(sys.stdin)
        command = context.get("tool_args", {}).get("CommandLine", "")

        blocked = [
            "rm -rf /",
            "mkfs",
            "DROP TABLE",
            "DELETE FROM",
        ]

        for b in blocked:
            if b.lower() in command.lower():
                print(f"BLOCKED: {b}", file=sys.stderr)
                sys.exit(1)

        if ".env" in command and "cat" in command:
            print("BLOCKED: .env access", file=sys.stderr)
            sys.exit(1)

        print("APPROVED")
        sys.exit(0)

    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
