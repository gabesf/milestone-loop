#!/usr/bin/env python3
"""Measure Claude Code sessions of a milestone-loop project.

Reads the session transcripts (orchestrator and subagents) and reports, per
session: the orchestrator's active time and waits, and for every subagent its
role, active minutes, model calls, context size, capture time and images.

- A step is one model call (transcripts write one line per content block; lines
  are de-duplicated by message id).
- Active time = wall time minus waits longer than 5 minutes: on the user, on
  subagents, on the coordinator's next message (an agent resumed for fixes), and
  on a sleeping machine (cut-off responses).
- Context of a call = input + cache read + cache creation tokens.

Usage:
  measure-sessions.py <project dir> [--session <id prefix>] [--since YYYY-MM-DD]
  measure-sessions.py <project dir> --latest --jsonl --milestone M-07
      prints one JSON line for the newest session (what /close-milestone appends
      to docs/metrics.jsonl).
Transcripts live in $CLAUDE_CONFIG_DIR/projects (default ~/.claude/projects);
--root overrides it.
"""
import argparse
import glob
import json
import os
import re
from collections import defaultdict
from datetime import datetime

IDLE = 300  # seconds without events before a gap counts as a wait

CAPTURE = re.compile(r'captur|screenshot|preview|chrome|Chrome|cdp|playwright|puppeteer|manage_editor|\.mjs')
TEST = re.compile(r'pnpm test|npm test|vitest|jest|pytest|run_tests|EditMode|PlayMode|dotnet test')


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return ' '.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text')
    return ''


def role_of(meta):
    kind = meta.get('agentType', '')
    d = meta.get('description', '')
    if re.search(r'fix|correç|finish|apply', d, re.I) and 'adversarial' not in kind:
        return 'fix'
    if 'adversarial' in kind or re.search(r'gate|review|revis|lens|lente', d, re.I):
        return 'reviewer'
    if re.search(r'^(Implement|Implementar)', d):
        return 'implementer'
    if re.search(r'tier|tester|captur|spike', d, re.I):
        return 'test/capture'
    if kind in ('Explore', 'Plan') or re.search(r'^(Map|Survey|Inventory|Find)', d):
        return 'mapping'
    return 'other'


def analyze(path, main):
    events = []
    with open(path) as f:
        for line in f:
            try:
                x = json.loads(line)
            except ValueError:
                continue
            if 'timestamp' in x:
                events.append(x)
    if not events:
        return None
    events.sort(key=lambda x: x['timestamp'])
    waits = defaultdict(float)
    for a, b in zip(events, events[1:]):
        gap = ts(b['timestamp']) - ts(a['timestamp'])
        if gap <= IDLE:
            continue
        tb = text_of((b.get('message') or {}).get('content') or b.get('content'))
        pending = [blk['name'] for blk in ((a.get('message') or {}).get('content') or [])
                   if a.get('type') == 'assistant' and isinstance(blk, dict) and blk.get('type') == 'tool_use']
        if 'cut off mid-stream' in tb or 'went to sleep' in tb:
            waits['sleep'] += gap
        elif 'coordinator sent a message' in tb:
            waits['coordinator'] += gap
        elif 'AskUserQuestion' in pending:
            waits['user'] += gap
        elif main and ('Agent' in pending or 'Task' in pending
                       or tb.startswith(('<task-notification', '<agent-message'))):
            waits['subagents'] += gap
        elif pending:
            continue  # a long tool call is work
        elif main and b.get('type') in ('user', 'attachment') and not tb.startswith('<'):
            waits['user'] += gap
        else:
            waits['other'] += gap
    calls = {}
    uses = {}
    tools = defaultdict(float)
    images = 0
    questions = 0
    model = ''
    for x in events:
        m = x.get('message') or {}
        c = m.get('content')
        if x.get('type') == 'assistant':
            u = m.get('usage') or {}
            model = model or m.get('model', '')
            if m.get('id') not in calls:
                calls[m.get('id')] = (u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0)
                                      + u.get('cache_creation_input_tokens', 0))
            for blk in c if isinstance(c, list) else []:
                if blk.get('type') == 'tool_use':
                    questions += blk['name'] == 'AskUserQuestion'
                    cmd = json.dumps(blk.get('input', {}))
                    kind = 'capture' if CAPTURE.search(cmd) else 'test' if TEST.search(cmd) else 'other'
                    uses[blk['id']] = (ts(x['timestamp']), kind)
        for blk in c if isinstance(c, list) else []:
            if isinstance(blk, dict) and blk.get('type') == 'tool_result' and blk.get('tool_use_id') in uses:
                t0, kind = uses.pop(blk['tool_use_id'])
                tools[kind] += ts(x['timestamp']) - t0
                if isinstance(blk.get('content'), list):
                    images += sum(1 for y in blk['content'] if y.get('type') == 'image')
    if not calls:
        return None
    ctx = list(calls.values())
    wall = ts(events[-1]['timestamp']) - ts(events[0]['timestamp'])
    return dict(start=ts(events[0]['timestamp']), wall=wall, active=wall - sum(waits.values()),
                waits=dict(waits), steps=len(ctx), ctx_avg=sum(ctx) / len(ctx), ctx_max=max(ctx),
                tools=dict(tools), images=images, questions=questions, model=model.replace('claude-', ''))


