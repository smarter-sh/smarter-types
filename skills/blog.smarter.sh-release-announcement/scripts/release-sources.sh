#!/usr/bin/env bash
# Print the source material for a release announcement: the full message of
# every commit between two release tags, oldest first, without the release
# commits that semantic-release makes.
#
# CHANGELOG.md lists one-line commit subjects. The commit bodies explain what
# each change is, why it exists, its limits and its upgrade steps, which is
# what the blog post needs.
#
# usage, from the repository root:
#   skills/blog.smarter.sh-release-announcement/scripts/release-sources.sh <from-tag> <to-tag>
#   e.g. release-sources.sh v0.1.0 v0.2.0, or v0.0.0 v0.1.0 for a first release
set -euo pipefail

FROM="${1:-}"
TO="${2:-}"
if [ -z "$FROM" ] || [ -z "$TO" ]; then
  echo "usage: $0 <from-tag> <to-tag>" >&2
  exit 1
fi
for ref in "$FROM" "$TO"; do
  if ! git rev-parse -q --verify "${ref}^{commit}" >/dev/null; then
    echo "unknown tag: $ref (git fetch --tags, then run again)" >&2
    exit 1
  fi
done

git log --reverse --no-merges --format=%H "${FROM}..${TO}" |
  while read -r sha; do
    subject="$(git log -1 --format=%s "$sha")"
    case "$subject" in "chore(release):"*) continue ;; esac
    echo "================================================================"
    git log -1 --format='commit %h  %ad%n%n%B' --date=short "$sha"
    git show --stat --format= "$sha" | tail -1
    echo
  done
