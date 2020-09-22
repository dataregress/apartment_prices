import pandas as pd

def remove_unwanted_columns(data_frame, column_list):
    
    data_frame = data_frame.drop(column_list, axis = 1)
    return data_frame

def remove_duplocate_properties(data_frame):
    
    data_frame = data_frame.drop_duplicates(subset = 'id', keep = "first")
    return data_frame

def remove_askforprice_properties(data_frame):
    
    data_frame = data_frame[data_frame['price'] != 'Ask for price']
    return data_frame


def convert_datatypes(data_frame, convert_dict):
    
    data_frame = data_frame.astype(convert_dict)
    return data_frame


def replace_nan(data_frame, replace_dict):
    
    return data_frame.fillna(value = replace_dict)

def fix_bedroom_column(data_frame):
    # creating maid_room feature with true/false based on value in bedrooms column
    data_frame['maid_room'] =  data_frame.no_of_bedrooms.apply(lambda x: '+ Maid' in x, 1, 0)
    
    # removing + Maid string from bedrooms column
    data_frame['no_of_bedrooms'] = data_frame.no_of_bedrooms.apply(lambda x: x.replace(' + Maid', ''))
    
    # assigning 0 bedroom to studio apartments
    data_frame['no_of_bedrooms'] = data_frame.no_of_bedrooms.apply(lambda x: x.replace('studio', '0'))
    
    return data_frame

def convert_amenities_to_columns(data_frame, amenities):
    
    amenities = amenities.replace(', ', ',').replace("'", '').replace(' ', '_').replace('-', '_').replace('/', '').lower()
    amenities_list = amenities.split(',')
    
    new_amenities_list = []
    
    for amen in amenities_list:
        new_amenities_list.append(amen)
    
    new_amenities_list = new_amenities_list[:-1]
    
    for amenity in new_amenities_list:
        data_frame[amenity] = False
        
    return data_frame, new_amenities_list

def fill_amenities(data_frame, new_amenities_list):
    data_frame.amenities = data_frame.amenities.apply(lambda x: x.replace(', ', ',').replace("'", '').replace(' ', '_').replace('-', '_').replace('/', '').lower())
    
    for index, prop_row in data_frame.iterrows():
        if len(prop_row.loc['amenities']) > 0:
            for column_name in new_amenities_list:
                if column_name in prop_row['amenities']:
                    data_frame.loc[index, column_name] = True
            
    return data_frame;
    

def cleanup_property_size(data_frame):
    data_frame['size'] = data_frame['size'].apply(lambda x: x.split('sqft')[0].strip().replace(',', ''))
    
    return data_frame


def create_feature_price_per_sqft(data_frame):
    
    convert_dict = {'price': int,
                'size_in_sqft':int
               }
    
    data_frame = data_frame.astype(convert_dict)
    
    data_frame['price_per_sqft'] = round(data_frame['price']/data_frame['size_in_sqft'], 2)
    
    # reposition column
    
    price_per_sqft = data_frame.pop('price_per_sqft')
    data_frame.insert(6, 'price_per_sqft', price_per_sqft)
    
    price = data_frame.pop('price')
    data_frame.insert(4, 'price', price)
    
    return data_frame

def mark_property_quality(data_frame):
    
    for index, prop_row in data_frame.iterrows():
        no_amenities = len(prop_row.loc['amenities'].split(','))
        if  no_amenities > 0 and no_amenities <= 7:
            data_frame.loc[index, 'quality'] = 'Low'
        elif no_amenities >= 8 and no_amenities <= 14:
            data_frame.loc[index, 'quality'] = 'Medium'
        elif no_amenities >= 15 and no_amenities <= 21:
            data_frame.loc[index, 'quality'] = 'High'
        elif no_amenities >= 22 and no_amenities <= 28:
            data_frame.loc[index, 'quality'] = 'Ultra'
        else:
            data_frame.loc[index, 'quality'] = 'None'
        
    quality = data_frame.pop('quality')
    data_frame.insert(8, 'quality', quality)
    
    return data_frame

def clean_location_details(data_frame):
    # Removing Dubai part from the location field
    
    # removing + Maid string from bedrooms column
    data_frame['location'] = data_frame.location.apply(lambda x: x.replace('Dubai, ', ''))
    
    for index, prop_row in data_frame.iterrows():
        location_parts_len = len(prop_row.loc['location'].split(', '))
        
        if location_parts_len > 1:
            data_frame.loc[index, 'location'] = prop_row.loc['location'].split(', ')[0]
            
        neighborhood_name = data_frame.loc[index, 'location']
        if 'Downtown Jebel Ali' in neighborhood_name:
            data_frame.loc[index, 'location'] = 'Jebel Ali'
        elif 'Downtown' in neighborhood_name:
            data_frame.loc[index, 'location'] = 'Downtown Dubai'
    
    data_frame.rename(columns={'location':'neighborhood'}, inplace = True)
    
    data_frame['neighborhood'] = data_frame.neighborhood.apply(lambda x: x.replace(' (Akoya by DAMAC)', ''))
    
    return data_frame