# RR pressure-player analysis (created by Anaya)
1. rr_pressure_pipeline.py : clean end-to-end pipeline (features -> win probability -> leverage -> ratings). 
   Run: python rr_pressure_pipeline.py --data <folder with the CSVs> --out outputs   (pandas, numpy, scikit-learn)
2. exploration/ : the scripts as I ran them while exploring (they use pickles; run prep.py first). The repeatability figures in the deck
   (0.53 / 0.38 / 0.25 / 0.05) come from exploration/validate.py and metrics.py; the pipeline uses simpler definitions, so its values differ slightly.
3. deck/ : deck.js (pptxgenjs) + data.json + logo used to build the PowerPoint.
Retained-player filtering and the final shortlist are manual steps based on the IPL 2027 retention lists (17 Nov 2026).
