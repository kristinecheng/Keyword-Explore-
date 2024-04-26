# README / Report **(R2)**

## Title

Explore universites and faculties with significant keywords for CS Master Applications.

## Purpose

The application is desgined for users that is planning to pursure Master Degree. Users can use this dashboard to explore for faculties and universities with their perference on keywords **(R4)**. The dashboard calculate trustful statistic including research interests trends over the years, relative score of the research topic from given faculty and university, and comparision between different keywords **(R5)**.

## Demo
 * Link: https://mediaspace.illinois.edu/media/t/1_6gus3awu **(R3)**

## Installation

As the application coordinates with three different databse, please make sure the local computer has same database information in the following. 
| Database | Connection details |
| --- | --- | 
| MYSQL **(R6)**| Database of the Academic world with user credentials root:password (username:password)  host:'localhost' port:'3306' | 
| MongoDB **(R7)**| Document database for academic world with default settings. host:'localhost' port:'27017' | 
| Neo4J **(R8)**| Graph database with standard credentials neo4j:password (username:password) host:'localhost' port:'7687' |

To run the code, simply enter in terminal: `python3 app.py`

## Usage

* Widget 1: By selecting the keyword, display the 10 most cited research paper.
* Widget 2: By selecting the keyword, display the top professor that has highest KRC score.
* Widget 3: By selecting the university, it will display the top 10 keywords of the school and the KRC score in pie chart.
* Widget 4: By selecting the time period (year), it shows the top 10 popular keywords of current year. 
* Widget 5: Users are able to add favorite keyword(s) and display the favorite keyword table.
* Widget 6: Display histogram to compare statistic between each favorite keywords. 
* It has total 6 widgets **(R9)** and contains 4 user input **(R11)**, along with two widgets perform updates of the backend database for insertion and deletion on keywords **(R10)**. All widgets are designed in rectangular space **(R12)**. 

## Design

The application have one main app.py with frontend implementation using Dash and Plotly. Database are designed and interacte with each API's in three files, mysql_utils.py, mongodb_utils.py, and neo4j_utils.py.

## Implementation

* Widget 1 to 3 are implemented with Neo4j. **(R5)**
* Widget 4 is implemented with MongoDB. **(R4)**
* Widget 5 to 6 are implemented with MySQL along with performing updates in backend database. **(R6)**
* Frontend are implemented with dash, dash_bootstrap_components, and plotly.
* Backend are implemented with three APIs to access database, MySQL(mysql.connector), MongoDB (pymongo) and Neo4j(neo4j). 

## Database Techniques

* All techniques are designed with MySQL located in mysql_utils.py
* Add index to the name variable in keyword table. **(R13)**
* Add trigger on faculty_keyword table to make sure keyword score is non-negative. **(R14)**
* Create view from faculty and university to show faculty from 'University of Illinois at Urbana Champaign'. **(R15)**

## Extra-Credit Capabilities 

N/A
