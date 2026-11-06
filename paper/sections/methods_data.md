## Data and Preprocessing

**Dataset.** We used resting-state fMRI data from the Human Connectome Project (HCP) Young Adult S1200 release (Van Essen et al., 2013). Fifteen healthy young adults were selected from the HCP "unrelated" subset with a complete resting-state session and a non-missing working-memory score. Data were accessed under the HCP Open Access Data Use Terms.

**Imaging data.** For each participant we used one resting-state run (`rfMRI_REST1_LR`; 1,200 volumes, TR = 0.72 s, ≈14.4 min, 2 mm isotropic, 3T Siemens Skyra with multiband factor 8) from the 2017 S1200 release on the HCP Amazon S3 bucket. We used the minimally preprocessed, ICA-FIX denoised data in CIFTI grayordinate space (`*_Atlas_hp2000_clean.dtseries.nii`; Glasser et al., 2013; Salimi-Khorshidi et al., 2014), which includes motion correction, MSMSulc surface registration to the fs_LR 32k mesh, high-pass filtering (2000 s FWHM) and removal of noise components.

**Parcellation and signal extraction.** The cortex was divided into 200 regions using the Schaefer 2018 parcellation (7-network order, fs_LR 32k CIFTI version; Schaefer et al., 2018). For each region, the mean signal over its cortical vertices was computed (nibabel 5.4.2) and z-scored over time, giving a 1,200 × 200 time-series matrix per participant.

**Quality control.** Participants were excluded if (i) mean relative head motion (HCP `Movement_RelativeRMS_mean`) exceeded 0.2 mm, (ii) fewer than 1,100 volumes were available, or (iii) any region had a missing or constant signal. Carpet plots of every participant were visually inspected. No participant met an exclusion criterion, leaving **N = 15** for analysis (mean relative motion = 0.089 ± 0.028 mm, range 0.060–0.165 mm). As a sanity check, mean functional connectivity within Yeo networks exceeded that between networks in every participant.

**Reproducibility.** Subject IDs, run, atlas, QC thresholds and software versions are recorded in the project repository (`config.yaml`, `src/p1_data/candidates.txt`, `requirements.txt`).
