#!/usr/bin/env python3
"""Send a memo to flomo via the official API."""

import argparse
import json
import os
import ssl
import sys
import urllib.request
import urllib.error


def get_api_url():
    url = os.environ.get("FLOMO_API_URL")
    if not url:
        config_path = os.path.expanduser("~/.claude/flomo-config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = json.load(f)
            url = cfg.get("api_url")
    if not url:
        print("Error: FLOMO_API_URL not set. Set it in ~/.zshrc or ~/.claude/flomo-config.json", file=sys.stderr)
        sys.exit(1)
    return url


def send_memo(content):
    url = get_api_url()
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 0:
                print(f"Memo sent successfully.")
            else:
                print(f"flomo API error: {result.get('message', 'unknown error')}", file=sys.stderr)
                sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Send a memo to flomo")
    parser.add_argument("--content", "-c", required=True, help="Memo content (including #tags)")
    args = parser.parse_args()
    send_memo(args.content)


if __name__ == "__main__":
    main()
