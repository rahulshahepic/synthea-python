# Review process (reviewer: Claude)

This file is both the reviewer's runbook and the instructions for the scheduled review routine.

## Labels

| Label | On | Meaning | Set by |
|---|---|---|---|
| `type:task` | issue | a porting task | reviewer |
| `status:blocked` | issue | dependencies not merged yet; do not take | reviewer |
| `status:ready` | issue | all dependencies merged; may be claimed | reviewer |
| `status:claimed` | issue | an agent owns it (branch `task/<N>` exists) | agent |
| `agent:muse` / `agent:chatgpt` | issue + PR | who owns it | agent |
| `review:needed` | PR | agent asks for a verdict (or asked a `❓ QUESTION`) | agent (and CI, after a post-approval push) |
| `review:changes-requested` | PR | reviewer asked for changes | reviewer |
| `review:approved` | PR | reviewer approved **this exact head commit**. Turns the required `review-gate` status from pending (amber) to success | reviewer only |

Every party may push as the same GitHub account, so GitHub's native "Approve" / "Request
changes" cannot be used. A review is a PR comment whose first line is `🟢 ALL CLEAR` or
`🔴 CHANGES REQUESTED`, plus the label swap. The `review-gate` workflow turns the label into a
required commit status (pending until approved, never a red failure), and removes the label
automatically when an agent pushes new commits.

Order of operations: automated checks (`lint`, `typecheck`, `java-golden`, `test`) run on every
push and come first. The reviewer only looks at PRs whose CI is green.

## Routine (each scheduled run)

1. **Housekeeping**
   * For every open `type:task` issue with `status:blocked`: if all its "Depends on" issues are
     closed, swap the label to `status:ready`.
   * For every `status:claimed` issue: if the branch `task/<N>` does not exist, or nothing was
     pushed for > 72h and the PR is not in review, comment on the issue and tell the user.
     Do not release the claim automatically.
   * Look for protocol violations: an agent with two open PRs, `review:approved` added by
     someone other than the reviewer, pushes to `main`, edits under `java/` or `.github/`.
     Flag them on the PR and tell the user.
2. **Review** every open PR labelled `review:needed` whose CI is green on the head commit,
   oldest first. (`review-dispatch.yml` already bounces PRs with red CI back to the agent
   automatically, and wakes this routine when a PR is green and waiting. Skip a PR whose CI
   is still running: you'll be woken again when it finishes.)
   1. Read the issue (scope + acceptance criteria) and the full diff at the head SHA.
   2. Check CI on the head SHA. If it's red, request changes with the failing job and the reason.
      If the PR conflicts with `main` (no checks appear at all), request changes: "merge
      `origin/main` into your branch (AGENTS.md §4)".
   3. Check scope: the changed files must be owned by the PR's task in `docs/port_map.toml`,
      or be its own tests, probes, or `docs/porting_notes/T<nn>.md`.
   4. Check faithfulness: compare the Python with the Java side by side. Look for RNG call
      order and count, iteration over Java hash collections, number formatting, integer
      arithmetic and rounding, BigDecimal scale, and time zone handling (PORTING_GUIDE).
   5. Check that the tests are real: the probe exercises the claimed breadth, the parity tests
      compare against goldens (nothing hard-coded or skipped, no loosened tolerances), and
      the JUnit ports are present.
   6. Run `scripts/check_port_map.py --task T<nn> --no-stubs` if the task requires it.
   7. Verdict:
      * **Changes needed**: comment `🔴 CHANGES REQUESTED (reviewed <sha>)` followed by
        numbered, actionable points (file:line, what is wrong, what "fixed" looks like). Swap
        `review:needed` → `review:changes-requested`.
      * **All good**: comment `🟢 ALL CLEAR (reviewed <sha>)`. Swap `review:needed` →
        `review:approved`. When `review-gate` and CI are green on that SHA, **squash-merge**
        with the title `#<N> <title> (T<nn>)`. The issue closes via `Closes #<N>`. Then run
        housekeeping again so dependants become `status:ready`.
      * **❓ QUESTION**: answer it in a comment and swap `review:needed` →
        `review:changes-requested` (the agent's next action is to read your answer).
3. **Problems found**: for every real issue an agent reports under "Problems found", open a
   fix task (an issue with acceptance criteria) owned by the module's task ID, labelled
   `status:ready`. Link it from the PR.
4. Post a short summary for the user: merged, reviewed, blocked, stale.

## Merge policy

* Squash-merge only, and only by the reviewer.
* Require: CI (`lint`, `typecheck`, `java-golden`, `test`) green **and** `review-gate` green
  on the head commit.
* If the branch is behind `main` and conflicts, request changes ("merge `origin/main` in; never rebase"). If it
  is only behind, update it from `main`, let CI rerun, and merge if still green.

## Conflicts are handled automatically

* `ci.yml` runs on every push, so CI results exist even while a PR conflicts.
* `sync-task-branches.yml` merges `main` into every open `task/*` PR each time `main` changes
  (resolving `uv.lock` by regenerating it), then dispatches `ci` and `review-gate` on the new
  head. A sync merge does **not** revoke `review:approved`; the re-dispatched `review-gate`
  re-checks the label. If CI on the synced head is green, merge.
* A real code conflict gets the `needs:manual-merge` label and one comment. Treat it as
  "waiting on the agent". Never resolve it yourself.
