# Marketing Funnel Analysis

An end-to-end analysis of e-commerce customer activity, following the workflow **Excel → Python → Power BI**. The project explores product views, cart activity, purchases, and the limits of interpreting events grouped by session.

> **A note about the data:** This repository includes a sanitized 9,999-record sample, not the full October 2019 dataset. The published copies omit `user_id` and `user_session`, and timestamps are reduced to the UTC calendar date. Original customer-level files and the Power BI file are not published.

## Project workflow

**Excel → Python → Power BI**

### Phase 1 — Excel: data preparation and quality checks

Sanitized copies of the event sample and cleaned workbook are included below. They retain the `Cleaned_Data`, `Data_Quality_Report`, and `Cleaning_Summary` sheets, but omit customer and session identifiers and reduce timestamps to dates. The original, identifier-bearing files remain local and unchanged.

- Sanitized event sample: [`data/raw/2019-Oct-Sanitized-Sample.csv`](data/raw/2019-Oct-Sanitized-Sample.csv)
- Sanitized cleaned workbook: [`data/cleaned/Task_3_Marketing_Funnel_Cleaned_Sanitized.xlsx`](data/cleaned/Task_3_Marketing_Funnel_Cleaned_Sanitized.xlsx) (also available in [`excel/`](excel/Task_3_Marketing_Funnel_Cleaned_Sanitized.xlsx))
- Script input: `data/cleaned/Task_3_Marketing_Funnel_Cleaned.xlsx` (provide your own authorized, complete workbook locally; the sanitized public copy does not contain the identifier columns required for session analysis)
- Required worksheet: `Cleaned_Data`
- Required columns: `event_time`, `event_type`, `product_id`, `category_id`, `category_code`, `brand`, `price`, `user_id`, and `user_session`

### Phase 2 — Python: repeatable funnel analysis

The Python script standardizes event fields and summarizes event counts, session-level funnel patterns, prices, categories, brands, daily activity, and data quality. It prints the full report in the terminal and does not create a text report file.

- Analysis script: [`python/marketing_funnel_analysis.py`](python/marketing_funnel_analysis.py)
- Python analysis report: [`reports/Task_3_Phase_3_Python_Analysis_Report.pdf`](reports/Task_3_Phase_3_Python_Analysis_Report.pdf) · [editable DOCX](reports/Task_3_Phase_3_Python_Analysis_Report.docx)

To run the analysis from the project root, place your own authorized, script-compatible cleaned workbook at the expected input path, or pass its location with `--input`. The public sanitized workbook is for inspection and cannot produce user/session-level analysis.

```powershell
python -m pip install pandas openpyxl
python .\python\marketing_funnel_analysis.py
```

To use a workbook at a different location, pass it with `--input`:

```powershell
python .\python\marketing_funnel_analysis.py --input ".\path\to\another-workbook.xlsx"
```

### Phase 3 — Power BI: interactive dashboard

The Power BI report presents the marketing funnel overview and product/customer analysis. The `.pbix` file is retained locally and is not published here; the images below are static previews.

**Marketing funnel overview**

![Marketing funnel overview dashboard](visuals/marketing_funnel_overview.png)

**Product and customer analysis**

![Product and customer analysis dashboard](visuals/product_customer_analysis.png)

## Repository contents

```text
data/
  raw/2019-Oct-Sanitized-Sample.csv
  cleaned/Task_3_Marketing_Funnel_Cleaned_Sanitized.xlsx
excel/
  Task_3_Marketing_Funnel_Cleaned_Sanitized.xlsx
python/
  marketing_funnel_analysis.py
reports/
  Task_3_Phase_3_Python_Analysis_Report.docx
  Task_3_Phase_3_Python_Analysis_Report.pdf
visuals/
  marketing_funnel_overview.png
  product_customer_analysis.png
  project_workflow.svg
```

The published sample omits `user_id` and `user_session` and reduces timestamps to dates. The original source CSV, identifier-bearing cleaned workbook, and Power BI file remain local and are not published.

## Reading the funnel carefully

The analysis checks whether a session contains views, cart events, or purchases and reports descriptive ratios. Session-level event presence does **not** prove event order, so these ratios are not verified step-by-step conversion rates. The sample is also limited and should not be generalized to all customers or the entire month.

## Future implementation roadmap

The current analysis is a sample-based descriptive baseline. These are potential next steps—not features already included in the project:

1. **Analyze the full authorized dataset.** Process larger files in chunks or through a database, then compare the selected sample with the full source before drawing broader conclusions.
2. **Measure ordered funnel transitions.** Reconstruct event timelines within sessions and define explicit view-to-cart and cart-to-purchase rules, including session boundaries and repeated events.
3. **Add cohort and time-based views.** Compare conversion patterns across dates, acquisition periods, product groups, and returning versus first-time users where those fields are available.
4. **Validate dashboard metrics.** Document KPI definitions, reconcile Power BI totals with Python outputs, and add recurring data-quality checks before refreshing the report.

Any conversion or customer-level analysis should use appropriately authorized data and clearly state its definitions, coverage, and limitations.

## Reports

- [Marketing Funnel Analysis — PDF](reports/Task_3_Phase_3_Python_Analysis_Report.pdf)
- [Marketing Funnel Analysis — editable Word report](reports/Task_3_Phase_3_Python_Analysis_Report.docx)
