################################################################################
####  Metadata for this signature dataset
################################################################################

Observed signature values are calculated with a modified TOSSH toolbox (Gnann et al., 2021).
https://github.com/RY4GIT/TOSSH

Signatures and process interpretations follow Table 1 in Araki et al. (2026), "Continental-scale prediction of hydrologic signatures and processes", HESS.
https://hess.copernicus.org/articles/30/3647/2026/hess-30-3647-2026.pdf

Observed values come from Caravan or GAGES-II streamflow. Predicted values come from random forest models trained on landscape attributes.


################################################################################
####  CSV files
################################################################################

sigs_Baseflow.csv
    Baseflow signatures and process class

sigs_HighStorageCapacity.csv
    Storage-capacity signatures and process class

sigs_WaterBalanceLosses.csv
    Runoff-ratio signatures and process class

sigs_SeasonalVariability.csv
    Seasonal-variability signatures and process class

sigs_OverlandFlow.csv
    Overland-flow threshold signatures and process class

sigs_OverlandFlowType.csv
    Overland-flow infiltration-excess vs saturation-excess type


################################################################################
####  Columns shared by the process CSVs
################################################################################

gauge_id
    Dataset prefix (camels_, hysets_, or gages2_) plus the 8-digit USGS gauge ID.

gauge_num
    8-digit USGS gauge ID.

gauge_name
    USGS gauge name (from Caravan gauge_name or GAGES-II STANAME).

gauge_lat
    Gauge latitude in degrees (WGS84).

gauge_lon
    Gauge longitude in degrees (WGS84).

source
    How the signature values were obtained.

    obs_Caravan
        Observed TOSSH signatures from Caravan.

    obs_GAGES2
        Observed TOSSH signatures from GAGES-II gauges that do not overlap Caravan.

    pred_hys_gg2
        Random-forest prediction for HYSETS/GAGES-II overlap gauges excluded from training because of data-quality flags (trained with Caravan + GAGES-II landscape attributes).

    pred_hys
        Random-forest prediction for HYSETS-only gauges (trained with Caravan landscape attributes).

    pred_gg2
        Random-forest prediction for GAGES-II-only gauges (trained with Caravan + GAGES-II landscape attributes).

order
    Display priority used in visualization, when stacking map layers. Lower numbers are draw top (observed data under predictions, as observed is more reliable).
    1 = obs_Caravan
    2 = obs_GAGES2
    3 = pred_hys_gg2
    4 = pred_hys
    5 = pred_gg2

bivariate_class
    Quantile pair written as X-Y, where X and Y are integers from 1 to 4. Each number is a quartile of one signature. Which signatures are X and Y depends on the file (see below). Some axes are reversed so that class 1 is high values and class 4 is low values. This lines the process-supporting direction up with the same corner of the color grid.

    1-4 or 4-1 indicates the strongest dominance of the hydrologic process, depending on whether high or low signature values indicate process dominance. The definition follows Table 1. The classification logic is in signatures/visualize/plot_sigs_process_multiple_sources.py.

dominance
    True if bivariate_class falls in the process-dominant corner.
    For most files: 1-4, 1-3, 2-3, or 2-4.
    For water-balance losses: 4-1, 3-1, 3-2, or 4-2 (low runoff ratios, meaning larger losses).

color
    Hex fill color for the bivariate map cell that matches bivariate_class.


################################################################################
####  Percentile columns (*_perc)
################################################################################

Each signature has a matching *_perc column, scaled 0 to 100.

For most signatures this is the percentile rank among gauges in the dataset (i.e., ranking within CONUS). A higher signature value corresponds to a higher percentile.

For significance columns (*_signif) it is an inverted p-value score:
    If p > 0.05, the percentile is 0 (not significant).
    If p = 0, the percentile is 100 (most significant).
    If 0 < p < 0.05, values are scaled across that range. 


################################################################################
####  sigs_Baseflow.csv
################################################################################

BFI (unitless)
    Baseflow index, the fraction of total streamflow that is baseflow. High BFI means stronger baseflow.

BaseflowRecessionK (1/day)
    Baseflow recession rate. High K means faster recession and weaker sustained baseflow.

