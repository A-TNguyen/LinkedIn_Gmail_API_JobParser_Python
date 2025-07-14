# File Naming Examples

## Overview

The EmailJobParser now creates separate files for each date range with timestamps to prevent overwriting and allow easy tracking of different processing runs.

## File Naming Pattern

**Main Output Files:**
```
data/processed/job_application_status_{date_range}_{timestamp}.csv
```

**Failure Log Files:**
```
data/processed/failed_verifications_{timestamp}.csv
```

**Note:** Failure logs are now consolidated into a single file per session, with additional columns showing which source file and date range each failure came from.

**Timestamp Format:** `YYYYMMDD_HHMMSS` (e.g., `20250113_143022`)

## Examples by Date Range

### Quick Selection Options

| Date Range Selection | Filename Suffix | Example Filename |
|---------------------|----------------|------------------|
| All Time | `all_time` | `job_application_status_all_time_20250113_143022.csv` |
| Last 24 Hours | `last_24h` | `job_application_status_last_24h_20250113_143022.csv` |
| Last Week | `last_week` | `job_application_status_last_week_20250113_143022.csv` |
| Last Month | `last_month` | `job_application_status_last_month_20250113_143022.csv` |
| Last 3 Months | `last_3months` | `job_application_status_last_3months_20250113_143022.csv` |
| Last Year | `last_year` | `job_application_status_last_year_20250113_143022.csv` |

### Custom Date Ranges

| Date Range Input | Filename Suffix | Example Filename |
|------------------|----------------|------------------|
| `2024-01-01:2024-12-31` | `custom_2024-01-01_to_2024-12-31` | `job_application_status_custom_2024-01-01_to_2024-12-31_20250113_143022.csv` |
| `2024-06-01:2024-06-30` | `custom_2024-06-01_to_2024-06-30` | `job_application_status_custom_2024-06-01_to_2024-06-30_20250113_143022.csv` |
| `2023-01-01:2023-12-31` | `custom_2023-01-01_to_2023-12-31` | `job_application_status_custom_2023-01-01_to_2023-12-31_20250113_143022.csv` |

## Sample File Structure

After running the application multiple times with different date ranges, your `data/processed/` directory might look like:

```
data/processed/
├── job_application_status_all_time_20250113_143022.csv
├── job_application_status_last_week_20250113_150045.csv
├── job_application_status_last_month_20250113_162130.csv
├── job_application_status_custom_2024-01-01_to_2024-12-31_20250113_143022.csv
├── failed_verifications_all_time_20250113_143022.csv
├── failed_verifications_last_week_20250113_150045.csv
└── archive/
    └── (older files if any)
```

## Benefits of This System

### 1. **No Data Loss**
- Previous results are never overwritten
- Each run creates a new file with timestamp
- Easy to track processing history

### 2. **Clear Identification**
- Filename immediately shows what date range was processed
- Timestamp shows when processing occurred
- Easy to find specific results

### 3. **Comparison Capability**
- Compare results from different time periods
- Track changes over time
- Identify trends in job application activity

### 4. **Organization**
- Separate files for different purposes
- Main results and failure logs are clearly distinguished
- Easy to clean up old files if needed

## File Content Examples

### Main Output File
Contains processed job application data:
```csv
Company Name,Job Title,Status,Date,Location,Metadata Subject,Comment
Google,Software Engineer,Applied,2024-01-15,Mountain View CA,Your application was sent to Google,Applied via LinkedIn
Microsoft,Product Manager,Viewed,2024-01-16,Seattle WA,Your application was viewed by Microsoft,Application viewed
```

### Failure Log File
Contains emails that couldn't be parsed, with source file information:
```csv
Timestamp,Email ID,Label,Row Number,Total Emails,Reason,Date,Company Name,Job Title,Location,Status,Metadata,Comment,Source_File,Date_Range
2025-01-13 14:30:22,abc123,LinkedIn/Applied,1,100,Missing company name,2024-01-15,,,Unknown,Applied,Subject line here,Parse failed,job_application_status_last_week_20250113_143022.csv,Last week
2025-01-13 14:35:15,def456,LinkedIn/Viewed,5,50,Parse error,2024-01-16,TestCorp,Engineer,NYC,Viewed,Application viewed,Parse failed,job_application_status_all_time_20250113_143522.csv,All time
```

## Best Practices

### 1. **Regular Cleanup**
- Periodically review and archive old files
- Keep recent results for comparison
- Delete unnecessary failure logs after review

### 2. **Naming Conventions**
- Use consistent date formats in custom ranges (YYYY-MM-DD)
- Choose meaningful date ranges for your analysis needs
- Consider your reporting frequency when selecting ranges

### 3. **File Management**
- Use the `archive/` directory for long-term storage
- Keep frequently accessed files in the main directory
- Consider using external tools for data analysis across multiple files

## Troubleshooting

### File Not Found
If you can't find your output file:
1. Check the console output for the exact filename
2. Look in `data/processed/` directory
3. Verify the timestamp matches when you ran the process

### Large Number of Files
If you have too many files:
1. Move older files to the `archive/` directory
2. Use file explorer to sort by date
3. Consider deleting very old failure logs after review

### Filename Too Long
For very long custom date ranges:
1. Use shorter date ranges when possible
2. The system handles long filenames automatically
3. Windows has a 260 character path limit (rarely an issue) 