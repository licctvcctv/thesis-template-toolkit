# Mixed Review Learning Design

## Research Notes

- Anki deck options support mixing new cards with reviews, and warn that new cards temporarily increase review load. The manual also recommends stopping new cards when the overdue review backlog is already large.
- Anki FSRS uses desired retention as the main workload dial. Its default `0.90` is described as a good balance; higher retention sharply increases daily reviews.
- SuperMemo similarly schedules repetitions around the point where recall probability drops toward 90%, and brings difficult or forgotten items closer together.

Sources:

- https://docs.ankiweb.net/deck-options
- https://www.supermemo.com/en/faq/how-often-should-the-material-be-repeated
- https://www.super-memory.com/english/ol/sm2.htm

## Decision

Do not replace the current 0-6 weight model with full SM-2 or FSRS. The app has only `familiarity`, `nextReviewTime`, and `reviewCount`, and it does not store enough review history for FSRS parameter optimization. Keep the lightweight scheduler and improve the daily queue behavior.

The Learn screen should be a two-phase queue:

- Due review words are still selected first by `familiarity ASC, nextReviewTime ASC, difficultyTag DESC`.
- New words are still picked from the selected book with the existing stable daily random picker.
- The final daily plan shows all new words first, then enters a review phase and shows due review words.

## Phase Order

Use a simple phase order instead of interleaving:

- If both new words and due reviews exist, order them as `all new words -> all due review words`.
- When the first review word appears, show a one-time "进入复习环节" prompt.
- If either side is empty, show the other side normally.

This keeps the behavior explainable to the student and avoids the "learn a few, review one or two" flow that felt too close to Baicizhan-style interleaving.

## Existing Daily Plan Refresh

The existing daily plan is no longer treated as frozen for the whole day.

- When the Learn screen loads, due review words already in today's plan are reopened by setting `learned = 0`.
- Due review words missing from today's plan are appended.
- The pending part of the plan is re-sorted with the same new-then-review phase policy.
- After each answer or skip, the current plan checks due words again, so words that become due during the same study session can re-enter the queue.

## Acceptance

- A first-day learner can see previously learned due words after completing the new-word phase.
- A word marked difficult with a short review delay can reappear later in the same session after it becomes due.
- Existing completed, non-due words stay completed.
- The app clearly prompts before entering the review phase.
- Unit tests cover the queue ordering and existing-plan refresh policy.
