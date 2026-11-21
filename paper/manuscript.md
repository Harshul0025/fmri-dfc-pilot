# Static and Dynamic Functional Connectivity and Working Memory: An Exploratory Pilot Study Using Human Connectome Project Data

*Authors: Vedansh, Vishesh, Vishal, Harshul*

> **How this file is built (P4 note — delete before submission).**
> Each person writes their part in `paper/sections/`. P4 copies the final text into the
> matching place below and keeps one consistent voice. Status of each part:
>
> | Section | Source | Status |
> |---|---|---|
> | Abstract | P4 | write last, after real results |
> | Introduction | P4 | ✅ draft below |
> | Methods – Data & preprocessing | `sections/methods_data.md` (P1) | ✅ copied in |
> | Methods – Static FC & network | `sections/static.md` (P2) | ⏳ waiting for Vishesh's PR |
> | Methods – Dynamic FC & states | `sections/dynamic.md` (P3) | ⏳ waiting for Vishal |
> | Methods – Behaviour & statistics | `sections/behaviour_stats.md` (P4) | ✅ copied in |
> | Results | P2, P3, P4 (`results/stats/associations.csv`) | ⏳ after real metrics |
> | Discussion | P4 | ⏳ outline below |
> | Limitations | P4 | ✅ draft below |

---

## Abstract

*[Write last. ~200 words: aim, data (N = 15 HCP young adults, one resting-state run, Schaefer-200), methods (static FC + graph metrics, sliding-window dynamic FC + k-means states, partial Spearman with working memory controlling for motion), main results with effect sizes and CIs, one-sentence cautious conclusion.]*

---

## 1. Introduction

The human brain is organised into large-scale networks whose regions show correlated activity even at rest. Resting-state functional magnetic resonance imaging (fMRI) measures this through *functional connectivity* (FC): the statistical dependence, usually the Pearson correlation, between the blood-oxygen-level-dependent (BOLD) signals of different regions (Biswal et al., 1995). Resting-state FC is organised into reproducible networks, such as the default-mode, frontoparietal control and dorsal attention networks (Yeo et al., 2011), and it varies between individuals in ways that are stable enough to identify a person and relate to cognitive ability (Finn et al., 2015; Smith et al., 2015).

Most studies compute *static* FC: one correlation matrix over the whole scan, which assumes that connectivity is constant over several minutes. Graph theory then summarises this matrix with measures such as node strength, clustering coefficient and global efficiency, which describe how segregated or integrated the network is (Bullmore & Sporns, 2009; Rubinov & Sporns, 2010). However, there is growing evidence that FC changes over seconds to minutes, even at rest (Chang & Glover, 2010; Hutchison et al., 2013). *Dynamic* (time-varying) FC is commonly estimated with a sliding-window approach: a short window is moved along the time series, and an FC matrix is computed in each window. Clustering these windowed matrices across participants reveals a small number of recurring connectivity patterns, or *brain states*, and each participant can then be described by how much time they spend in each state and how often they switch between states (Allen et al., 2014; Calhoun et al., 2014).

Dynamic FC has been linked to cognition. Moment-to-moment shifts between more segregated and more integrated network configurations track task performance (Shine et al., 2016), and the temporal organisation of brain-state switching is heritable and related to behaviour (Vidaurre et al., 2017). Reviews suggest that time-varying connectivity may capture cognitive information that static FC misses (Cohen, 2018). Working memory, the ability to hold and manipulate information over a few seconds (Baddeley, 2003), is a natural candidate because it relies on flexible interaction between frontoparietal, attention and default-mode networks (Cole et al., 2014).

At the same time, dynamic FC is methodologically sensitive. Window length, preprocessing and sampling variability can all create apparent fluctuations, and head motion can produce spurious connectivity changes and even spurious "states" (Leonardi & Van De Ville, 2015; Laumann et al., 2017; Lurie et al., 2020). Motion also biases static FC (Power et al., 2012), and the best denoising strategy, including whether to apply global signal regression, remains debated (Ciric et al., 2017; Murphy & Fox, 2017). Finally, brain–behaviour correlations in small samples are unstable and tend to overestimate effect sizes (Marek et al., 2022).

