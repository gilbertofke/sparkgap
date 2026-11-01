# ADR-0002: Commit convention and history policy

Status: accepted
Date: 2026-11-01

## Context
Sparkgap is open source and expects contributions from developers who do not
know the codebase. A consistent history lets a contributor understand why a
change was made, lets a maintainer revert or bisect a single change, and
allows release notes to be generated from commit metadata instead of written
by hand. Without a written standard, history quality depends on each
contributor's habits, and it degrades over time.

## Decision
Commit messages follow Conventional Commits:

    type(scope): imperative summary

- The type is one of feat, fix, test, docs, refactor, build, ci, chore, perf.
- The scope is optional and names the affected area, for example masking.
- The summary is lowercase, in the imperative mood, without a trailing period,
  and at most 72 characters.
- A body is added when the reason for the change is not obvious from the
  diff. It explains why, and records any tradeoff.

Two rules apply to every commit:

1. One logical change per commit. A commit that needs the word "and" in its
   summary is usually two commits.
2. Every commit leaves the repository passing lint, type checks and tests, so
   that bisecting and reverting remain safe.

Changes reach main only through pull requests, merged with "rebase and merge"
so that each commit is preserved and history stays linear. Squash merges and
merge commits are disabled for the repository. Branch protection requires the
`check` and `commits` CI jobs to pass and requires linear history.

The `commits` job validates every commit message in a pull request with
commitizen. A local commit-msg hook is recommended so mistakes are caught
before pushing.

## Alternatives considered
Squash and merge. It is simple for contributors, because only the pull request
title has to follow the convention, and it keeps main tidy. It was rejected
because it collapses a series of deliberate commits into one, which removes
the granularity that makes revert and bisect useful.

Merge commits. They preserve every commit but add merge nodes, so history is
no longer linear and is harder to read, bisect and generate notes from.

Free-form messages with review comments as the only control. This costs
nothing to adopt, but it depends on reviewers noticing and repeating the same
feedback, and it makes automated release notes impossible.

A different structured convention, such as a project-specific prefix list.
Conventional Commits was chosen because tooling for it already exists in
several ecosystems, and contributors are likely to know it.

## Consequences
Easier: reverting or bisecting a single change, reading history, and
generating a changelog from commit types.

Harder: contributors must clean up their own history before a pull request is
merged, because rebase merging publishes commits exactly as submitted.
Rebase merging also gives each commit a new hash on main, so local branches
must be deleted with `git branch -D` after a merge, since git cannot tell the
rewritten commits are the same work.

Limits of enforcement: the `commits` job checks message format only. It
cannot judge whether a commit is truly atomic. The `check` job runs on the
final state of the pull request, so it does not prove that each intermediate
commit is green. Rule 2 therefore relies on contributor discipline and review.

Maintainer exception: administrator enforcement is disabled on main so a
sole maintainer can recover from a broken pipeline. The rule remains that
nothing is pushed to main directly. The only direct pushes were the initial
bootstrap commits, which were made before CI and branch protection could
exist. This is also recorded in ADR-0001.

Cost: a failed message check can block a pull request over wording alone.
