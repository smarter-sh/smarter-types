---
name: smarter-types-code-quality
description: Use before finishing any change to smarter-types, to lint and format it with the repository's pre-commit hooks (black, flake8, isort, autoflake, bandit, codespell, pyupgrade, pydocstringformatter, Prettier, commitlint). Explains which tools are authoritative, how to run them under zsh, and the hooks' traps (untracked files, capitalized docstrings, a prettier cache folder).
---

# smarter-types Code Quality

`.pre-commit-config.yaml` is the authoritative standard. It follows Smarter's
Python hooks (`../smarter/.pre-commit-config.yaml`), without the React ones. If
a hook passes, the code meets the standard; if it fails, fix the code. Never
bypass a hook (`--no-verify`, `SKIP=`, a blanket `# noqa`). CI's `lint` job
runs every hook on every file, so a bypassed hook fails the pull request
anyway.

## What the hooks enforce

| Hook                 | Configuration                       | Notes                                                                                                                             |
| -------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| black                | `pyproject.toml`, line length 120   | Formatter. Let it reformat.                                                                                                       |
| isort                | `pyproject.toml`, `profile = black` | Import order.                                                                                                                     |
| autoflake            | `--remove-all-unused-imports`       | **No-op**: `args` drops the hook's default `--in-place`, so it only prints a diff. flake8's F401 finds unused imports.            |
| flake8               | `.flake8`, line length 120          | **Every** check runs, unlike Smarter's `.flake8`, which selects only C101.                                                        |
| bandit               | `-ll`                               | Medium or high severity findings fail.                                                                                            |
| pyupgrade            | `--py310-plus`                      | Rewrites annotations to `X \| None`. See `smarter-types-typing`.                                                                  |
| pydocstringformatter |                                     | Docstring layout. Capitalizes the first word: see below.                                                                          |
| codespell            |                                     | Spelling in code, comments and docs.                                                                                              |
| prettier             | Markdown, YAML, JSON                | Formats the README, skills and workflows.                                                                                         |
| commitlint           | `commitlint.config.js`              | Checks each commit message, at the `commit-msg` stage. semantic-release reads the same messages: see `smarter-types-git-commits`. |

Plus trailing whitespace, end-of-file newlines, YAML/JSON/TOML syntax, merge
conflict markers, private keys and debug statements.

**ruff is not configured.** Don't report ruff output as lint debt.

## How to run

```console
make init                    # once: installs pre-commit, and the pre-commit and commit-msg hooks
git diff --name-only | xargs venv/bin/pre-commit run --files
git ls-files --others --exclude-standard | xargs venv/bin/pre-commit run --files   # new files
make pre-commit-run          # every hook on every tracked file (= make lint)
make pre-commit-init         # reinstall the hooks and update their versions (pre-commit autoupdate)
```

- **`--all-files` skips untracked files**: it uses `git ls-files`. Check a new
  file with `--files`.
- Use `xargs`. Under zsh, `pre-commit run --files $FILES` passes one argument,
  and pre-commit checks nothing.
- Hooks that modify files fail the first run, then pass. Run them until they
  pass, and read the diff of what they changed.
- `make pre-commit-run` is slower, and touches files you didn't change. Use
  it before a pull request, and `--files` while you work.
- **pydocstringformatter capitalizes a docstring's first word**, e.g.
  `smarter_types.kinds` becomes `Smarter_types.kinds`. Start module docstrings
  with a sentence (`smarter-types-docstrings`).
- **The prettier hook can leave a `node_modules/.cache/` folder** in the
  repository root. It is git-ignored; `make clean` removes it. Don't pass it to
  the hooks.
- `make pre-commit-init`, and so `make init`, runs `pre-commit autoupdate`,
  which edits `.pre-commit-config.yaml`. That change is a commit of its own
  (`build:`): don't fold it into an unrelated one.

## Principles

- Match the surrounding code: naming, comment density, the logging style in
  `smarter-types-development`.
- Fix the cause of a finding. Suppress one only with a narrow, commented
  directive that says why, e.g. `# nosec B105: test settings only`.
- Don't reformat code you didn't otherwise change. It buries the real diff.
