# Review Weight And Spelling Review Design

**Goal:** Finish the Android vocabulary review feature requested in the chat: each word has a 0-6 weight, learned words start at 5, correct spelling review raises weight, wrong review lowers weight, mastered words are counted when weight is greater than 5, and high-weight words decay over time.

**Recommended approach:** Use a small deterministic local scheduler instead of adopting full SM-2 or FSRS. The project already stores local word progress in Room and the customer described an explicit weight rule, so a transparent 0-6 model is easier to explain, test, and deliver within two or three days.

**Scope:** Android app first. The Spring Boot server and Vue admin web can stay unchanged unless the customer later requires the server-side leaderboard to show mastered-word count rather than total learned/study points.

---

## Research Summary

Exa research points to three relevant ideas:

- [SuperMemo SM-2](https://super-memory.org/archive/english/ol/sm2.htm) stores per-item scheduling state and grows review intervals after successful reviews. Failed recall resets the item into relearning.
- [Anki's studying model](https://docs.ankiweb.net/studying.html) separates incorrect recall from difficult-but-correct recall. Anki also notes that a simple two-button model can work: use one action for incorrect answers and one for correct answers.
- [Anki deck options](https://docs.ankiweb.net/deck-options) use short relearning steps for failed cards and daily limits for review workload, which matches this app's existing `dailyReviewWords` setting.
- [FSRS](https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md) is more advanced and uses review history plus model parameters, but it is too heavy for this project because there is no existing review log, optimizer, or server sync for scheduler parameters.

Decision: implement a simple weighted scheduler inspired by SRS principles, not full SM-2/FSRS.

---

## Current Project State

Important files:

- `lebei/app/src/main/java/com/example/lebei/Word.java`
  - Has `familiarity`, `nextReviewTime`, and `reviewCount`.
  - `familiarity` can be reused as the requested word weight.
- `lebei/app/src/main/java/com/example/lebei/WordDao.java`
  - Currently selects review words by `nextReviewTime < currentTime`.
  - Counts mastered words as `familiarity >= 3`, which conflicts with the chat requirement.
- `lebei/app/src/main/java/com/example/lebei/LearnFragment.java`
  - Current buttons are `简单` and `困难`.
  - `简单` increments familiarity by 1.
  - `困难` does not reduce familiarity.
  - There is no spelling input comparison yet.
- `lebei/app/src/main/java/com/example/lebei/DataProvider.java`
  - CSV import reads only `word, phonetic, translation, bookId`.
  - The CSV files contain a fifth column `0/1` that is currently ignored.
- `lebei/app/src/main/java/com/example/lebei/AppDatabase.java`
  - Room database is version 6.
  - Needs a migration if we add a difficulty/tag column.
- `lebei/app/src/main/java/com/example/lebei/StatisticsFragment.java`
  - Displays mastered words using `WordDao.getMasteredWordsCount()`.
- `lebei-server/src/main/java/com/example/lebei/service/UserService.java`
  - Server leaderboard ranks by `studyPoints` and `learnedWordsCount`.
  - It does not know local mastered count.

---

## Proposed Product Behavior

### Weight Rules

Use `Word.familiarity` as the word weight.

- New/unseen word: `0`
- First time learned: set to `5`
- Correct spelling review: `min(6, weight + 1)`
- Wrong spelling review: `max(0, weight - 1)`
- Mastered word: `weight > 5`, so practically `6`
- Review candidate: `weight <= 5`
- Weight upper bound: `6`

This exactly matches the chat wording while keeping the code small.

### Time Decay

High-weight words decay after enough time:

- If `weight == 6` and the word has passed its `nextReviewTime`, reduce it to `5`.
- Once reduced to `5`, it becomes reviewable again.
- Decay should run before building the daily plan, not continuously in the background.

This implements "greater than 5 decreases over time" without adding a background job.

### Scheduling

Keep both weight and time:

- `weight` decides whether the word is mastered or needs review.
- `nextReviewTime` prevents the app from showing the same failed word too aggressively forever.
- Daily review list should prioritize:
  1. Due words with lower weight first.
  2. Earlier `nextReviewTime` first.
  3. Higher CSV difficulty first when ties occur.

Suggested next review times:

- Correct spelling and new weight becomes `6`: `now + 3 days`
- Correct spelling and weight remains `5`: `now + 1 day`
- Wrong spelling and new weight is `4` or lower: `now + 10 minutes`
- Wrong spelling and new weight is `5`: `now + 1 day`

The exact times are intentionally simple. They can be adjusted later without changing the schema.

### Spelling Review UI

Add a spelling check mode to the existing Learn screen instead of building a separate page.

Recommended UI flow:

1. Show Chinese translation and phonetic.
2. Hide the English word for review items.
3. User types the English spelling.
4. App compares normalized input with `Word.word`.
5. Correct result updates weight up.
6. Wrong result shows the correct spelling and updates weight down.

Normalization:

- Trim whitespace.
- Lowercase.
- Collapse repeated spaces.
- Keep letters, apostrophes, hyphens, and spaces.

For first-pass delivery, exact normalized match is enough. Fuzzy matching can wait.

### CSV Difficulty Tag

The fifth CSV column is a local difficulty flag:

- `0`: simple word
- `1`: difficult word

Add `difficultyTag` to `Word`.

Use it for ordering only. Do not change the core weight math based on the tag in the first version, because the customer only said the previous developer had not bound the tag. A visible, testable binding is:

- Difficult words sort earlier in review selection when weight/time tie.
- Optional display text can show `难词` in the review detail later, but this is not required for delivery.

---

## Data Model Changes

### Word

Modify `Word.java`:

- Keep `familiarity` as `weight`.
- Add `public int difficultyTag;`
- Add comments that define the 0-6 range.

### Room Migration

Bump database version from `6` to `7`.

Add migration:

```sql
ALTER TABLE word_table ADD COLUMN difficultyTag INTEGER NOT NULL DEFAULT 0;
```

Existing installed users keep progress. New imports fill `difficultyTag` from CSV.

### CSV Import

Modify `DataProvider.readWordsFromAsset`:

- Continue accepting old four-column rows.
- If column 5 exists, parse it as `difficultyTag`.
- Clamp invalid values to `0`.

Because existing databases already contain words, add a one-time repair path:

- If words exist but `difficultyTag` is still `0` for all rows in a book, update difficulty tags by matching CSV rows on `word + bookId`.

This avoids requiring users to reinstall.

---

## Android Implementation Plan

### Task 1: Centralize Weight Logic

Create `WordReviewPolicy.java`.

Responsibilities:

- Constants: `MIN_WEIGHT = 0`, `LEARNED_WEIGHT = 5`, `MASTERED_WEIGHT = 6`.
- Normalize spelling.
- Calculate next weight for correct/wrong answers.
- Calculate next review time.
- Decide whether a word is mastered.

Reason: `LearnFragment` is already large, so putting rules in a small class makes it testable.

### Task 2: Update Word Queries

Modify `WordDao.java`:

- `getWordsForReview` should select by:
  - `familiarity > 0`
  - `familiarity <= 5`
  - `nextReviewTime <= :currentTime`
  - order by `familiarity ASC, nextReviewTime ASC, difficultyTag DESC`
- `getMasteredWordsCount` should count `familiarity > 5`.
- Add `decayMasteredWords(long now)`:

```sql
UPDATE word_table
SET familiarity = 5, nextReviewTime = :now
WHERE familiarity > 5 AND nextReviewTime <= :now
```

### Task 3: Apply Decay Before Daily Plan Creation

Modify `LearnFragment.loadUserAndTodayWords`:

- Before selecting review words, call `db.wordDao().decayMasteredWords(now)`.
- Then select review words using the new query.
- Keep `dailyReviewWords` as the cap.

### Task 4: Implement Spelling Review

Modify `fragment_learn.xml` and `LearnFragment.java`:

- Add an `EditText` for spelling input.
- Add a `提交拼写` button.
- For review words, show translation first and hide the English word until answer submission.
- For new words, current `简单/困难` flow can remain, but clicking either should set learned weight to `5` for first-time words.

To keep scope controlled:

- `简单` for a new word means learned successfully: set weight `5`.
- `困难` for a new word means still learned but needs soon review: set weight `4` and `nextReviewTime = now + 10 minutes`.
- Spelling review handles mature/review words.

### Task 5: Sync Statistics

Modify `StatisticsFragment` only through existing DAO behavior:

- `已掌握单词` automatically becomes count of `weight > 5`.
- `累计已学` remains `weight > 0`.

Do not change server sync in this pass. The current backend only stores total learned/study points; changing it would expand scope into database/API/admin-web migration.

### Task 6: Optional Server Extension Later

Only do this if the customer explicitly says the web/admin leaderboard must show mastered words:

- Add `masteredWordsCount` to server `users`.
- Add `/api/app/user/stats/mastered-words`.
- Add field to `LeaderboardEntryDto`.
- Update Android sync and admin web table.

This is intentionally out of the first implementation.

---

## Acceptance Criteria

- First-time learned word gets weight `5`.
- Correct spelling review changes `5 -> 6`.
- Wrong spelling review changes `5 -> 4`.
- Weight never goes below `0` or above `6`.
- Mastered count equals words with weight `6`.
- Review queue includes words with weight `1..5` whose `nextReviewTime` is due.
- Weight `6` words decay back to `5` after their review time arrives.
- CSV fifth column is stored in Room and affects review ordering.
- Existing users do not lose local progress when upgrading from database version 6 to 7.
- No Android SDK path, secrets, `node_modules`, build outputs, or local database dump are committed.

---

## Test Strategy

### Unit Tests

Add JVM tests for `WordReviewPolicy`:

- New word + easy -> weight 5.
- Review correct from 5 -> 6.
- Review correct from 6 -> 6.
- Review wrong from 5 -> 4.
- Review wrong from 0 -> 0.
- Spelling normalization handles case and extra spaces.

### DAO Tests

Use Room instrumentation tests if Android test setup is available:

- Insert words with weights 0, 4, 5, 6.
- Verify review query returns due 4 and 5 only.
- Verify mastered count returns only 6.
- Verify decay turns due 6 into 5.

If instrumentation setup is too slow for the delivery window, test DAO behavior manually on emulator and keep `WordReviewPolicy` covered by JVM tests.

### Manual QA

1. Register/login.
2. Choose a plan with daily new words and review words.
3. Learn a new word.
4. Confirm statistics count it as learned, not mastered.
5. Review spelling correctly.
6. Confirm mastered count increases.
7. Review spelling incorrectly on another word.
8. Confirm the word returns soon and weight decreases.
9. Restart app.
10. Confirm local Room state persists.

---

## Risks And Decisions

- The customer said "needs review means weight <= 5", but showing every such word every day can create too many reviews. Use `dailyReviewWords` as the cap and `nextReviewTime` as the due gate.
- Full FSRS is not recommended here because it needs review history and more scheduler state than the app currently has.
- Full SM-2 is also unnecessary because the customer already gave a simpler weight model. The implementation borrows the SRS idea of per-word state and due times, but keeps the customer's 0-6 weights.
- Server leaderboard currently reflects study activity, not mastered-word count. Leave it unchanged unless the customer specifically requests web-side mastered ranking.

---

## Implementation Order

1. Add `WordReviewPolicy` and unit tests.
2. Add `difficultyTag` and Room migration.
3. Update CSV import and repair existing imported words.
4. Update DAO review/mastery queries.
5. Update Learn screen spelling flow.
6. Verify statistics and local persistence.
7. Commit and push.

