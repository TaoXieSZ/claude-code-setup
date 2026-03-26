---
name: flomo
description: >
  Send memos to flomo note-taking app for syncing coding notes to phone.
  Use for session summaries, TODOs, blockers, and quick notes.
  Triggers: "flomo", "send to flomo", "记到flomo", "发flomo",
  "memo to phone", "note to flomo"
allowed-tools: Bash
---

# Flomo Memo Sender

Send memos to flomo via the official API. Memos sync instantly to the user's phone.

## How to Send

```bash
python3 ~/.agents/skills/flomo/scripts/flomo.py --content "YOUR MEMO CONTENT HERE"
```

The content should include flomo tags (prefixed with #) for organization.

## Tag Conventions

Use these tags to categorize memos:

| Type | Tags | When to use |
|------|------|-------------|
| Session summary | `#coding/session #project/PROJECT_NAME` | End of coding session |
| TODO | `#coding/todo` | Tasks to do later |
| Blocker | `#coding/blocker` | Issues blocking progress |
| General note | `#coding/note` | Any other coding note |

## Formatting Templates

### Session Summary
When the user asks to send a session summary, gather context from the current conversation (what was done, key decisions, next steps) and format as:

```
#coding/session #project/PROJECT_NAME
YYYY-MM-DD Session Summary

- What was accomplished (bullet points)
- Key decisions made
- Next steps or open questions
```

### TODO / Blocker
```
#coding/todo
Description of the task

Context: why this matters
```

### General Note
```
#coding/note #project/PROJECT_NAME
The note content here
```

## Guidelines

- Keep memos concise — flomo is for quick capture, not long documents
- Always include at least one tag for organization
- Use the project name tag when the note is project-specific
- Support both English and Chinese content
- If the user says "记到flomo" or similar, treat it the same as "send to flomo"
- When sending session summaries, summarize from the current conversation context — don't ask the user to repeat what was done
