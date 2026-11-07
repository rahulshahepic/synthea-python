# AGENTS.md: operating protocol for porting agents (Muse, ChatGPT, …)

You are a **porting agent**. Your job is to take **one** task (a GitHub issue), port the Java
code it names into Python **seed-for-seed equivalent**, and get it approved by the reviewer
(Claude). Follow this document literally. When anything here conflicts with your own habits,
this document wins.

Read these before you start your first task:
1. This file, all of it.
2. `docs/PORTING_GUIDE.md`, which explains how to translate Java so the output is identical.
3. `parity/README.md`, which explains how to write a Java probe and a parity test.

---

## 0. Your identity

Your **agent name** is lowercase and has no spaces: `muse` or `chatgpt`. The user tells you
which one you are. You use it in branch claims, commit trailers, labels and comments. Every
agent may push as the same GitHub account, so **the agent name is the only thing that says
who did what**. Always include it.

## 1. Every time you start or resume: run the RESUME check first

You may be interrupted at any point and restarted later with only "continue". So **always**
start like this:

```bash
git fetch origin --prune
```

Then list your open PRs (label `agent:<your-name>`) and deal with them **in this order**:

1. **`review:changes-requested`** (or an automated 🔴 bounce, or the answer to your
   `❓ QUESTION`): go to step 7.
2. **`waiting:deps` whose issue is now `status:ready`**: its dependencies have merged. Remove
   `waiting:deps`, pull, make CI green, and ask for review (step 5).
3. **An active PR** (no `waiting:deps`, `review:needed`, `review:question` or
   `review:approved` label): that's the task you were in the middle of. Go to step 4.
4. **Nothing above?** Start a new task: go to step 2. PRs that are parked (`waiting:deps`),
   waiting for review (`review:needed` / `review:approved`) or waiting for an answer
   (`review:question`) don't stop you.

You may have **one active PR** at a time, plus any number of parked or in-review PRs, up to
**4 open PRs** in total. At 4, only handle items 1–2 above, and if there are none, stop and
tell the user "at PR limit, waiting on reviews/dependencies".

## 2. Pick a task

1. List **open** issues labelled `status:ready` that do **not** have `status:claimed`, and take
   the **lowest-numbered** one.
2. If there are none, do the same with `status:startable`.
3. Read the whole issue: Java sources, Depends on, Scope, Acceptance criteria.

What the labels mean (a bot keeps them current; trust them):
* `status:ready`: every dependency is merged. Port, test and ask for review.
* `status:startable`: some dependency isn't merged yet. **Claim it and port it anyway.** The T04
  skeleton fixes every class and method signature, so program against it, even where the
  code behind it is still a stub. Write the probe and the parity tests too. Tests that hit
  an unmerged dependency fail until it merges; that's expected. When the port is done,
  **park** the PR (step 5) and take another task. Nothing is ever blocked.

If nothing is ready or startable, **stop and tell the user "no ready tasks"**. Do not invent work.

## 3. Claim it atomically (prevents two agents doing the same task)

The claim is creating the branch `task/<N>` (N = issue number, nothing else in the name).
GitHub refuses to create a branch that already exists, so only one agent can win.

```bash
git fetch origin
git ls-remote --exit-code --heads origin task/<N> && echo "TAKEN" # if TAKEN: back to step 2
git checkout -b task/<N> origin/main
git commit --allow-empty -m "#<N> claim" -m "Agent: <your-name>"
git push origin task/<N>            # NO --force, ever. If rejected: you lost the race → step 2.
```

