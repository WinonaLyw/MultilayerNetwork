# Location Based Social Network Service (LBSNS)
## Network Data Analysis CW 2
## Multi-layer networks

### Package 
1. pandas
2. matlibplot
3. xml
4. smopy
5. sklearn

### Data source
1. [NYC Foursquare Checkins](https://www.kaggle.com/chetanism/foursquare-nyc-and-tokyo-checkin-dataset)
<!-- 1. [NYC GIS Zoning Features](https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-gis-zoning.page) -->
1. [Foursquare Categories Resource](https://developer.foursquare.com/docs/resources/categories)


### Preprocessing
1. Download check-ins data from [Foursquare](#data-source).
2. [01_data_insight.py](01_data_insight.py)
   1. Extract all venueCategory
   2. Count user venueCategory visit frequency.
3. Download official venue category from [Foursquare](#data-source).
4. [02_categroy_extract.py](02_category_extract.py)
   1. Extract category from html file.
   2. Map all venueCategory in check-ins to the parent category
   3. If cannot find in official category, then manual input
5. [03_user_loc_cate_mapping](03_user_loc_cate_mapping.py)
   1. aggrate user check-in behaviou on venue categories
6. [04_food_location](04_food_locations.py)
   1. Select out the venues with parent categroy 'Food'
   2. Manually add  a self-defined tag to each food venue type
7. [05_visualisation](06_visualisation.py) and [06_recommend](07_recommend.py)
   1. test the result of training
   2. visualise results
   
### Recommender System
1. [visualisation](visualisation.py) and [recommender](recommender.py)
   1. classes and functions for visualise multilayer network
   2. recommender will use one user id and a location to recommend a list food venues
2. [test_recommender](test_recommender.py)
   1. select user Id
   2. select one living-community location and one out-of-living-community location
   3. fit into recommender
   4. plot results in map