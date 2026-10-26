---
name: smarter-types-git-commits
description: Use whenever the user asks you to "write a git commit" (or a commit message, or the git add) in the smarter-types repo. Covers the never-execute rule, authorship, the multiple -m command format, conventional-commit types and scopes, how semantic-release turns them into versions, the BREAKING CHANGE footer, and how thorough the body must be.
---

# smarter-types Git Commits

## The rule: write, never execute

"Write a git commit", in any wording or tone, means **output the command as
text**. It never means run it, however emphatic the request.

- Never execute `git commit`, `git add`, `git reset`, `git restore --staged`,
  `git push`, `git tag`, `git stash`, or any other git command that writes.
  The user stages, commits, tags and pushes.
- Read-only git commands (`git status`, `git diff`, `git log`) are fine.
- Don't volunteer commit messages. Write one only when asked.

## Authorship

Lawrence McDaniel is the author. You are a co-author, and your email is `noreply@anthropic.com`.

- `--author="Lawrence McDaniel <lpm0073@gmail.com>"`
- The last `-m` is `Co-authored-by: Claude <noreply@anthropic.com>`.

## Command format

Exactly one `git commit` command in one code block:

```console
git commit --author="Lawrence McDaniel <lpm0073@gmail.com>" \
  -m "<type>(<scope>): <subject>" \
  -m "<body paragraph>" \
  -m "<body paragraph or bullet list>" \
  -m "Co-authored-by: Claude <noreply@anthropic.com>"
```

- One `-m` per paragraph. git joins them with blank lines.
- No heredoc, no `-F`, and no `git add` in the same block.
- Avoid backticks, `$` and `!` inside the double-quoted messages. The user's
  shell is zsh, where `!` in double quotes is history expansion and aborts the
  command (`zsh: event not found`). Reword instead.
- When the user asks for the `git add` too, write it as a separate code block,
  listing the paths explicitly.

## Subject line

`<type>(<scope>): <subject>`. The commitlint pre-commit hook
(`commitlint.config.js`: `@commitlint/config-conventional` plus
`@commitlint/config-angular`) checks it, and **semantic-release reads it to
version the package** (`release.config.js`, `smarter-types-release`).

- **type** decides the release:
  - `fix`: a bug fix, or repairing a shortcoming of something that exists.
    Makes a **patch** release.
  - `feat`: a new capability a user can see: a new SAM kind, cli command,
    journal thing, enumeration or class method. Makes a **minor** release.
    When in doubt, it is `fix`.
  - `perf`: a patch release, for a measurable speed-up.
  - `docs`, `test`, `refactor`, `style`, `build`, `ci`, `chore`: no release.
- **A breaking change** (rule 6 of `smarter-types-development`: a removed or
  renamed member, a changed value, a reordered `apply_order()` that a caller
  relies on, a dropped Python version)
  gets a footer paragraph `-m "BREAKING CHANGE: <what breaks, and what users
must do>"`. It makes a **major** release.
- **scope**, lower case: `kinds`, `journal`, `enum`, `exceptions`, `tests`,
  `docs`, `adr`, `skills`, `ci`, `release`, `deps`. Omit it for changes across
  the whole repository.
- **subject:** imperative mood, lower case, no trailing period.
- **length:** the whole header must be **72 characters or fewer**. commitlint
  rejects 73. Measure it, and aim for 70:

  ```console
  printf %s "feat(kinds): add the Orchestrator kind" | wc -c
  ```

- `chore(release): ...` belongs to semantic-release. Never write it yourself.

## Body

Write for a reader with no context, a reviewer six months from now. A terse
four-bullet body is too brief.

- Start with the problem or motivation: what was wrong or missing, and how it
  showed up.
- Then area by area, a heading paragraph per area (e.g.
  `Kinds (src/smarter_types/kinds.py):`), then one bullet per change, saying
  what changed and why, including alternatives you rejected.
- Name files, classes, settings and commands precisely.
- Cover the tests: what's new, and what they prove.
- End with the status: the Python versions you tested, skips, follow-ups, and
  whether the platform and the SDK need their minimum version raised.

## Before writing

1. Run `git status` and `git diff --stat` (and `git diff` on anything unclear).
2. Check which files belong to the commit, if that's ambiguous.
3. Measure the header with `wc -c`.
4. Start the response with a one-line `Written for:` audience note.

A change that the platform or the SDK adopts (a new kind here, then their
minimum-version bump and its use) gets one commit command per repository. In
`../smarter`, follow Smarter's own `smarter-git-commits` skill; in
`../smarter-python`, the SDK's.

See [references/canonical-git-commit.md](references/canonical-git-commit.md)
for a complete, real example.
