# Git hooks

Enable the repository hooks locally:

```sh
git config core.hooksPath .githooks
```

- `pre-commit` runs `git diff --cached --check`, blocks common secret-bearing file paths, and rejects common private-key/token signatures in staged additions.
- `pre-push` runs the focused continuity, ethics, memory-stewardship, boot, trust, and consequence-gate regression tests.

Run them manually with:

```sh
git hook run pre-commit
git hook run pre-push
```

The pre-push suite is a fast safety gate, not a replacement for the complete test suite or release CI.
