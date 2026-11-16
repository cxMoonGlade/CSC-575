Nature axes: manuscript / methods / experiments / en / generic.

Canonical labels: Note projection; Note NNLS; Long STFT; development example. The player introduces its development status before displaying labels. The CLI summary records the input and configuration fingerprints, the full configuration, separate warm-up time and audio-to-interval time. It makes no new accuracy or runtime comparison claim.

The preidentified example is `01_Funk1-97-C_comp`. Its saved long-window baseline is shown beside the new prediction; neither display nor reference scoring affects inference. The source WAV is embedded unchanged with GuitarSet attribution. Reference intervals are clipped to audio duration, including the approximately 10-microsecond rounded final endpoint.

Six new tests passed. They cover actual CLI output equivalence for both frozen methods, existing-output preservation, player scope, an inconsistent projection configuration and rounded annotation endpoints. Chromium loaded three tracks, played and stopped a selected interval, sought to five seconds and reported no JavaScript errors.

The CLI player uses the shorter labels Note projection and Note NNLS so track names fit beside the timeline. Method identifiers and configuration values are unchanged. The example was redrawn from saved intervals without rerunning recognition.