def session(base, sid):
    main = analyze(f'{base}/{sid}.jsonl', True)
    if not main:
        return None, []
    subs = []
    for sf in glob.glob(f'{base}/{sid}/subagents/*.jsonl'):
        mf = sf[:-6] + '.meta.json'
        meta = json.load(open(mf)) if os.path.exists(mf) else {}
        s = analyze(sf, False)
        if s:
            s.update(role=role_of(meta), desc=meta.get('description', ''))
            subs.append(s)
    return main, sorted(subs, key=lambda s: s['start'])


def jsonl_line(sid, milestone, main, subs):
    mins = lambda s: round(s / 60, 1)
    by_role = defaultdict(list)
    for s in subs:
        by_role[s['role']].append(s)
    impl = by_role['implementer'] + by_role['fix']
    return json.dumps(dict(
        milestone=milestone, session=sid[:8], date=datetime.fromtimestamp(main['start']).strftime('%Y-%m-%d'),
        model=main['model'], wall_min=mins(main['wall']), orchestrator_active_min=mins(main['active']),
        wait_user_min=mins(main['waits'].get('user', 0)), wait_subagents_min=mins(main['waits'].get('subagents', 0)),
        sleep_min=mins(sum(s['waits'].get('sleep', 0) for s in subs) + main['waits'].get('sleep', 0)),
        active_min_by_role={r: mins(sum(s['active'] for s in v)) for r, v in sorted(by_role.items())},
        implementer_steps=sum(s['steps'] for s in impl), implementer_runs=len(impl),
        reviewer_runs=len(by_role['reviewer']), max_context_k=round(max([main['ctx_max']] + [s['ctx_max'] for s in subs]) / 1000),
        capture_min=mins(sum(s['tools'].get('capture', 0) for s in subs)), images=sum(s['images'] for s in subs),
        user_questions=main['questions'],
    ), ensure_ascii=False)


def report(sid, main, subs):
    m = lambda s: s / 60
    w = main['waits']
    print(f"\n## {sid[:8]}  {datetime.fromtimestamp(main['start']):%Y-%m-%d %H:%M}  {main['model']}  "
          f"wall {m(main['wall']):.0f} min | orchestrator active {m(main['active']):.0f} min, {main['steps']} calls, "
          f"ctx avg {main['ctx_avg']/1e3:.0f}k (max {main['ctx_max']/1e3:.0f}k) | waiting: user {m(w.get('user', 0)):.0f}, "
          f"subagents {m(w.get('subagents', 0)):.0f}, other {m(w.get('other', 0)):.0f} min | questions {main['questions']}")
    if not subs:
        return
    print(f"   {'role':13s} {'active':>6s} {'wait':>5s} {'calls':>5s} {'ctx avg':>7s} {'ctx max':>7s} "
          f"{'capture':>7s} {'test':>4s} {'imgs':>4s}  description")
    for s in subs:
        print(f"   {s['role']:13s} {m(s['active']):6.0f} {m(sum(s['waits'].values())):5.0f} {s['steps']:5d} "
              f"{s['ctx_avg']/1e3:6.0f}k {s['ctx_max']/1e3:6.0f}k {m(s['tools'].get('capture', 0)):7.0f} "
              f"{m(s['tools'].get('test', 0)):4.0f} {s['images']:4d}  {s['desc'][:48]}")
    sleep = sum(s['waits'].get('sleep', 0) for s in subs)
    if sleep:
        print(f"   machine asleep (cut-off responses), summed over subagents: {m(sleep):.0f} min")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--root', default=os.path.join(os.environ.get('CLAUDE_CONFIG_DIR', '~/.claude'), 'projects'))
    ap.add_argument('--session')
    ap.add_argument('--since')
    ap.add_argument('--latest', action='store_true')
    ap.add_argument('--jsonl', action='store_true')
    ap.add_argument('--milestone', default='')
    a = ap.parse_args()
    base = os.path.join(os.path.expanduser(a.root), re.sub(r'[^A-Za-z0-9]', '-', os.path.abspath(a.project)))
    files = sorted(glob.glob(base + '/*.jsonl'), key=os.path.getmtime)
    if not files:
        raise SystemExit(f'no transcripts under {base}')
    if a.latest:
        files = files[-1:]
    since = datetime.fromisoformat(a.since).timestamp() if a.since else 0
    for f in files:
        sid = os.path.basename(f)[:-6]
        if a.session and not sid.startswith(a.session):
            continue
        main_s, subs = session(base, sid)
        if not main_s or main_s['start'] < since or (not subs and main_s['steps'] < 20 and not a.latest):
            continue
        if a.jsonl:
            print(jsonl_line(sid, a.milestone, main_s, subs))
        else:
            report(sid, main_s, subs)


if __name__ == '__main__':
    main()
