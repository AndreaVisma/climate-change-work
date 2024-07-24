import pandas as pd
import numpy as np

# Load your dataset
file_path = './mexico.xlsx'
df = pd.read_excel(file_path)
df = df[~df.Location.isna()]

# Predefined dataset with latitude and longitude for Mexican states and major cities
predefined_coords = {
    'Chihuahua': (28.6329957, -106.0691004),
    'Coahuila': (27.0586763, -101.7068294),
    'Durango': (24.0277202, -104.6531759),
    'Guanajuato': (21.0190145, -101.2573586),
    'Nuevo Leon': (25.5584286, -99.9962041),
    'Sonora': (29.0951724, -110.9547006),
    'Zacatecas': (22.7759008, -102.5721998),
    'Chiapas': (16.7573037, -93.1327004),
    'Hidalgo': (20.0910967, -98.7623876),
    'Oaxaca': (17.0718253, -96.7265889),
    'Puebla': (19.0414398, -98.2062727),
    'Tabasco': (18.2679842, -92.8994189),
    'Veracruz': (19.1898596, -96.1530239),
    'Benito Juarez': (21.1618751, -86.8515267),
    'Isla Mujeres': (21.232907, -86.7310373),
    'Cozumel': (20.4883167, -86.9458274),
    'Acapulco': (16.852583, -99.8475696),
    'Guerrero': (17.4391926, -99.5450974),
    'Michoacan': (19.3340556, -102.0655195),
    'Jalisco': (20.6595382, -103.3494376),
    'Campeche': (19.8301078, -90.5349094),
    'Quintana Roo': (19.7968703, -87.6184063),
    'Yucatan': (20.8600933, -89.0093808)
}

# Function to get predefined coordinates for a location
def get_predefined_coords(location):
    return predefined_coords.get(location.strip(), (None, None))

# Function to calculate centroid of multiple locations using predefined coordinates
def calculate_centroid_predefined(locations):
    latitudes = []
    longitudes = []

    for location in locations:
        lat, lon = get_predefined_coords(location)
        if lat is not None and lon is not None:
            latitudes.append(lat)
            longitudes.append(lon)

    if latitudes and longitudes:
        centroid_lat = np.mean(latitudes)
        centroid_lon = np.mean(longitudes)
        return centroid_lat, centroid_lon
    return None, None

# Fill missing Latitude and Longitude based on Location using predefined coordinates
for idx, row in df.iterrows():
    if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
        locations = row['Location'].split(',')
        centroid_lat, centroid_lon = calculate_centroid_predefined(locations)
        if centroid_lat is not None and centroid_lon is not None:
            df.at[idx, 'Latitude'] = centroid_lat
            df.at[idx, 'Longitude'] = centroid_lon

# Save the updated dataframe to a new Excel file
output_file_path = './mexico_updated.xlsx'
df.to_excel(output_file_path, index=False)

# Show the first few rows of the updated dataframe to verify
print(df.head(10))