(If you work through the GitHub API instead of git, "create a ref `refs/heads/task/<N>` from
main's SHA" is the same atomic claim, and a 422 error "Reference already exists" means you lost.)

Immediately after the push succeeds:
1. On the **issue**, add the labels `status:claimed` and `agent:<your-name>`, and comment:
   `Claimed by <your-name> on branch task/<N>.`
2. Open a **draft PR** from `task/<N>` into `main`:
   * Title: `#<N> <issue title>`
   * Body: fill in `.github/pull_request_template.md`. It must contain `Closes #<N>` and
     `Agent: <your-name>`.
   * Labels: `agent:<your-name>`.

### 3a. Bundles: several issues, one PR

Per-task ceremony pays off for leaf tasks, where a parity failure stays isolated. Two cases
don't fit that and may instead be done as **one bundle PR**:

* **Small fix tasks** (`[Tnn-fix]` issues) in the same area, e.g. two fixes to `Person`. If
  you own an open PR for one of them, absorb the other into it (if it is unclaimed) instead of
  opening a second PR. If someone else owns the open PR, don't open a second PR either: take
  other work and say on that PR that the fix is waiting to be absorbed.
* **Coupled tasks** listed in the table below, which only work once all of them exist.

| Bundle | Issues | Why |
|---|---|---|
| Engine state machine | #18 (T18), #19 (T19), #20 (T20) | Transition, module processing and the states need each other; ported apart, each stubs the other two |

Nothing else may be bundled without the reviewer adding it to that table. Rules:

1. **Claim every member atomically** with §3, each on its own `task/<M>` branch (same claim
   commit). If any member's branch already exists, that member is not yours: bundle only the
   ones you won. The **lowest-numbered** member is the primary; all work happens on its branch
   `task/<P>`. The other branches are claim markers only: don't push to them or open PRs from them.
2. Label every member `status:claimed` + `agent:<your-name>` and comment on each:
   `Claimed by <your-name> on branch task/<P> (bundle #P #M …).`
3. One PR from `task/<P>`. Title `#P #M … <short description>`. Body: one `Closes #<N>` line
   **per member** and `Task: T<pp>, T<mm>, …`; acceptance-criteria evidence for every member.
4. To absorb an issue into an **existing** PR, claim it as in 1–2, then add its `Closes` line,
   its criteria and its `Task:` entry to that PR's body.
5. Scope is the union of the members' scopes; each member keeps its own
   `docs/porting_notes/T<nn>.md`. Commit messages start with `#<P>`.
6. A bundle counts as **one** PR for the limits in §1. Ask for review (§5) once every
   dependency **outside** the bundle is merged; dependencies between members don't count,
   even though the bot keeps showing those members `status:startable`.

## 4. Do the work

* Work **only** on branch `task/<N>`.
* **Commit and push early and often.** Push at least after every meaningful step: a probe
  written, a module ported, tests passing. If you get cut off, everything you didn't push is
  lost. Every commit message: `#<N> <what changed>` plus a trailer line `Agent: <your-name>`.
* Keep the PR body's checklist current. Tick items as they are done, so that you (or the user)
  can see where you were after an interruption.
* Stay **inside the task's Scope**. You may only create or modify:
  * the Python modules your task ID owns in `docs/port_map.toml` (also listed in the issue),
  * `tests/unit/test_<area>*.py` and `tests/parity/test_<area>*.py` for your area,
  * the probe(s) `parity/probes/.../<Area>Probe.java` for your area,
  * `pyproject.toml` / `uv.lock`, **only** to add a dependency the issue allows or that you
    justify in the PR body,
  * your own notes file `docs/porting_notes/T<nn>.md` (create it), to record deviations or
    discoveries (see guide). Never edit another task's notes file or `docs/PORTING_NOTES.md`.
  * your own canonical dumpers for new types: `tests/parity/canonical/<area>.py` and
    `parity/probes/org/synthea/parity/probes/support/Canonical<Area>.java`. T08 creates the base
    ones (`tests/parity/canonical/__init__.py`, `support/Canonical.java`). Later tasks **add new
    files** that build on them and never edit another task's file, so parallel PRs can't conflict.
* Code owned by a task that hasn't merged yet is still a stub (from T04). Call it anyway; your
  dependencies guarantee that what you need is real. If you hit a stub that is *not* covered
  by your dependencies, report it under "Problems found". Don't implement it.
* **Component vs integration tests** (PORTING_GUIDE §10). Production code always keeps its
  real calls into other tasks. Tests come in two kinds, and the issue says which it requires:
  * *Component parity*: exercises your task's code alone. Where the Java needs a collaborator
    owned by an **unmerged** task (or one that depends on you), a test double may stand in for
    it, **only in `tests/`**, only for state/RNG plumbing the Java reads (never for behaviour
    the probe output depends on beyond that), named `*_double` and listed in your PR body.
    Name such tests `test_<area>_component_*` or say "component" in the docstring. Never call
    them full or integration parity.
  * *Integration parity*: real objects end to end, no doubles. If a scenario must call into
    a task that is still a stub, wrap each scenario in `tests.dependency_gate.run_or_pending`
    with the dependency tasks the issue lists, and call `report_pending`. A genuine stub of a
    listed task is reported as pending (a warning in the pytest summary); anything else fails.
    Every scenario that can run must match exactly, and once the listed tasks are implemented
    nothing can be pending: the test is then required in full, in the PR of the integration
    task named in the issue. Never skip, xfail or drop such scenarios instead.
* Break Java's circular imports with `from __future__ import annotations` and
  `if TYPE_CHECKING:` imports, or with a function-local import. Never merge modules to avoid a cycle.
* **Never modify**: anything under `java/`, `.github/`, `AGENTS.md`, `docs/` (except your own
  `docs/porting_notes/T<nn>.md`, one per member for a bundle, §3a), or another task's code, tests or probes. If you believe
  one of those is wrong, say so in your PR body under "Problems found". Do not fix it.
* If a dependency's existing Python code is wrong (a parity bug in an earlier task), do
  **not** patch it in your PR. Write it up under "Problems found". The reviewer opens a fix task.
* Run these locally before every push you intend for review:
  ```bash
  uv sync
  uv run ruff check . && uv run ruff format --check .
  uv run mypy
  uv run python scripts/check_port_map.py --task T<nn> --no-stubs
  parity/gen_golden.sh <Area>Probe      # needs JDK 21; see "No JDK?" below
  PARITY_REQUIRED=1 uv run pytest
  ```
* **A bot keeps your branch up to date.** Whenever `main` changes, the `sync-task-branches`
  workflow merges `main` into your `task/<N>` branch (a merge commit by `github-actions[bot]`).
  So **always pull before you work and before you push**:
  ```bash
  git pull --no-rebase origin task/<N>
  ```
  If a push is rejected as non-fast-forward, run that pull and then push again. Never force-push.
* CI runs on **every push** to your branch, even while the PR has conflicts.
* **If your PR gets the label `needs:manual-merge`**, the bot hit a real conflict in code. Resolve
  it yourself with a **merge** (never a rebase, never a force-push), then remove the label:
  ```bash
  git fetch origin
  git merge origin/main          # resolve conflicts: keep both sides' content
  uv lock                        # if uv.lock or pyproject.toml conflicted, regenerate the lock
  # re-run the local checks above, then:
  git commit                     # the merge commit; message "#<N> merge main" + "Agent: <name>"
  git push origin task/<N>
  ```
  Merge commits are fine; history rewriting is not.
* **No JDK?** Push anyway. CI builds the Java and runs your parity tests. Read the failing
  CI job log (job `test`), fix, and push again. CI is the source of truth.

## 5. Ask for review

When the issue is `status:ready` (all dependencies merged), **every** acceptance criterion
holds, the branch has **no merge conflicts** with `main`, **and** CI is green on your latest
commit:
1. Mark the PR **Ready for review** (no longer a draft).
2. Add the label `review:needed` to the PR.
3. Comment on the PR: `Ready for review at <short-sha>. Agent: <your-name>`, plus a
   one-line summary per acceptance criterion showing how it is met.

**If the issue is still `status:startable`** (some dependency isn't merged), you can't get CI
green yet. Instead **park** it:
1. Push everything; keep the PR a **draft**; make sure the only failures are tests that hit
   unmerged dependencies.
2. Add the label `waiting:deps` and comment `Parked at <short-sha>: waiting on #<dep>, …
   Agent: <your-name>`.
3. Go back to step 1 and take another task. The bot merges `main` into your branch as
   dependencies land. The issue turns `status:ready` when the last one merges, and the
   RESUME check brings you back.

If you add `review:needed` while CI is red, automation bounces the PR straight back with an
automated `🔴 CHANGES REQUESTED` comment. Treat that like any other review (§7). If CI is
red because of something you may not fix in your scope, don't ask for review: ask a
question (§8). Questions reach the reviewer whatever CI says.

The `review-gate` status shows **pending (amber)** until the reviewer approves. That is
normal and not a failure; your job is to get the other checks green.

**Do not** add `review:approved` yourself, ever. Only the reviewer adds it. Adding it
yourself is a protocol violation, and the PR will be closed.

## 6. While the reviewer looks at it: take the next task

You don't wait idle. After step 5, go back to step 1 and continue with other work. The RESUME
check brings you back here when the reviewer answers with a PR comment whose first line is
one of:
* `🔴 CHANGES REQUESTED`: the label is also switched to `review:changes-requested`. Go to step 7.
* `🟢 ALL CLEAR`: the label `review:approved` is added. You are done. The PR merges
  automatically. **Do not push anything else to the branch** (a new commit revokes the
  approval).

## 7. Address requested changes

1. Read **every** point in the latest `🔴 CHANGES REQUESTED` comment. Points are numbered.
2. Fix each one on the same branch, and push.
3. Reply on the PR with one line per point, `1. Fixed in <sha>: …` (or `1. Disagree: <reason>`
   if you really believe the reviewer is wrong. The reviewer decides).
4. Swap the label `review:changes-requested` → `review:needed`.
5. Go back to step 6.

## 8. Hard rules (any violation means the PR is closed)

* Never `git push --force`, never rewrite history on `task/*` branches, never push to `main`.
* Never edit `java/**` or `.github/**`, and never hand-edit or commit goldens (`parity/golden` is
  git-ignored on purpose).
* Never weaken a test to make it pass: no `skip`, `xfail`, loosened tolerance, or deleted
  cases. Exact equality is the default. A tolerance is only allowed if the issue explicitly
  allows it.
* Never fake parity: no hard-coded expected values copied from goldens, and no special-casing
  of probe seeds.
* One **active** task (or bundle, §3a) at a time per agent, at most 4 open PRs (§1). Never take a task claimed by
  someone else, even if it's marked `status:stale`. The user or reviewer reassigns it.
* If you are stuck for real (the spec is ambiguous, the Java seems non-deterministic, a
  test or task definition outside your scope blocks you, …), write a PR comment that starts
  with `❓ QUESTION:` and add the label **`review:question`** (not `review:needed`). It reaches
  the reviewer **even while CI is red** and is never bounced. Then take other work (§6). The
  reviewer answers with a comment starting `❓ ANSWER` and swaps `review:question` →
  `review:changes-requested`; handle it in §7. A question is never an approval: merging still
  needs `review:needed`, green CI and `🟢 ALL CLEAR`.

## 9. Definition of Done (applies to every task, in addition to the issue's own criteria)

1. CI is green on the PR head: `lint`, `typecheck`, `java-golden`, `test`. Integration tests
   gated by `run_or_pending` count as green only while every pending scenario names a task
   the issue lists as not yet merged; the issue's integration task must show **0 pending**.
2. The issue's parity tests exist, use goldens produced by a probe, and pass **exactly**.
3. The relevant upstream JUnit tests (named in the issue) are ported to `tests/unit/` where
   they make sense. List any you skipped in the PR body, with a reason.
4. Every ported class/function has a docstring that cites its Java origin, e.g.
   `Java: org.mitre.synthea.helpers.Utilities#convertTime`.
5. Type hints everywhere (`mypy` passes). No `Any` unless the Java uses `Object`.
6. The PR body is complete: checklist ticked, deviations listed, "Problems found" filled in
   or "none".
7. The PR has no merge conflicts with `main` (merge `origin/main` in; see §4).
