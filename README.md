# Multi-resolution chord recognition from audio

CSC475 design specification  
Christopher Xu | Solo project  
October 23 to December 3, 2026

## Project description

I will build an offline program that identifies chords in a recording and displays them on a playable timeline. It will support twelve major and twelve minor chords, plus a no-chord label (`N`).

The project asks whether combining short and long analysis windows improves chord recognition near chord changes. Long windows provide finer frequency resolution but can mix sounds from adjacent chords. Short windows localize changes more closely but provide less frequency detail [3]. I will compare a simple adaptive combination with single-resolution features and fixed combinations.

This project applies the course topics of Fourier analysis, audio feature extraction, chord detection, and MIR evaluation.

## Data and tools

I will aim for 20 Beatles recordings from my collection with matching Isophonics annotations [15], checking recording versions and timing before selecting ten development songs and ten test songs. Excerpts and versions of the same song will stay together. All parameter choices will use the development set.

The implementation will use Python, NumPy/SciPy, librosa [13], SoundFile, and mir_eval [14]. A Jupyter notebook will provide playback, chord plots, and CSV export. Public dataset and software links are listed in [docs/resources.md](docs/resources.md).

## Method

Audio will be converted to mono at 22,050 Hz. I will start with Hann windows of 2,048 and 8,192 samples and a shared hop of 512 samples. All front ends will share a tuning estimate, pitch range, frame centres, pitch-class order, and per-frame L2 normalization.

For short-window chroma $x_s(t)$ and long-window chroma $x_l(t)$, the combined feature is

$$
x(t)=w(t)x_s(t)+(1-w(t))x_l(t), \qquad 0\leq w(t)\leq1.
$$

The proposed weight will increase near peaks in short-window chroma change and decrease in stable passages. Its neighbourhood will extend on both sides of a peak to account for the long window's duration. The threshold and neighbourhood width will be selected on development songs.

Cosine similarity to major/minor templates will produce chord scores. All methods will share an energy-based `N` rule and a Viterbi decoder with a common chord-switch penalty, selected across methods on the development set. Consecutive identical labels will become timed chord intervals.

| Front end | Comparison |
|---|---|
| Single-window STFT | Best window selected on development songs |
| CQT chroma | Alternative time-frequency representation |
| Fixed fusion | Equal weighting and a development-selected constant weight |
| Adaptive fusion | Weight varies around detected changes |

## Evaluation

I will compare duration accuracy (correctly labelled time divided by scoreable time) and chord-change precision, recall, and F1, using one-to-one boundary matching within 100 ms. Matched-boundary timing errors and per-song results will show where each method helps or fails. Results before temporal decoding will help separate feature effects from smoothing.

Reference labels will be reduced to supported major/minor triads, with `N` retained. Unsupported labels and annotation gaps will be excluded and their duration reported. Boundaries will be extracted after merging equivalent labels, without adding transitions at excluded intervals. All predictions will cover the same verified annotation spans.

Experiments will also measure complete audio-to-label runtime with feature caches disabled. The first development experiments will check whether the two windows provide useful complementary evidence. The main risk is that melody or percussion changes trigger short-window weighting without a chord change.

## Related work

McVicar et al. [1] and Pauwels et al. [2] review chord-recognition features, classifiers, and temporal models. Khadkevich and Omologo [3] study reassigned spectra and window length, providing a starting point for the time-frequency question here.

Chroma design also affects which sounds contribute to a prediction. Müller et al. [4] study timbre robustness for audio matching; Mauch and Dixon [5] use a harmonic dictionary and non-negative least squares; Ueda et al. [6] refine acoustic features using harmonic/percussive separation. Learned representations [7, 8] offer another approach, with different targets for chord-related chroma and score-derived pitch classes.

Joint chord/downbeat estimation [9] and duration modelling [10] show the role of temporal context. Humphrey and Bello [11] and Koops et al. [12] discuss vocabulary and annotation differences, which inform the evaluation scope.

## Timeline

| Week | Objective |
|---|---|
| 1: Oct. 23-29 | Verify songs and split; build the single-window baseline and initial window comparisons. |
| 2: Oct. 30-Nov. 5 | Add CQT and fixed fusion; implement adaptive weighting. |
| 3: Nov. 6-12 | Complete decoding and evaluation; write the progress report. |
| 4: Nov. 13-19 | Finish the playback notebook and freeze settings on development data. |
| 5: Nov. 20-26 | Run test comparisons, timing measurements, and error analysis. |
| 6: Nov. 27-Dec. 3 | Finish the README, ISMIR LaTeX report, and demonstration. |

These are working dates; course submission deadlines remain to be confirmed.

## Christopher Xu

I will handle the audio pipeline, fusion method, evaluation, and report.

- Objective 1: Build a functional multi-resolution chord recognizer.
  - PI1 (basic): Load aligned audio and annotations and produce single-window chord predictions.
  - PI2 (basic): Extract aligned short-window, long-window, and CQT chroma.
  - PI3 (expected): Implement fixed and adaptive fusion with the shared decoder.
  - PI4 (expected): Provide playback, a chord timeline, and timestamped CSV export.
  - PI5 (advanced): Compare reassigned chroma with the main front ends.

