"""Offline graph/closure audit. Does not modify the execution ledger."""
import json
from pathlib import Path
import subprocess

tasks = json.loads(Path('tasks.json').read_text())['tasks']
by_id = {t['id']: t for t in tasks}
requirements = {r['id'] for r in json.loads(Path('requirements.json').read_text())['requirements']}
seen, active = set(), set()
def visit(task_id):
    assert task_id not in active, f"dependency cycle: {task_id}"
    if task_id in seen:
        return
    active.add(task_id)
    t = by_id[task_id]
    assert set(t['requirements']) <= requirements
    for dep in t['depends_on']:
        visit(dep)
        if t['status'] == 'completed':
            assert by_id[dep]['status'] == 'completed'
    if t['status'] == 'completed':
        assert not t['verification_is_proposed'], task_id
        assert Path(t['evidence']).is_file(), task_id
        assert t['completion_commit'], task_id
        subprocess.run(['git', 'cat-file', '-e', t['completion_commit'] + '^{commit}'], check=True)
    active.remove(task_id)
    seen.add(task_id)
for task_id in by_id:
    visit(task_id)
print(json.dumps({'acyclic': True, 'tasks': len(tasks), 'completed': [t['id'] for t in tasks if t['status'] == 'completed'], 'evidence_and_commits_exist': True}))
