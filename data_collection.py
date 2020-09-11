# importing libraries
import propertyscrapper as ps
from datetime import datetime

# printing start time of the operation
print('started at:', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# calling function to start the scrapping process and save it in a csv format
ps.start_scrapping_properties(50, 'properties.csv')

# printing end time of the operation
print('completed at:', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