bivariate_class axes
    X = BaseflowRecessionK (low K is class 1)
    Y = BFI (low BFI is class 1)
    Example: 1-4 means slow recession and high BFI (baseflow process is dominant)


################################################################################
####  sigs_HighStorageCapacity.csv
################################################################################

AverageStorage (mm)
    Average catchment storage inferred from streamflow. High storage means greater storage capacity.

RecessionParameters_b (unitless)
    Recession nonlinearity parameter b in -dQ/dt = a Q^b. High b means more nonlinear recession / multiple storage elements.

bivariate_class axes
    X = RecessionParameters_b (high b is class 1)
    Y = AverageStorage (low storage is class 1)
    Example: 1-4 means high recession nonlinearity and high storage (high storage capacity is dominant)


################################################################################
####  sigs_WaterBalanceLosses.csv
################################################################################

TotalRR (unitless)
    Total runoff ratio (long-term Q/P). High TotalRR means smaller water-balance losses (less ET or deep groundwater loss).

EventRR (unitless)
    Event runoff ratio (event Q / event P). High EventRR means smaller event-scale losses.

bivariate_class axes
    X = EventRR (high EventRR is class 1)
    Y = TotalRR (low TotalRR is class 1)
    Example: 4-1 means low event runoff ratio and low total runoff ratio (water-balance losses are dominant)


################################################################################
####  sigs_SeasonalVariability.csv
################################################################################

VariabilityIndex (unitless)
    Index of streamflow variability. High values mean more variable flow.

Recession_a_Seasonality (unitless)
    Seasonality of the recession parameter a. High values mean stronger seasonal change in recession.

bivariate_class axes
    X = VariabilityIndex (high variability is class 1)
    Y = Recession_a_Seasonality (low seasonality is class 1)
    Example: 1-4 means high flow variability and high recession seasonality (seasonal variability is dominant)


################################################################################
####  sigs_OverlandFlow.csv
################################################################################

Event-based overland-flow signatures are set to missing where snow fraction exceeds 20%.

IE_thresh (mm/day)
    Infiltration-excess (Hortonian) overland-flow rainfall-intensity threshold. A higher threshold means more rainfall intensity is needed to generate infiltration-excess overland flow.

SE_thresh (mm)
    Saturation-excess (Dunne) overland-flow storage/rainfall-volume threshold. A higher threshold means more storage or rainfall volume is needed to generate saturation-excess overland flow.

IE_thresh_signif (unitless)
    p-value for the infiltration-excess threshold. p less than 0.05 means the IE signature is statistically significant.

SE_thresh_signif (unitless)
    p-value for the saturation-excess threshold. p less than 0.05 means the SE signature is statistically significant.

avg_IE_SE_thresh (mm)
    Mean of IE_thresh and SE_thresh. Values above 300 mm are set to missing.

avg_IE_SE_signif (unitless)
    Mean of IE_thresh_signif and SE_thresh_signif.

bivariate_class axes
    X = avg_IE_SE_signif_perc (high significance / low p-value is class 1)
    Y = avg_IE_SE_thresh (low threshold is class 1)
    Example: 1-4 means significant IE/SE thresholds and a high activation threshold (overland-flow process is dominant)


################################################################################
####  sigs_OverlandFlowType.csv
################################################################################

Wu et al. (2021) signatures. Gauges with snow fraction above 20% are excluded. Rows where both R_Pint_RC and R_Pvol_RC are negative are dropped.

R_Pint_RC (unitless)
    Correlation between runoff coefficient and rainfall intensity. High values point to infiltration-excess (IE) overland flow.

R_Pvol_RC (unitless)
    Correlation between runoff coefficient and rainfall volume. High values point to saturation-excess (SE) overland flow.

diff_RCPint_RCPvol (unitless)
    R_Pint_RC minus R_Pvol_RC. Positive is IE-like; negative is SE-like. Missing if both correlations are negative.

dominance
    "IE" if diff_RCPint_RCPvol > 0, "SE" if diff_RCPint_RCPvol < 0, otherwise missing.
    Example: a positive difference means infiltration-excess overland flow is dominant. This is a text label, not a true/false flag like the other process files.