- Objective 2: Evaluate the recognition methods and explain their differences.
  - PI1 (basic): Save the song split, settings, and software versions.
  - PI2 (basic): Calculate duration accuracy, annotation coverage, and boundary metrics.
  - PI3 (expected): Compare test results and full runtime by song, with examples of improved and worsened predictions.
  - PI4 (expected): Complete the related work, results, and discussion in the README and final report.
  - PI5 (advanced): Estimate uncertainty by bootstrapping whole test songs.

## References

Full BibTeX entries are in [references.bib](references.bib).

[1] M. McVicar, R. Santos-Rodríguez, Y. Ni, and T. De Bie. "Automatic Chord Estimation from Audio: A Review of the State of the Art." *IEEE/ACM TASLP* 22(2), 556-575, 2014. [DOI](https://doi.org/10.1109/TASLP.2013.2294580).

[2] J. Pauwels, K. O'Hanlon, E. Gómez, and M. B. Sandler. "20 Years of Automatic Chord Recognition from Audio." *ISMIR*, 54-63, 2019. [DOI](https://doi.org/10.5281/zenodo.3527739).

[3] M. Khadkevich and M. Omologo. "Reassigned Spectrum-Based Feature Extraction for GMM-Based Automatic Chord Recognition." *EURASIP Journal on Audio, Speech, and Music Processing* 2013, article 15, 2013. [DOI](https://doi.org/10.1186/1687-4722-2013-15).

[4] M. Müller, S. Ewert, and S. Kreuzer. "Making Chroma Features More Robust to Timbre Changes." *ICASSP*, 1877-1880, 2009. [DOI](https://doi.org/10.1109/ICASSP.2009.4959974).

[5] M. Mauch and S. Dixon. "Approximate Note Transcription for the Improved Identification of Difficult Chords." *ISMIR*, 135-140, 2010. [Paper](https://webspace.eecs.qmul.ac.uk/s.e.dixon/pub/2010/Mauch-Dixon-ISMIR-2010.pdf).

[6] Y. Ueda, Y. Uchiyama, T. Nishimoto, N. Ono, and S. Sagayama. "HMM-Based Approach for Automatic Chord Detection Using Refined Acoustic Features." *ICASSP*, 5518-5521, 2010. [DOI](https://doi.org/10.1109/ICASSP.2010.5495218).

[7] F. Korzeniowski and G. Widmer. "Feature Learning for Chord Recognition: The Deep Chroma Extractor." *ISMIR*, 37-43, 2016. [Paper](https://arxiv.org/abs/1612.05065).

[8] C. Weiß, J. Zeitler, T. Zunner, F. Schuberth, and M. Müller. "Learning Pitch-Class Representations from Score-Audio Pairs of Classical Music." *ISMIR*, 746-753, 2021. [DOI](https://doi.org/10.5281/zenodo.5624549).

[9] H. Papadopoulos and G. Peeters. "Joint Estimation of Chords and Downbeats From an Audio Signal." *IEEE TASLP* 19(1), 138-152, 2011. [DOI](https://doi.org/10.1109/TASL.2010.2045236).

[10] F. Korzeniowski and G. Widmer. "Improved Chord Recognition by Combining Duration and Harmonic Language Models." *ISMIR*, 10-17, 2018. [Paper](https://archives.ismir.net/ismir2018/paper/000300.pdf).

[11] E. J. Humphrey and J. P. Bello. "Four Timely Insights on Automatic Chord Estimation." *ISMIR*, 673-679, 2015. [Paper](https://archives.ismir.net/ismir2015/paper/000294.pdf).

[12] H. V. Koops, W. B. de Haas, J. A. Burgoyne, J. Bransen, A. Kent-Muller, and A. Volk. "Annotator Subjectivity in Harmony Annotations of Popular Music." *Journal of New Music Research* 48(3), 232-252, 2019. [DOI](https://doi.org/10.1080/09298215.2019.1613436).

[13] B. McFee, C. Raffel, D. Liang, D. P. W. Ellis, M. McVicar, E. Battenberg, and O. Nieto. "librosa: Audio and Music Signal Analysis in Python." *Proceedings of the 14th Python in Science Conference*, 18-24, 2015. [DOI](https://doi.org/10.25080/Majora-7b98e3ed-003).

[14] C. Raffel, B. McFee, E. J. Humphrey, J. Salamon, O. Nieto, D. Liang, and D. P. W. Ellis. "mir_eval: A Transparent Implementation of Common MIR Metrics." *ISMIR*, 367-372, 2014. [Paper](https://www.justinsalamon.com/uploads/4/3/9/4/4394963/raffel_mir_eval_ismir2014.pdf).

[15] Isophonics. "Reference Annotations: The Beatles." Dataset documentation. [Resource](https://isophonics.net/content/reference-annotations-beatles). Accessed October 23, 2026.
