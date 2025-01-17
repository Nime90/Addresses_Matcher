import streamlit as st
import pandas as pd

def match_geoloc(toscana_scuole_geo, elenchi_sezioni):
    import pandas as pd
    def find_lat_lon(address):
        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="Sabrina_geo_locator")
        try:
            location = geolocator.geocode(address)
        except:
            location = None

        if location is not None:
            return location.latitude, location.longitude
        else:
            return None, None

    elenchi_lat = []
    elenchi_lon = []
    for address in elenchi_sezioni['INDIRIZZO']:
        lat, lon = find_lat_lon(address)
        elenchi_lat.append(lat)
        elenchi_lon.append(lon)
        
    elenchi_sezioni['lon']=elenchi_lon
    elenchi_sezioni['lat']=elenchi_lat

    #Not necessary, but for consistency we could use this too
    toscana_lat = []
    toscana_lon = []
    for address in toscana_scuole_geo["indirizzo_geocoding"]:
        lat, lon = find_lat_lon(address)
        toscana_lat.append(lat)
        toscana_lon.append(lon)
        
    toscana_scuole_geo['lon_n']=toscana_lon
    toscana_scuole_geo['lat_n']=toscana_lat

    #getting a thinner dataframes
    elenchi = elenchi_sezioni[['INDIRIZZO', 'lat','lon']]
    elenchi.columns = ['indirizzo_elenchi','lat','lon']
    toscana = toscana_scuole_geo[["indirizzo_geocoding", "lat", "lon",'lat_n','lon_n']]
    toscana.columns = ['indirizzo_toscana','lat','lon','lat_n','lon_n']

    #fixing the lat_lon from toscana file (it is saved with the wrong decimal)
    lat_lon=[]
    for i, l in enumerate(toscana['lat']):
        try:
            lat_lon.append(
                (
                    float(str(int(toscana['lat'][i]))[:2]+'.'+str(int(toscana['lat'][i]))[2:]),
                    float(str(int(toscana['lon'][i]))[:2]+'.'+str(int(toscana['lon'][i]))[2:])
                    )
                )
            
        except:
            lat_lon.append((None,None))
    toscana['lat_lon']=lat_lon

    lat_lon_elen=[]
    for i, l in enumerate(elenchi['lat']):
        lat_lon_elen.append((elenchi['lat'][i],elenchi['lon'][i]))
    elenchi['lat_lon']=lat_lon_elen

    lat_lon_tos=[]
    for i, l in enumerate(toscana['lat_n']):
        lat_lon_tos.append((toscana['lat_n'][i],toscana['lon_n'][i]))
    toscana['lat_lon_n']=lat_lon_tos

    from geopy.distance import geodesic
    closest_point_elenchi=[]
    list1 = elenchi['lat_lon']
    list2 = toscana['lat_lon']
    # Example for haversine distance
    for point1 in list1:
        try:
            closest_point = min(list2, key=lambda point2: geodesic(point1, point2).meters)
            closest_point_elenchi.append(closest_point)
        except:
            closest_point_elenchi.append(None)

    elenchi['closest_point'] = closest_point_elenchi

    index_addresses = pd.merge(elenchi,toscana,how='left',right_on='lat_lon', left_on='closest_point')
    index_addresses = index_addresses[['indirizzo_x','indirizzo_y']]
    index_addresses.columns = ['indirizzo_elenchi','indirizzo_toscana']
    index_addresses= index_addresses.drop_duplicates().reset_index(drop=True)
    index_addresses.to_excel('Indice_iondirizzi.xlsx',index=False)


    from geopy.distance import geodesic
    closest_point_elenchi=[]
    list1 = elenchi['lat_lon']
    list2 = toscana['lat_lon_n']
    list2_clean =[]
    for l in list2: 
        if float(l[0])>0 :
            list2_clean.append(l)
    # Example for haversine distance
    for point1 in list1:
        try:
            closest_point = min(list2_clean, key=lambda point2: geodesic(point1, point2).meters)
            closest_point_elenchi.append(closest_point)
        except:
            closest_point_elenchi.append((None,None))


    elenchi['closest_point'] = closest_point_elenchi

    index_addresses = pd.merge(elenchi,toscana,how='left',right_on='lat_lon_n', left_on='closest_point')
    index_addresses = index_addresses[['indirizzo_elenchi','indirizzo_toscana']]

    index_addresses= index_addresses.drop_duplicates().reset_index(drop=True)
    return index_addresses#.to_excel('Indice_iondirizzi_n.xlsx',index=False)

def run() -> None:
    # Streamlit app title
    st.title("The Geo Locator")
    st.write("Please load your files to continue.")
    # Streamlit file uploader
    toscana_scuole_geo = st.file_uploader("Upload 'regione_scuole_geo.csv' file ", type=["csv", "xlsx"])
    elenchi_sezioni = st.file_uploader("Upload 'elenco_sezioni_elettorali_REGIONE.xlsx' file ", type=["csv", "xlsx"])
    if toscana_scuole_geo is not None and elenchi_sezioni is not None:
        try:
            # Check the file type and read accordingly
            if toscana_scuole_geo.name.endswith(".csv"):
                try: toscana_scuole_geo = pd.read_csv(toscana_scuole_geo, encoding="utf-8", sep=';')
                except: toscana_scuole_geo = pd.read_csv(toscana_scuole_geo)
            elif toscana_scuole_geo.name.endswith(".xlsx"):
                toscana_scuole_geo = pd.read_excel(toscana_scuole_geo)
            # Check the file type and read accordingly
            if elenchi_sezioni.name.endswith(".csv"):
                elenchi_sezioni = pd.read_csv(elenchi_sezioni)
            elif elenchi_sezioni.name.endswith(".xlsx"):
                elenchi_sezioni = pd.read_excel(elenchi_sezioni)
        except Exception as e:
            st.error(f"Error loading file: {e}")

        index_addresses = match_geoloc(toscana_scuole_geo, elenchi_sezioni)
        csv_data = index_addresses.to_csv(index=False)
        if csv_data:
            st.download_button(
                label="Download results File",
                data=csv_data,
                file_name=f'indice_indirizzi_match_geoloc.csv',
                mime="text/csv",
            )
    if __name__ == "__main__":
        run()