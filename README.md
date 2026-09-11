# SF-311-service-request-explorer
Explore patterns in San Francisco 311 service requests
## Research Questions
1. What are the most common request categories?
2. How does the request volume change over time?
3. How does the median resolution time differ by category?
## Project Scope
The first version will analyze closed service requests from the most recent 12 months
## Planned Visualization
- Top 10 request categories
- Monthly request volume
- Median resolution time by category
## Data Source
San Francisco 311 Cases:
https://data.sf.gov/d/vw6y-z8j6
## Status
Week 1 repository setup is complete
Current structure:

-Python entry point created
-Dependencies recorded
-Data-analysis questions defined
Week 2  Data loading and Cleaning
-Connected the project to San Francisco 311 Socrata API
-Stored the application token in an environment variable instead of source code
-Retrievd a sample of most recent 311 requests
-Selected nine relevant columns for analysis
-Converted request and closure dates to datetime values
-Created a resolution-time column for closed requests
-Preserved open requests with missing closure times
-Removed invalid records, including negative resolution times
-Confirmed that the cleaned dataset loads successfully
