# Location Based Social Network Service (LBSNS)
## Network Data Analysis CW 2
## Multi-layer networks


### Data source
1. [NYC Foursquare Checkins](https://www.kaggle.com/chetanism/foursquare-nyc-and-tokyo-checkin-dataset)
<!-- 1. [NYC GIS Zoning Features](https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-gis-zoning.page) -->
1. [Foursquare Categories Resource](https://developer.foursquare.com/docs/resources/categories)


### Preprocessing
1. Download check-ins data from [Foursquare](#data-source).
2. [data_insight.py](data_insight.py)
   1. Extract all venueCategory
   2. Count user venueCategory visit frequency.
3. Download official venue category from [Foursquare](#data-source).
4. [categroy_extract.py](category_extract.py)
   1. Extract category from html file.
   2. Map all venueCategory in check-ins to the parent category
   3. If cannot find in official category, then manual input
5. [user_loc_cate_mapping](user_loc_cate_mapping.py)