# Spelling Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a timed spelling game that satisfies the task-book game requirement and reuses the existing leaderboard points system.

**Architecture:** Keep game scoring in a small pure Java policy so it can be tested without Android SDK. Add one Android Activity for the game screen, launch it from the statistics page, and reuse existing Room DAOs, `WordReviewPolicy`, `SessionManager`, and `LebeiApi.recordStudyWord`.

**Tech Stack:** Android Java, Room, OkHttp API client, JUnit 4 pure Java tests.

---

### Task 1: Game Policy

**Files:**
- Create: `lebei/app/src/main/java/com/example/lebei/SpellingGamePolicy.java`
- Create: `lebei/app/src/test/java/com/example/lebei/SpellingGamePolicyTest.java`

- [ ] Write failing JUnit tests for score changes, answered count changes, and time-up detection.
- [ ] Run the pure Java JUnit command and confirm the new tests fail because `SpellingGamePolicy` is missing.
- [ ] Implement `SpellingGamePolicy` with `GAME_DURATION_MS = 60_000`, `scoreAfterAnswer`, `answeredAfterSubmit`, and `isTimeUp`.
- [ ] Run the pure Java JUnit command again and confirm the tests pass.

### Task 2: Word Selection Support

**Files:**
- Modify: `lebei/app/src/main/java/com/example/lebei/WordDao.java`

- [ ] Add queries for game words: due review words first and learned fallback words.
- [ ] Keep ordering deterministic and useful: lower weight first, due time first, difficult tag first.

### Task 3: Game Activity

**Files:**
- Create: `lebei/app/src/main/java/com/example/lebei/SpellingGameActivity.java`
- Create: `lebei/app/src/main/res/layout/activity_spelling_game.xml`
- Modify: `lebei/app/src/main/AndroidManifest.xml`

- [ ] Add a toolbar-style Activity with timer, score, translation, phonetic, input, submit, skip, replay, and leaderboard controls.
- [ ] Load words on a background executor under `LocalLearningDataStore.withDbLock`.
- [ ] On correct spelling, update local word weight with `WordReviewPolicy`, increment score, sync learned count, and call `recordStudyWord`.
- [ ] On wrong spelling or skip, show feedback and move to the next word without awarding points.
- [ ] Stop the timer and executor safely on destroy.

### Task 4: Entry Point

**Files:**
- Modify: `lebei/app/src/main/res/layout/fragment_statistics.xml`
- Modify: `lebei/app/src/main/java/com/example/lebei/StatisticsFragment.java`

- [ ] Add a “限时拼写挑战” button beside the existing leaderboard button.
- [ ] Require login before launching, matching the leaderboard behavior.

### Task 5: Verification And Git

**Files:**
- Verify all changed files.

- [ ] Run the pure Java JUnit command for `WordReviewPolicyTest` and `SpellingGamePolicyTest`.
- [ ] Run `git diff --check`.
- [ ] Confirm no Android SDK paths or `local.properties` were added.
- [ ] Commit and push the branch.
