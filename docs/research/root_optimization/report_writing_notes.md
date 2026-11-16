# Report update notes

Nature-writing route: manuscript / research / method, experiments and discussion / English / generic. Terms retained: chord accuracy, root accuracy, fundamental-only NNLS, direct projection, isolated chords. The existing project title and vocabulary remain unchanged.

| Evidence | Role | Placement |
| --- | --- | --- |
| Original GuitarSet comparison | Original project result | Table 1 and §4.2, unchanged |
| Failed 4,096/8,192 transfer to IDMT subset 4 | Qualification of fusion | §4.3; both accuracies and coverage retained |
| Fundamental-only NNLS and direct projection on development data | Main new finding | Equation 2, §4.4 and Table 2 |
| Worse harmonic-profile variants | Qualification of mechanism | §4.4, with both adverse scores |
| Three-way 100% isolated-chord result | Boundary of the new evidence | §4.4 and Table 2; full inference costs retained |
| NNLS numerical checks, source hashes and tuning records | Reproducibility | Repository experiment records |

The shortest argument is: fusion did not improve the frozen comparisons; root errors motivated note profiles; direct projection retained most of the development gain; the isolated-chord test reached a ceiling and therefore leaves the progression-level question open. Discussion interprets that sequence instead of repeating the table.

The former subset-4 table was replaced by one root-study table. Introductory and related-work prose was compressed, preserving every citation. Approximate source-token counts excluding numbers: Introduction 98→81, Related Work 233→169, follow-up narrative 200→227. The additional root-method equation and table fit within four A4 pages by removing repeated descriptions rather than changing template dimensions or type size. Both existing figures remain. Only ordinary underfull-box warnings remain in the LaTeX log.

The previous exact test-count sentence was replaced with the tested capabilities, because the parent task is still integrating new checks. No unverified count was inserted. The advanced PI items remain open. The expected final objective now follows the unresolved evidence: test note features on new recordings with chord changes.

Data checks: 119 development recordings; 88 isolated clips grouped as 44 paired fingering settings; 202.725/220s scoreable (92.15%); all isolated decoded chord/root scores100%; runtimes1.29/6.04/1.86s. Complete validation is in `report_validation.json`.

Final wording correction after the draft build: Discussion explicitly compares both harmonic variants with fundamental-only fitting, since decay0.6 still exceeds the original STFT baseline. The NC statistic is identified as duration-weighted. The parent task will rebuild the integrated report.
