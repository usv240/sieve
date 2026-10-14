# Benchmark B, version 2: pre-registration

Written and committed before any version 2 run. The git timestamp of this file precedes `eval/results/bench_b_v2.json`.

## Why a version 2

Version 1 took the first 20 openFDA MAUDE records for two brands. On 2026-10-14 a blind judge found that none of Sieve's hypotheses matched the manufacturer's finding in any of those 20. Two causes:

1. Selection. Of 335 records with a manufacturer narrative, 56 are paperwork corrections, 46 say the device was never returned and several say no fault was found. Version 1 counted all of these as misses.
2. Coverage. Fires, burnt cords and connectors, and internal heat damage are the most common real findings, and Sieve's fault list had no electrical or thermal faults. Five faults were added on 2026-10-15: power-cord-thermal, internal-overheat, external-ignition-fire, oxygen-sensor-fault and control-board-fault. Their text comes from the WHO specification and the indexed service manuals, not from MAUDE narratives.

Version 1 is kept in the history and in this note. It is not deleted or hidden.

## Selection rule (fixed)

Source: `data/external/maude_oxygen_concentrator_malfunctions.json`, 647 openFDA MAUDE records, CC0.

A record is included if and only if all three hold:

1. It has both an event description and a manufacturer narrative.
2. Sieve's registry matches its brand, manufacturer and model number to a device with confidence at least 0.8. Portable units Sieve does not cover, mostly Inogen, are out of scope.
3. The manufacturer narrative names a finding. A record is excluded if the narrative matches the exclusion pattern in `packages/eval/sieve_eval/bench_b.py`: paperwork corrections, device not returned or discarded, no fault found, or could not duplicate or determine.

Every qualifying record is used, ordered by MDR report key. A dry count on 2026-10-15 gave 74 records.

## Systems

- **Sieve**: the full pipeline with retrieval over the indexed manuals, Nemotron 3 Super synthesis, the citation verifier and the rules engine. The Ultra audit is off to bound cost; it does not change hypotheses.
- **Baseline**: Nemotron 3 Nano zero-shot. It gets the same complaint text, the same device name and the same list of allowed fault names, and picks up to three. It gets no manual pages.

Both systems name faults from the same list, so the judge sees the same format from both.

## Scoring

- Primary judge: Nemotron 3 Super, blind to which system produced the candidates. It answers YES if any candidate names the same failing component or failure mode as the manufacturer's finding. Synonyms count. If the manufacturer blames an outside cause such as smoking or an open flame, only a candidate naming that outside cause counts.
- Second judge: DeepSeek-V4.1-Flash on Token Factory, same prompt, to show this is not only Nemotron grading Nemotron. Cohen's kappa between the judges is reported per system.
- Safety check: for every record whose event description describes smoke, fire, burning, sparks or heat, the share where Sieve shows the remove-from-service stop. This holds by construction through the rules engine, so it is a regression check, not a model score.
- Cost is read from the ledger.

## What is reported whatever the outcome

Agreement for both systems under both judges, kappa, the safety check, the number of records, and every row with its MDR key so anyone can check it against openFDA.
