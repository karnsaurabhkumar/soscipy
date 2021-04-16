# Soscipy
This library attempts to solve some of the most basic challenges with data science pipelines and analysis. Some of the most repeated functions have been extracted while some other useful tools have been added.

There are four different parts to the library that talks to specific needs while working with data.
1. Data fetching
2. Data analysis
3. Data processing
4. Data visualisation
5. Utilities


### 1. Data Analysis
**dat2csv:** A simple module to export data into a csv file



### 2. Data processing
**Combine** Takes two dataframes as input and exports a merged dataframe automatically. It figures out a primary key for the dataset and utilised TfIdf to match entities before merging

```
from socipy.process.rename_pd import rename_pd
df = rename_pd(df,[col1,col2,col3],[new_col1,new_col2,new_col3])
```

**Thin Panda:** A set of commonly used pandas functions such as renaming the columns etc.



**Parallelize:** A simple wrapper that takes a function and list of parameters and runs them in parallel to help you save the time and effort of dealing with more complicated multi-processing tools 




### 3. Data visualisation
**Plot:** Simple functions to quickly export visualised graphs
```
from kornect.plot import sns_cntplt_array
sns_cntplt_array([1,2,2,3,3,4],chart_title='Random chart',export=False) 
```
![Count Plot Chart](examples/kornect_plot.png "Count Plot Output")

**istates:** Takes a dataframe with state names and values and plots a geomap of India for you as a PNG or GIF

**idistrict:** Takes a dataframe with district names and values and plots a geomap of India for you as a PNG or GIF

### 4. Utilities
**Browser:** Creates a selenium browser for you
**Update Progress:** This takes a float as an input and creates a beautiful progress bar and shows you the percentage. No added libraries just pure python implementation.
```
from kornect.utilities import update_progress
import time

for i in range(100):
    update_progress(i/100.0)
    time.sleep(0.01)
```