The Human Connectome Project (HCP) Young Adult dataset offers high-quality resting-state fMRI with high temporal resolution (TR = 0.72 s), standardised preprocessing and matched cognitive scores, including NIH Toolbox measures of working memory (Van Essen et al., 2013; Glasser et al., 2013; Barch et al., 2013). This makes it well suited for building and testing an analysis pipeline before scaling up.

In this exploratory pilot study, we used resting-state fMRI from 15 HCP participants to (i) estimate static FC and graph-theoretical network measures; (ii) estimate dynamic FC with sliding windows and identify recurring brain states with k-means clustering; (iii) compare static and dynamic descriptions of the same data; and (iv) explore whether static and dynamic measures are associated with working-memory performance, while controlling for head motion. Because of the small sample, our goal is not to establish reliable brain–behaviour relationships but to build a reproducible, laptop-friendly pipeline, describe the patterns it produces, and report effect sizes with honest uncertainty to inform a larger follow-up study.

---

## 2. Methods

### 2.1 Data and Preprocessing

**Dataset.** We used resting-state fMRI data from the Human Connectome Project (HCP) Young Adult S1200 release (Van Essen et al., 2013). Fifteen healthy young adults were selected from the HCP "unrelated" subset with a complete resting-state session and a non-missing working-memory score. Data were accessed under the HCP Open Access Data Use Terms.

**Imaging data.** For each participant we used one resting-state run (`rfMRI_REST1_LR`; 1,200 volumes, TR = 0.72 s, ≈14.4 min, 2 mm isotropic, 3T Siemens Skyra with multiband factor 8) from the 2017 S1200 release on the HCP Amazon S3 bucket. We used the minimally preprocessed, ICA-FIX denoised data in CIFTI grayordinate space (`*_Atlas_hp2000_clean.dtseries.nii`; Glasser et al., 2013; Salimi-Khorshidi et al., 2014), which includes motion correction, MSMSulc surface registration to the fs_LR 32k mesh, high-pass filtering (2000 s FWHM) and removal of noise components.

**Parcellation and signal extraction.** The cortex was divided into 200 regions using the Schaefer 2018 parcellation (7-network order, fs_LR 32k CIFTI version; Schaefer et al., 2018). For each region, the mean signal over its cortical vertices was computed (nibabel 5.4.2) and z-scored over time, giving a 1,200 × 200 time-series matrix per participant.

**Quality control.** Participants were excluded if (i) mean relative head motion (HCP `Movement_RelativeRMS_mean`) exceeded 0.2 mm, (ii) fewer than 1,100 volumes were available, or (iii) any region had a missing or constant signal. Carpet plots of every participant were visually inspected. No participant met an exclusion criterion, leaving **N = 15** for analysis (mean relative motion = 0.089 ± 0.028 mm, range 0.060–0.165 mm). As a sanity check, mean functional connectivity within Yeo networks exceeded that between networks in every participant.

