"""Metrics from runs/预设运行版本 for thesis tables."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY = ROOT / 'runs' / '预设运行版本' / 'summary.json'


def load_evaluation():
    data = json.loads(SUMMARY.read_text(encoding='utf-8'))
    return data['evaluation']


def rankings_ordered():
    ev = load_evaluation()
    order = ['aggressive-breakout', 'balanced-strategist', 'conservative-hedger', 'memory-auditor']
    by_id = {r['agentId']: r for r in ev['rankings']}
    labels = ['第一', '第二', '第三', '第四']
    rows = []
    for i, aid in enumerate(order):
        r = by_id[aid]
        sym = {'gold': 'GC', 'crude_oil': 'CL', 'soybean': 'ZS'}.get(r.get('commodity'), '')
        rows.append({
            'rank': labels[i],
            'role': r['role'],
            'symbol': sym,
            'total': r['totalScore'],
            'train': r['trainingScore'],
            'test': r['testScore'],
            'hit': r['hitRate'],
            'mdd': r['maxDrawdown'],
            'raw': r.get('rawScore', 0),
            'raw_train': r.get('rawTrainingScore', 0),
            'raw_test': r.get('rawTestScore', 0),
        })
    return rows


def action_distribution():
    ev = load_evaluation()
    from collections import Counter
    c = Counter()
    for r in ev['rankings']:
        for t in r.get('trades', []):
            c[t['action']] += 1
    return dict(c)


def aggregate_stats():
    rows = rankings_ordered()
    hits = [r['hit'] for r in rows]
    mdds = [r['mdd'] for r in rows]
    totals = [r['total'] for r in rows]
    return {
        'avg_hit': round(sum(hits) / len(hits), 1),
        'avg_mdd': round(sum(mdds) / len(mdds), 2),
        'alpha_spread': round(max(totals) - min(totals), 2),
        'actions': action_distribution(),
    }


def worst_failures(limit=1):
    ev = load_evaluation()
    out = {}
    for r in ev['rankings']:
        trades = sorted(r.get('trades', []), key=lambda x: x.get('scoreDelta', 0))
        bad = [t for t in trades if t.get('scoreDelta', 0) < 0]
        if not bad:
            continue
        t = bad[0]
        neg_count = len(bad)
        out[r['agentId']] = {
            'role': r['role'],
            'round': t['index'] + 1,
            'date': t['date'],
            'action': t.get('actionLabel', t['action']),
            'symbol': t.get('symbol', ''),
            'delta': round(t['scoreDelta'], 2),
            'neg_rounds': neg_count,
            'total_rounds': len(trades),
        }
    return out


if __name__ == '__main__':
    print(rankings_ordered())
    print(aggregate_stats())
    print(worst_failures())
