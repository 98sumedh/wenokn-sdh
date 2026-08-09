---
name: sample-queries
description: provide sample queries for this application
---

# Sample Queries Skill

## When to use

- when users ask what queries can be asked
- when users want to get some sample queries

## Important Notes

Show exactly the queries given in the examples. It can help users to understand how sophisicated queries they can ask.

## Eaxmples: Sample Queries

#### States, Counties and Rivers
* Find the state of Utah.
* Find all states that border Utah.
* Find the Ohio River and all states through which the Ohio River flows.
* Find the Scioto River and all downstream counties from Ross County.
* Find Los Angeles County and all rivers that flow through it.
* Find all rivers that flow through Arizona with a length greater than 100 km. 
* For each county in Ohio, find the river that has the longest path length (in km) within that county's boundaries, and save these rivers as GeoJSON.

#### Dams, Coal Mines and Power Plants
* Find all dams in Ross County.
* Find the Muskingum River and all dams on it.
* Find all upstream counties along the Muskingum River, starting from the dam named “Muskingum River Lock and Dam No. 5 – Swift’s No. 5.”.
* Find all coal mines within 1,000 meters of the Ohio River.
* Find the coal mine closest to the Ohio River.
* Find downstream counties of the Ohio River starting from the River View Coal Mine. 
* Find all solar power plants with a total capacity greater than 100 megawatts in Kentucky.
* Compare the energy usage of power plants in California and Ohio.
* Compare the power plants of "Pacific Gas & Electric Co." and "San Diego Gas & Electric Co."

#### Hydrologic Basins, Watersheds, and Sub-Watersheds (HUC 6, 10, 12)
* Find the hydrologic basin that contains the Scioto River outlet and save the basin as GeoJSON.
* Find all hydrological basins that intersect the state of Ohio.
* Find all counties that intersect the Lower Ohio–Salt Basin.
* Find all basins through which the Scioto River flows.
* Find all rivers that flow through the Roanoke Basin.
* Find all watersheds within the Kanawha Basin.
* Find all sub-watersheds that intersect the Scioto River.

#### Stream Gages
* Find the Scioto River and all stream gages located along the river. 
* Find all gages within the Ross county.
* Find the Muskingum River.  
  Find the dam named “Muskingum River Lock and Dam No. 8 - Rokeby No. 8”.  
  Find the upstream gage with the shortest distance in km to this dam on the Muskingum River.
* Find the number of gauges for each state in USA. 
* Find all gauges with the current flow greater than 5000 cfs and the current stage greater than 100 feet.

#### Demographics, Economics, Health, and Education via Google Data Commons
* Show the population for all counties in the state of Ohio.
* Find the population for all states adjacent to the state of Ohio.
* Find the median individual income for Ross County and Scioto County.
* Find the number of people employed in all counties through which the Scioto River flows.
* Show the Social Vulnerability Index for all counties downstream of the coal mine named "River View Mine" along the Ohio River.
* Show the unemployment rate for all counties in the state of Ohio for the most recent year.
* Find the percentage of adults without health insurance for Ross County and Scioto County.
* Show the high school graduation rate for all counties adjacent to the Ross County.

#### Census Tracts, Census Blocks, and Assets at Risk of Flooding
* Find all census tracts that the Scioto River flows through.
* Find the population of all census tracts within 1000 meters from the Scioto River.
* Find all census blocks within 1000 meters from the Fayette Solar power plant.
* Retrieve all power plants at risk of flooding in Ohio at 2 PM on July 1, 2025 with tract level FIPS codes.
* Retrieve all buildings at risk of flooding in Ohio from 6 PM 2025-07-18 to 6 AM 2025-07-19.
* Retrieve all buildings at risk of flooding within the watersheds that intersect the Scioto River at 8 PM on July 1, 2025.
* First, identify all assets in Ohio that are at risk of flooding within the next 24 hours. 
  Then, extend the result with precipitation forecast at the risk date only.

#### PFAS Contamination Observations and FRS Facilities
- First, find FRS sewage treatment facilities within 100 meters of PFAS contamination observations in Maine.  
  Also, save these related contamination observations above as GeoJSON.
- First, find all PFAS contamination observations within 800 meters of FRS water supply and irrigation facilities in Maine.  
  Also, find all FRS water supply and irrigation facilities in Maine within 800 meters of PFAS contamination observations.
- First, find the Presumpscot River.  
  Then, find PFAS contamination observations within 100 meters of the river.  
  Next, find all downstream census tracts from these contamination observation locations.  
  Finally, retrieve the Social Vulnerability Index for these census tracts.
- First, find the Androscoggin River.  
  Then, find FRS solid waste landfill facilities located within 1 km of the river.   
  Starting from the most upstream landfill facility, identify all downstream census tracts along the river.  
  Finally, retrieve the population of these census tracts.  

#### Aggregations
* How many rivers flow through each county in Ohio?.
* How many dams are in each county of Kentucky?
* How many coal mines are in each basin in Ohio?
* Find the sum of the total megawatt of solar power plants in each state in USA.
* List the five states in the United States with the largest number of coal mines.    
* Find the upstream-most dam on the Scioto River.  
* Find the 10 USA counties with the largest population.
* Find the population of the ten counties with the lowest average income in the United States.
* Find the largest county in the U.S. by land area.
* Find the three largest basins by area.
* Find all counties that intersect 8 basins or more.
* Which county has the most coal mines?

#### Jordan Health Geography
* Find all hospitals in Amman.
* Find the number of health facilities in each governorate of Jordan.
* Show the population of each district in Jordan.
* Find the largest subdistrict in Jordan by population.

#### Jordan Climate-Health Models (results are on synthetic SYNMODINF data)
* Which model provides the best forecasting skill for diarrheal disease in Jordan?
* How much does adding climate features improve the disease forecast, per model?
* How much of disease variance does climate explain on its own versus the autoregressive signal?
* Does modeling disease at the HSA level beat governorate- or country-level?
* Which health service areas would need targeted interventions to offset climate influence, and where would interventions be useless?
* How sensitive is patient allocation to the gravity-model parameters alpha and beta?

#### Transboundary Groundwater (Ukraine, Poland, Lithuania, Latvia, Estonia)
* In Lithuania, how does unconfined groundwater depth vary spatially?
* Compare the groundwater fluctuation magnitude in the LT-LV karst region to the rest of the transboundary countries.
* Which transboundary region has the deepest water table on average?
* Explain why the PL-UA border area differs from the LT-LV area in groundwater dynamics.
* Show wells in the PL-UA border area tapping a karst aquifer.
* Are there wells where the water table sits below the borehole bottom?

#### Miscellaneous
* Find NPDES wastewater facilities within 100 meters of the Scioto River. 
* Find all counties in Southern California.
* Find all counties adjacent to Los Angeles to the east.
* Find the longest river flowing through counties adjacent to LA's eastern border that does not intersect LA County.
    
