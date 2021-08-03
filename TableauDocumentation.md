# [SchoolTextViz, ADS Test Site, Misc Testing]

## Dashboard description
- Audience: Valentina Bali/Political Science researchers.
- Purpose: To provide a visual component for the SchoolText project.
- Link: https://vis.qa.itservices.msu.edu/#/site/ADSTestSite/workbooks/489/views
- Last updated: 6/15/21 at 2:27PM.

## Data Source(s)
- US_Schools_Tableau: https://michiganstate.sharepoint.com/:x:/r/sites/MSUITADSDataScience/_layouts/15/Doc.aspx?sourcedoc=%7BB0C920A5-5129-40C1-BB10-96D1BDFB0B1C%7D&file=US_Schools_Tableau.csv&wdLOR=cA634EA8B-EB00-46FF-B6F8-63DE3C9BDDA1&action=default&mobileredirect=true&cid=4a71fa80-d2fc-453e-9d94-4e1318a667e1
- hexmap: https://michiganstate.sharepoint.com/:x:/r/sites/MSUITADSDataScience/_layouts/15/Doc.aspx?sourcedoc=%7B8BB184FE-821E-4BD5-BF2D-D43256517BB5%7D&file=hexmap.xlsx&action=default&mobileredirect=true
- missions: placeholder, this doesn't exist yet but I plan on having all the mission statements consolidated into one file

### Data Source 1: US_Schools_Tableau

__Connection Details:__
- Type: Extract
- Server: QA
- Service: NCES
- Port: 6311
- Schema: None

### Data Source 2

__Connection Details:__
- Type: Live
- Server: QA
- Service: None
- Port: 6311
- Schema: None


__View Name(s):__
- National Dash
    - National View
    - National Dash Info
- State Dash
    - State View
    - Zip View
    - Web View
    - Local Color Key
    - State Dash Info

__Calculated Fields__

| Field Name | Calculation | Description|
| --- | --- | --- |
| Percentage of websites | SUM([Number Websites])/SUM([Number of Schools]) * 100 | Calculates the percentage of websites a state has |
| Has Website? (Color) | IF ATTR([Website]) = "None" THEN 1 ELSE 0 END | Assigns 0 or 1 depending if the school has a website. Used to assign mark colors  |
| School Latitude  | ```SCRIPT_REAL("library('tidygeocoder'); library('dplyr') locations <- data.frame(address = unlist(.arg1)); latlongs <- locations %>% geocode(address, method = 'arcgis', lat = latitude , long = longitude) latlongs$latitude", ATTR([Full Address]))  | Calculate the latitude of a school based on geocoded address. |
| School Longitude | SCRIPT_REAL("library('tidygeocoder'); library('dplyr') locations <- data.frame(address = unlist(.arg1)); latlongs <- locations %>% geocode(address, method = 'arcgis', lat = latitude , long = longitude) latlongs$longitude", ATTR([Full Address])) | Calculates the longitude of a school based on geocoded address. |
| Full Address | [Street] + STR(" ") + [City] + STR(" ") + STR(" ") + [State] + STR(" ") + STR([ZIP Code]) | Used to consolidate location measures.|

__Hierarchies:__
- None were used.

__Sets:__ 
- State Set: 
A set that excluded the Bureau of Indian Education (BIE), U.S Virgin Islands (VI), and American Samoa (AS) from the state select filter. 
BIE is an institution across the country and datapoints under jurisdiction still appear with regular state filters. VI and AS had issues 
regarding the geocoding and were hidden. 

__Groups:__
- None were used.

__Filters:__
- No filters beyond selection actions were used.

## Parameters

None were made.


## Row-level security

Not implemented.

## Filters by worksheet

| Worksheet Name | Filter applied|
| State View | State Set: <State> |
| State View | ZIP code |
| Zip View | Action(ZIP Code) |
| Web View | Action(Full Address) |
