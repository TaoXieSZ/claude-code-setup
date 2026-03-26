---
name: flomo
description: >
  Send memos and daily work summaries to flomo note-taking app. Use this skill
  whenever the user mentions flomo, wants to capture a note to their phone,
  send a coding memo, record a TODO or blocker, summarize today's work,
  generate a daily report, or review what they accomplished.
  Triggers on: "flomo", "send to flomo", "记到flomo", "发flomo", "memo to phone",
  "note to flomo", "summarize my work", "daily summary", "今日工作总结",
  "what did I do today", "每日总结", "work recap", "end of day summary".
  Also use when the user says "going home", "wrapping up", "下班了" and wants
  a quick recap sent to their phone.
allowed-tools: Bash
---

# Flomo Integration

Send memos and automated daily work summaries to [flomo](https://flomoapp.com) via the API. Memos sync instantly to the user's phone.

## Setup

The flomo API URL must be configured in one of two ways:

1. Environment variable: `export FLOMO_API_URL="https://flomoapp.com/iwh/xxx/yyy"`
2. Config file: `~/.claude/flomo-config.json` with `{"api_url": "https://flomoapp.com/iwh/xxx/yyy"}`

The user can find their API URL in flomo settings under the "API" section.

## Capability 1: Send a Memo

For quick notes, TODOs, blockers, or session summaries — send a single memo:

```bash
python3 ~/.cursor/skills/flomo/scripts/flomo.py --content "YOUR MEMO CONTENT HERE"
```

Always include flomo tags (prefixed with `#`) for organization.

### Tag Conventions

| Type | Tags | When to use |
|------|------|-------------|
| Session summary | `#coding/session #project/PROJECT_NAME` | End of coding session |
| Daily summary | `#coding/daily #daily/YYYY-MM-DD` | End of day recap |
| TODO | `#coding/todo` | Tasks to do later |
| Blocker | `#coding/blocker` | Issues blocking progress |
| General note | `#coding/note` | Any other coding note |

### Formatting Templates

**Session Summary** — gather context from the current conversation and format:

```
#coding/session #project/PROJECT_NAME
YYYY-MM-DD Session Summary

- What was accomplished (bullet points)
- Key decisions made
- Next steps or open questions
```

**TODO / Blocker:**

```
#coding/todo
Description of the task

Context: why this matters
```

**General Note:**

```
#coding/note #project/PROJECT_NAME
The note content here
```

## Capability 2: Daily Work Summary

Scan all Cursor agent transcripts and activity logs for a given day, generate a bilingual (English + Chinese) summary, and send it to flomo. This captures work across all projects the user touched.

```bash
# Summarize today and send to flomo
python3 ~/.cursor/skills/flomo/scripts/daily_summary.py

# Preview without sending
python3 ~/.cursor/skills/flomo/scripts/daily_summary.py --dry-run

# Summarize a specific date
python3 ~/.cursor/skills/flomo/scripts/daily_summary.py --date 2026-03-25
```

### Data Sources

The script merges two sources for a complete picture:

1. **Agent transcripts** (`~/.cursor/projects/Users-<user>-*/agent-transcripts/*/*.jsonl`) — extracts the first user query from each session as the topic
2. **Agent activity log** (`~/.cursor/agent-activity.log`) — structured YAML entries with project, event type, and summary

### Output Format

The summary is sent as a flomo memo tagged `#coding/daily #daily/YYYY-MM-DD` with:
- Project list with session counts
- Top 15 session descriptions grouped by project
- Stats (total sessions, projects, files changed)

### Scheduling (Optional)

To run automatically every day at 6 PM, install the included macOS LaunchAgent:

```bash
sudo cp ~/.cursor/skills/flomo/com.txie.cursor-daily-flomo.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.txie.cursor-daily-flomo.plist
```

Logs go to `~/.cursor/logs/daily-flomo.log`.

## Guidelines

- Keep memos concise — flomo is for quick capture, not long documents
- Always include at least one tag for organization
- Use the project name tag when the note is project-specific
- Support both English and Chinese content
- If the user says "记到flomo" or similar Chinese phrases, treat it the same as "send to flomo"
- When sending session summaries, summarize from the current conversation context — don't ask the user to repeat what was done
- When the user asks for a daily summary or work recap, use `daily_summary.py` rather than manually composing one
