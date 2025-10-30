# Sprint 5 – Add/Commit/Push Helper

This repo contains `add-commit-push.py` which automates:
- `git add -A`
- `git commit -m "<message>"`
- `git push` (auto-sets upstream on first push)

## Usage
```bash
python add-commit-push.py -m "your message"
python add-commit-push.py -m "your message" -f
python add-commit-push.py
