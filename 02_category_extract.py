'''
extract category list from Foursquare site category list html file list tag
map venueCategory with the parent category
(manually input Unknown ones)
'''
# %%
import xml.etree.ElementTree as ET
import pandas as pd

# %%
tree = ET.parse('data/Venue Categories - Foursquare Developer.html')
root = tree.getroot()

cate_dict = {}
for child in root:
    cateName = ''
    for grand in list(child)[0]:
        if grand.attrib['class'] == 'categoryName':
            cateName = grand.text
            print (cateName)
        elif grand.attrib['class'] == 'categoryChildren':
            for gg in grand:
                for ggg in list(gg)[0]:
                    if ggg.attrib['class'] == 'categoryName':
                        cate_dict[ggg.text] = cateName


# %%
print (cate_dict)

# %%
venueCategory = pd.read_csv('data/category.csv', index_col=0)

# %%
venueCategory['parentCategory'] = [(cate_dict[cate] if cate in cate_dict.keys() else 'Unknown') for cate in venueCategory['venueCategory']]

# %%
venueCategory.to_csv('data/category.csv')

## will replace 'unknown' values
# %%