# Location Based Social Network Service (LBSNS)
## Network Data Analysis CW 2
## Multi-layer networks


### Data source
1. [NYC Foursquare Check-ins](https://www.kaggle.com/chetanism/foursquare-nyc-and-tokyo-checkin-dataset)
<!-- 2. [NYC GIS Zoning Features](https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-gis-zoning.page) -->
3. [Foursquare Categories Resource](https://developer.foursquare.com/docs/resources/categories)


### Preprocessing
1. Download check-ins data from [Foursquare](#NYC Foursquare Check-ins).
2. [data_insight.py](data_insight.py)
   1. Extract all venueCategory
   2. Count user venueCategory visit frequency.
3. Download official venue category from Data source 2.
4. [categroy_extract.py](category_extract.py)
   1. 