#!/usr/bin/env python3
"""Scan Cursor agent activity and transcripts for a given day, generate a
bilingual (EN/CN) summary, and send it to flomo."""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from flomo import send_memo

ACTIVITY_LOG = os.path.expanduser("~/.cursor/agent-activity.log")
PROJECTS_DIR = os.path.expanduser("~/.cursor/projects")


def parse_activity_log(target_date: date) -> list[dict]:
    """Parse the YAML-block activity log and return entries matching target_date."""
    if not os.path.exists(ACTIVITY_LOG):
        return []

    entries = []
    with open(ACTIVITY_LOG) as f:
        content = f.read()

    blocks = re.split(r"\n---\n", content)
    target_str = target_date.isoformat()

    for block in blocks:
        block = block.strip()
        if not block or block.startswith("#"):
            continue

        entry = {}
        for line in block.splitlines():
            line = line.strip().rstrip("---").strip()
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                if key in ("timestamp", "project", "event", "summary", "files", "branch"):
                    entry[key] = val

        ts = entry.get("timestamp", "")
        if ts.startswith("$("):
            continue
        if not ts.startswith(target_str):
            continue
        if entry.get("summary"):
            entries.append(entry)

    return entries


def extract_session_topic(jsonl_path: str) -> str | None:
    """Extract the first meaningful user query from a transcript as the session topic."""
    try:
        with open(jsonl_path) as f:
            for line in f:
                obj = json.loads(line)
                if obj.get("role") != "user":
                    continue
                for c in obj.get("message", {}).get("content", []):
                    if c.get("type") != "text":
                        continue
                    m = re.search(r"<user_query>\s*(.*?)\s*</user_query>", c["text"], re.DOTALL)
                    if m:
                        query = m.group(1).strip()
                        first_line = query.split("\n")[0].strip()
                        if len(first_line) < 3:
                            continue
                        if len(first_line) > 120:
                            first_line = first_line[:120] + "..."
                        return first_line
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _get_username() -> str:
    """Detect the current username from the home directory."""
    return os.path.basename(os.path.expanduser("~"))


def project_name_from_path(dirpath: str) -> str:
    """Extract a readable project name from the Cursor projects directory path.
    Strips the Users-<username>- prefix and common org/workspace prefixes."""
    basename = os.path.basename(dirpath)
    username = _get_username()
    name = re.sub(rf"^Users-{re.escape(username)}-", "", basename)
    name = re.sub(
        r"^(RobloxProjects-LuobuRepos-|RobloxProjects-|"
        r"luobustaging-repos-|luobutest-repos-|"
        r"roblox-ghc-|OpenSourceProjects-|"
        r"config-[^-]+-[^-]+-cursor-workspaces-|"
        r"Library-Application-Support-Cursor-Workspaces-)",
        "", name
    )
    name = re.sub(r"-?\d{10,}", "", name)
    name = re.sub(r"-?\d{4}-\d{2}-\d{2}(-\d{2}-\d{2})?", "", name)
    name = re.sub(r"-code-workspace$", "", name)
    name = name.strip("-_ ")
    if not name:
        name = basename
    return name


def scan_transcripts(target_date: date) -> dict[str, list[str]]:
    """Scan all project transcript dirs for JSONL files modified on target_date.
    Returns {project_name: [session_topic1, session_topic2, ...]}."""
    result = defaultdict(list)

    username = _get_username()
    pattern = os.path.join(PROJECTS_DIR, f"Users-{username}-*", "agent-transcripts")
    for transcript_dir in glob.glob(pattern):
        project_dir = os.path.dirname(transcript_dir)
        project = project_name_from_path(project_dir)

        for root, dirs, files in os.walk(transcript_dir):
            for fname in files:
                if not fname.endswith(".jsonl"):
                    continue
                fpath = os.path.join(root, fname)
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).date()
                if mtime != target_date:
                    continue
                topic = extract_session_topic(fpath)
                if topic:
                    result[project].append(topic)

    return dict(result)


MAX_SESSIONS = 15


def build_summary(target_date: date, log_entries: list[dict], transcript_data: dict[str, list[str]]) -> str:
    """Build a bilingual flomo memo from activity log entries and transcript data."""
    date_str = target_date.isoformat()
    lines = [
        f"#coding/daily #daily/{date_str}",
        "",
        f"Daily Work Summary / 每日工作总结",
        date_str,
        "",
    ]

    all_projects = set()
    project_items = defaultdict(list)

    for entry in log_entries:
        proj = entry.get("project", "unknown")
        all_projects.add(proj)
        summary = entry["summary"]
        event = entry.get("event", "")
        prefix = {"session_start": "start", "task_complete": "done", "session_end": "end"}.get(event, "")
        tag = f"[{prefix}] " if prefix else ""
        project_items[proj].append(f"{tag}{summary}")

    for proj, topics in transcript_data.items():
        all_projects.add(proj)
        existing = " ".join(project_items.get(proj, [])).lower()
        for topic in topics:
            if topic[:30].lower() not in existing:
                project_items[proj].append(topic)

    if not all_projects:
        return f"#coding/daily #daily/{date_str}\n\nNo Cursor activity recorded today / 今日无 Cursor 活动记录\n{date_str}"

    lines.append(f"Projects / 涉及项目: {len(all_projects)}")
    for proj in sorted(all_projects):
        items = project_items.get(proj, [])
        count_str = f" ({len(items)} sessions)" if len(items) > 1 else ""
        lines.append(f"- {proj}{count_str}")
    lines.append("")

    lines.append("Key sessions / 主要会话:")
    idx = 1
    for proj in sorted(all_projects):
        for item in project_items.get(proj, []):
            if idx > MAX_SESSIONS:
                break
            desc = item
            if len(desc) > 100:
                desc = desc[:100] + "..."
            lines.append(f"{idx}. [{proj}] {desc}")
            idx += 1
        if idx > MAX_SESSIONS:
            remaining = sum(len(v) for v in project_items.values()) - MAX_SESSIONS
            if remaining > 0:
                lines.append(f"   ...and {remaining} more sessions")
            break
    lines.append("")

    all_files = set()
    for entry in log_entries:
        files_str = entry.get("files", "none")
        if files_str and files_str != "none":
            for f in files_str.split(","):
                f = f.strip()
                if f:
                    all_files.add(f)

    total_sessions = sum(len(v) for v in project_items.values())
    lines.append(f"Stats / 统计: {total_sessions} sessions, {len(all_projects)} projects")
    if all_files:
        lines.append(f"Files changed / 修改文件: {len(all_files)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate daily Cursor work summary and send to flomo")
    parser.add_argument("--date", "-d", help="Date to summarize (YYYY-MM-DD, defaults to today)")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without sending to flomo")
    args = parser.parse_args()

    if args.date:
        target_date = date.fromisoformat(args.date)
    else:
        target_date = date.today()

    print(f"Scanning activity for {target_date}...")

    log_entries = parse_activity_log(target_date)
    print(f"  Activity log: {len(log_entries)} entries")

    transcript_data = scan_transcripts(target_date)
    total_queries = sum(len(v) for v in transcript_data.values())
    print(f"  Transcripts: {total_queries} queries across {len(transcript_data)} projects")

    summary = build_summary(target_date, log_entries, transcript_data)

    if args.dry_run:
        print("\n--- Summary (dry run) ---")
        print(summary)
        print("--- End ---")
    else:
        print("\nSending to flomo...")
        send_memo(summary)
        print("Done!")


if __name__ == "__main__":
    main()
