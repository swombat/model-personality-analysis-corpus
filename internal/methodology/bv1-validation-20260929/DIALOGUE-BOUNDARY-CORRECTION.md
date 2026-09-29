# Whole direct-speech sentence boundary correction — 2026-09-29

Mira reviewed GPT-6.1 Sol `LONG_18` after all four allowed BV1 evaluations
failed `quote_sentence_boundary`. This is a validator implementation correction
within Daniel's authorized validation work, not permission for more inference.

The exact source is:

> Mara could have recited the department’s official answer. Instead, she said, “Sometimes keeping something safe gives a person enough time to know what they want to do with it.”

All four preserved evaluations chose exactly the complete utterance inside the
speech marks, ending in its original period. The original boundary heuristic
strips opening speech marks but then rejects the preceding attribution comma.
It already accepts sentence text without its enclosing quotation marks at other
boundaries. Treating this complete utterance as a sentence is consistent with
that existing interpretation: the surrounding narrative attribution is not part
of the character's spoken sentence.

The additional gate requires a capitalized exact substring, terminal sentence
punctuation, an immediately preceding opening speech mark after comma+whitespace,
and a matching closing mark immediately afterward, followed by whitespace or EOF.
It does not accept a comma alone, mismatched marks, a substring within an
utterance, or an added quote. All old gates and exact-byte checks remain.
This conservative rule does not try to solve general sentence segmentation.
Capitalization and punctuation remain heuristics, not grammatical proof.

Offline evidence before changing production: ten focused positive/negative
fixtures passed; none of 232 existing successful Luna outputs changed result;
all four preserved LONG_18 responses became valid under the proposed rule.
The expanded committed regression suite contains 20 tests (eight new tests).
The original validator snapshot and offline report remain in the raw run's
`preflight/` directory. Record the code hashes in the recovery receipt.

Recovery must select the **earliest preserved response**, not whichever reading
is most attractive. Revalidate source hash, model, provider, finish reason,
all headings and quote fidelity. Keep all four original failed attempt records
unchanged. Bind the preserved output and use one separately recorded local
revalidation repair, with provider credentials removed, never another API call.
Original queue attempts remain 4/4; the intervention is visible, not rewritten
as unattended success.

I read the complete source and earliest evaluation. Its fiction classification,
main interpretation and selected evidence are supported. One minor detail is
inaccurate: the evaluation calls the lift squeaky, while the source gives the
squeak to Mr. Vale's shoes. This is retained rather than silently editing an
evaluator output. Structural QA is not a guarantee of semantic perfection.

Prompts, evaluator, reasoning policy, token allowance, taxonomy, raw samples and
consensus thresholds are unchanged. Future release notes must disclose both the
boundary correction and the preserved-output recovery.