**Motion and global signal.** Because residual head motion can inflate connectivity across the whole brain, we computed QC-FC correlations (the across-subject correlation between mean motion and each edge's Fisher-z FC). Without further denoising, 55% of edges were nominally motion-related (|r| > 0.51, p < .05), and mean FC correlated with motion (Spearman ρ = 0.65, p = 0.01). After regressing the global cortical signal (mean over all 200 parcels) out of each parcel time series, this fell to 13% of edges. The association between network segregation (within- minus between-network FC) and motion disappeared (ρ = −0.63 → 0.15). Global signal regression was therefore used for the primary analyses; results without it are reported as a sensitivity analysis, and mean motion was included as a covariate in the brain–behaviour analyses.

**Reproducibility.** Subject IDs, run, atlas, QC thresholds and software versions are recorded in the project repository (`config.yaml`, `src/p1_data/candidates.txt`, `requirements.txt`).

### 2.2 Static Functional Connectivity and Network Analysis

*[Copy from `paper/sections/static.md` (P2, Vishesh) when merged. Must include: Pearson FC → Fisher z, proportional threshold 15% (positive weights), graph metrics and software (networkx/bctpy + version), density sensitivity 10/20/30% with rank-stability result.]*

### 2.3 Dynamic Functional Connectivity and Brain States

*[Copy from `paper/sections/dynamic.md` (P3, Vishal). Must include: window 60 TR (43.2 s), step 5 TR, taper type, number of windows, k-means settings (n_init, seed), how K was chosen (elbow + silhouette), definition of fractional occupancy / dwell time / transitions, robustness to 40 and 90 TR windows.]*

### 2.4 Behavioural Measure and Statistical Analysis

**Working-memory measure.** Working memory was indexed by the NIH Toolbox List Sorting Working Memory Test (unadjusted scale score, HCP variable `ListSort_Unadj`; Tulsky et al., 2013), taken from the HCP unrestricted behavioural data. In this test, participants see and hear a sequence of pictures and must recall them in order of size, first within one category and then across two categories. We chose this measure over in-scanner 2-back accuracy (`WM_Task_2bk_Acc`) for three reasons: (i) it is a validated, standardised test; (ii) it is collected outside the scanner, so it is independent of the fMRI session analysed; and (iii) it is available for nearly all HCP participants. Age bracket and sex were taken from the same file.

**Brain–behaviour associations.** We tested each static metric (mean FC, mean node strength, mean clustering coefficient, global efficiency) and each dynamic metric (FC variability, number of state transitions, and the fractional occupancy and mean dwell time of every brain state) for association with working memory. Metrics that were identical across participants by construction (graph density after proportional thresholding) were not tested. Because head motion can bias connectivity estimates even after denoising (Power et al., 2012; Ciric et al., 2017), the primary test was a **partial Spearman correlation** between each metric and the working-memory score, controlling for mean relative head motion (mean FD). Spearman rather than Pearson correlation was used as the primary test because, with N = 15, a single extreme participant can dominate a Pearson correlation. Plain Spearman and Pearson correlations are reported as secondary results. Uncertainty was estimated with a percentile bootstrap (5,000 resamples of participants) giving a 95% confidence interval for each partial correlation. To account for testing many metrics, p-values from the primary test were corrected with the Benjamini–Hochberg false discovery rate (FDR) procedure (Benjamini & Hochberg, 1995); we report both uncorrected p and FDR-adjusted q.

**Motion check.** To check whether motion could explain any association, we also correlated mean FD with the working-memory score and with each connectivity metric (Spearman).

**Software.** Analyses used Python with NumPy, pandas, SciPy (`scipy.stats`) and Matplotlib. The full analysis runs with one command (`python src/p4_behaviour/associations.py`).

**Interpretation.** Given the small sample, all associations are treated as exploratory and descriptive. With N = 15, only correlations of about |ρ| > 0.5 reach nominal significance, and confidence intervals are wide; we therefore emphasise effect sizes and intervals over p-values (Marek et al., 2022).

---

## 3. Results

### 3.1 Sample

*[Table 1 from `results/stats/descriptives.csv`: N, sex, age groups, WM mean ± SD, mean FD.]*

### 3.2 Static functional connectivity and network structure

*[From P2: group FC matrix figure sorted by Yeo network, within- vs between-network FC, graph metric values (mean ± SD), density-sensitivity result.]*

### 3.3 Dynamic functional connectivity and brain states

*[From P3: chosen K and why, centroid figure, fractional occupancy bar plot, dwell times, transitions, robustness to window length, state fraction vs motion.]*

### 3.4 Associations with working memory

*[From `results/stats/associations.csv` + `results/stats/figures/scatter_grid.png`. Report for each metric: partial ρ [95% CI], p, q. Say how many survive FDR. Report motion check from `motion_check.csv`. Mention GSR-off sensitivity if P2/P3 provide no-GSR metrics.]*

---

## 4. Discussion

*[Outline — write after real results:]*
1. Summary of what we found, in one paragraph, using "exploratory association".
2. Static FC: does the network structure look as expected (strong within-network FC, Yeo networks visible)? This validates the pipeline.
3. Dynamic FC: did we find recurring states? Do they resemble states reported before (e.g. Allen et al., 2014: one frequent, weakly connected state and less frequent, strongly connected states)?
4. Behaviour: compare effect sizes with the literature; stress wide CIs; say whether anything survived FDR. If nothing did, say clearly that this is expected at N = 15 and is not evidence of no effect.
5. Static vs dynamic: did dynamic metrics add anything beyond static ones?
6. What the pipeline makes possible next (scale to more HCP subjects, both runs, both phase-encoding directions).

---

## 5. Limitations

- **Small sample.** With 15 participants, the study can test the workflow but cannot support definitive hypothesis testing. Brain–behaviour correlations at this size are unstable and tend to overestimate true effects (Marek et al., 2022), and confidence intervals are wide. All results are exploratory associations, not predictions.
- **One short run per participant.** We used a single 14.4-minute run (`REST1_LR`). Dynamic FC estimates, especially state dwell times and transition counts, become more reliable with more data (Laumann et al., 2017).
- **Methodological choices in dynamic FC.** Window length, step, taper and the number of states (K) all affect the results, and sliding-window FC can show fluctuations even when the true connectivity is constant (Leonardi & Van De Ville, 2015; Lurie et al., 2020). We tested robustness to window length, but the states should be seen as a description of this sample, not as fixed brain properties.
- **Head motion and global signal regression.** Motion is a known confound for both static and dynamic FC (Power et al., 2012). We applied global signal regression and controlled for mean motion, but GSR is itself debated because it can shift correlations towards negative values (Murphy & Fox, 2017). Results without GSR are reported as a sensitivity analysis.
- **Cortex only.** The Schaefer parcellation covers cortex only; subcortical and cerebellar regions, which also contribute to working memory, were not included.
- **One cognitive measure.** We used a single working-memory score measured on a different day from the scan. Other cognitive domains were not examined.
- **Homogeneous sample.** HCP participants are healthy young adults (22–35 years), so findings do not generalise to other ages or clinical groups, and no clinical claims are made.

**Future work.** Increase the sample size (hundreds of HCP participants), use all four resting-state runs, validate on an independent dataset, and only then consider more complex models such as graph neural networks or sequence models.

---

## References

*(P4 note: check every entry against the DOI/journal page before submission.)*

1. Allen, E. A., Damaraju, E., Plis, S. M., Erhardt, E. B., Eichele, T., & Calhoun, V. D. (2014). Tracking whole-brain connectivity dynamics in the resting state. *Cerebral Cortex, 24*(3), 663–676.
2. Baddeley, A. (2003). Working memory: Looking back and looking forward. *Nature Reviews Neuroscience, 4*(10), 829–839.
3. Barch, D. M., Burgess, G. C., Harms, M. P., Petersen, S. E., Schlaggar, B. L., Corbetta, M., et al. (2013). Function in the human connectome: Task-fMRI and individual differences in behavior. *NeuroImage, 80*, 169–189.
4. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B, 57*(1), 289–300.
5. Biswal, B., Yetkin, F. Z., Haughton, V. M., & Hyde, J. S. (1995). Functional connectivity in the motor cortex of resting human brain using echo-planar MRI. *Magnetic Resonance in Medicine, 34*(4), 537–541.
6. Bullmore, E., & Sporns, O. (2009). Complex brain networks: Graph theoretical analysis of structural and functional systems. *Nature Reviews Neuroscience, 10*(3), 186–198.
7. Calhoun, V. D., Miller, R., Pearlson, G., & Adalı, T. (2014). The chronnectome: Time-varying connectivity networks as the next frontier in fMRI data discovery. *Neuron, 84*(2), 262–274.
8. Chang, C., & Glover, G. H. (2010). Time–frequency dynamics of resting-state brain connectivity measured with fMRI. *NeuroImage, 50*(1), 81–98.
9. Ciric, R., Wolf, D. H., Power, J. D., Roalf, D. R., Baum, G. L., Ruparel, K., et al. (2017). Benchmarking of participant-level confound regression strategies for the control of motion artifact in studies of functional connectivity. *NeuroImage, 154*, 174–187.
10. Cohen, J. R. (2018). The behavioral and cognitive relevance of time-varying, dynamic changes in functional connectivity. *NeuroImage, 180*, 515–525.
11. Cole, M. W., Bassett, D. S., Power, J. D., Braver, T. S., & Petersen, S. E. (2014). Intrinsic and task-evoked network architectures of the human brain. *Neuron, 83*(1), 238–251.
12. Finn, E. S., Shen, X., Scheinost, D., Rosenberg, M. D., Huang, J., Chun, M. M., Papademetris, X., & Constable, R. T. (2015). Functional connectome fingerprinting: Identifying individuals using patterns of brain connectivity. *Nature Neuroscience, 18*(11), 1664–1671.
13. Glasser, M. F., Sotiropoulos, S. N., Wilson, J. A., Coalson, T. S., Fischl, B., Andersson, J. L., et al. (2013). The minimal preprocessing pipelines for the Human Connectome Project. *NeuroImage, 80*, 105–124.
14. Hutchison, R. M., Womelsdorf, T., Allen, E. A., Bandettini, P. A., Calhoun, V. D., Corbetta, M., et al. (2013). Dynamic functional connectivity: Promise, issues, and interpretations. *NeuroImage, 80*, 360–378.
15. Laumann, T. O., Snyder, A. Z., Mitra, A., Gordon, E. M., Gratton, C., Adeyemo, B., et al. (2017). On the stability of BOLD fMRI correlations. *Cerebral Cortex, 27*(10), 4719–4732.
16. Leonardi, N., & Van De Ville, D. (2015). On spurious and real fluctuations of dynamic functional connectivity during rest. *NeuroImage, 104*, 430–436.
17. Lurie, D. J., Kessler, D., Bassett, D. S., Betzel, R. F., Breakspear, M., Keilholz, S., et al. (2020). Questions and controversies in the study of time-varying functional connectivity in resting fMRI. *Network Neuroscience, 4*(1), 30–69.
18. Marek, S., Tervo-Clemmens, B., Calabro, F. J., Montez, D. F., Kay, B. P., Hatoum, A. S., et al. (2022). Reproducible brain-wide association studies require thousands of individuals. *Nature, 603*(7902), 654–660.
19. Murphy, K., & Fox, M. D. (2017). Towards a consensus regarding global signal regression for resting state functional connectivity MRI. *NeuroImage, 154*, 169–173.
20. Power, J. D., Barnes, K. A., Snyder, A. Z., Schlaggar, B. L., & Petersen, S. E. (2012). Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. *NeuroImage, 59*(3), 2142–2154.
21. Rubinov, M., & Sporns, O. (2010). Complex network measures of brain connectivity: Uses and interpretations. *NeuroImage, 52*(3), 1059–1069.
22. Salimi-Khorshidi, G., Douaud, G., Beckmann, C. F., Glasser, M. F., Griffanti, L., & Smith, S. M. (2014). Automatic denoising of functional MRI data: Combining independent component analysis and hierarchical fusion of classifiers. *NeuroImage, 90*, 449–468.
23. Schaefer, A., Kong, R., Gordon, E. M., Laumann, T. O., Zuo, X.-N., Holmes, A. J., Eickhoff, S. B., & Yeo, B. T. T. (2018). Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. *Cerebral Cortex, 28*(9), 3095–3114.
24. Shine, J. M., Bissett, P. G., Bell, P. T., Koyejo, O., Balsters, J. H., Gorgolewski, K. J., Moodie, C. A., & Poldrack, R. A. (2016). The dynamics of functional brain networks: Integrated network states during cognitive task performance. *Neuron, 92*(2), 544–554.
25. Smith, S. M., Nichols, T. E., Vidaurre, D., Winkler, A. M., Behrens, T. E. J., Glasser, M. F., et al. (2015). A positive-negative mode of population covariation links brain connectivity, demographics and behavior. *Nature Neuroscience, 18*(11), 1565–1567.
26. Tulsky, D. S., Carlozzi, N. E., Chevalier, N., Espy, K. A., Beaumont, J. L., & Mungas, D. (2013). V. NIH Toolbox Cognition Battery (CB): Measuring working memory. *Monographs of the Society for Research in Child Development, 78*(4), 70–87.
27. Van Essen, D. C., Smith, S. M., Barch, D. M., Behrens, T. E. J., Yacoub, E., & Ugurbil, K. (2013). The WU-Minn Human Connectome Project: An overview. *NeuroImage, 80*, 62–79.
28. Vidaurre, D., Smith, S. M., & Woolrich, M. W. (2017). Brain network dynamics are hierarchically organized in time. *Proceedings of the National Academy of Sciences, 114*(48), 12827–12832.
29. Yeo, B. T. T., Krienen, F. M., Sepulcre, J., Sabuncu, M. R., Lichtenstein, J. L., Hollinshead, M., et al. (2011). The organization of the human cerebral cortex estimated by intrinsic functional connectivity. *Journal of Neurophysiology, 106*(3), 1125–1165.
