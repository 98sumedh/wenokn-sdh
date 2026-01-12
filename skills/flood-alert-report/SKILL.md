---
name: flood-alert-report
description: Guide for creating a flood alert report.
---

# flood-alert-report Skill

## Description 
This skill defines what data is required to generate a report for a specific flood alert.

## When to Use

Requested to generate a report for a flood alert.

## How to Use

For a flood alert, create a step-by-step to-do list to run the following queries and retrieve relevant data:

- Find the flood alert.  
- Find all gauges in the polygon of the flood alert.
- Find the rivers these gauges locate. (Critical Notes: if a gauge name contains a river name, sometimes this river name may be incorrect or the river may have been renamed for historical reasons or the gauge has been allocated from another river without renaming. Carefully verify that the river is indeed the one where the gauge is located.)
- Find all the gagues on these rivers. 
- Find the precipitation forecase for the locations of these gauges.
- Find all census blocks intersecting the polygon of the flood alert.
- Find the population, house units and flood related variables of these blocks from Google Data Commons.
- Find the power plants in the the polygon of the flood alert.

generate a comprehansive report based on the fetched data.




