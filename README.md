# MindLibs repository
This repository contains the code necessary to reproduce the figures from the manuscript: *Updated neural representations predict reinterpretation of ambiguous social scenes independent of gaze-linked visual resampling*.

Important info: 
- Folders are named for the analysis they perform, not the figure they produce, since
several scripts contribute to more than one figure. Which figure each script feeds is
listed under Figure map below.
- Scripts are numbered in pipeline order
- If you need any additional information that is not included in this code directory, please feel free to reach out to **Clara Sava-Segal** at 📧 [csava@dartmouth.edu](mailto:csava@dartmouth.edu). 
Raw MR data will be added on OpenNeuro and updates will be made as a part of the review process

## Requirements

Used Python 3.7.9 and R 4.4.1.

---

Everything except `001` starts from a single file:

```
data/subject_by_node_Viewing1_Viewing2_subs_schaefer_rois.csv
```

One row per subject × Schaefer parcel × condition × stimulus (56 subjects × 100 parcels
× 2 conditions × 45 stimuli = 252,000 rows), carrying:

- "R_Value": Pearson *r* between the Viewing-1 and Viewing-2 voxel patterns for that
  trial and parcel. Viewing 1 and Viewing 2 come from a GLM generated via AFNI. Will be converted to a "neural shift" in the scripts themselves.
- "Node_Number": Schaefer-100 parcel (1–100)
- "Condition" : `expt` (experimental) or `cont` (control)
- "stim_file": (images used, will be added ASAP)
- behavioral and NLP columns : ratings, free-text responses, cosine similarities

- Scripts `002` onward rely on this df. `001` creates it. 

---

## Scripts

### `01_condition_differences/` : condition differences in Fig 2

- `001._prepping_df_for_lmer.ipynb` : correlates the Viewing-1 and Viewing-2 beta patterns
  trial-by-trial within each parcel, separately per condition, and merges in the relevant behavioral
  and NLP columns. Writes the .csv in data
- `002._subject_by_node_Viewing1_Viewing2.Rmd` : behavioral models, and the parcel- and
  network-level LMERs. Writes `model_outputs/` and the resampled matched-length iterations that are then used in 003. It also creates the behavioral plots that go into **Fig. 2A**
- `003._visualizing_R_betas_condition_differences_surfplot_matched_length.ipynb` : cortical
  surface map and network distribution for the condition effect. This becomes **Fig. 2B**

### `02_reinterpretation/` : Fig 3

- `004._making_3dplot.ipynb` : creates the 3D scatter in **Fig. 3B**.
- `004._visualized_behavioral_effects.Rmd` : behavioral effects in **Fig. 3A**.
- `005._subject_by_node_Viewing1_Viewing2_network_reinterpretation.Rmd` : reinterpretation
  LMERs, by parcel and by networks. Writes into
  `model_outputs/`. **Fig. 3C** and **D** are visualized in this file.
- `006._visualizing_reinterpretation-poly-model.ipynb` : surface map and network
  distribution for the reinterpretation effect, using the output from `005`. Creates **Fig. 3C**.

### `03_eyetracking/` : eyetracking analyses in Figs 2, 3 and 4

- `007._..._eyetracking_condition_differences.Rmd` : gaze-shift score by condition, in **Fig. 2C**.
- `008._..._eyetracking_reinterpretation_neural.Rmd` : Gaze x reinterpretation **(Fig. 3E)** and gaze × neural-shift × semantic-distance
  models, testing whether the DMN-B and combined visual effects are independent (**Fig. 4.**)


### `utils/`

- `run_lmer_functions.R` : fits LMERs per parcel and per network, and writes the tidy
  `model_outputs/` CSVs. Used by `002`, `005`, `007`, `008`.
- `add_network_labels.R` : maps Schaefer parcels to 7N and 17N networks. Used by `002`,
  `005`, `007`, `008`.
- `ggbetweenstats_custom.R` : used by `002`.
- `plotting_brains_surfplot.py` : `map_values_to_atlas`, `Plot`. Used by `003` and `006`.
- `plotting_network_plots.py` : `plot_17N_effect_distribution_horizontal`,
  `compare_network_effects`. Used by `003` and `006`.
- `7N_to_17N_complete_mapping.csv` : parcel to network lookup, used in
  `add_network_labels.R` and the plotting functions.

---


