#Alternative method. poor resutls
import streamlit as st
def get_close_match():
    #Alternative method. poor resutls
    from difflib import get_close_matches
    import pandas as pd
    import streamlit as st
    import tempfile

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


        # Strip whitespace from addresses
        elenchi_addresses = [address.strip() for address in elenchi_sezioni['INDIRIZZO'].unique()]
        toscana_addresses = [address.strip() for address in toscana_scuole_geo["indirizzo_geocoding"].unique()]

        # Match addresses
        matches = []
        for toscana_address in toscana_addresses:
            best_match = get_close_matches(toscana_address, elenchi_addresses, n=1, cutoff=0.6)
            matches.append((toscana_address, best_match[0] if best_match else "No match found"))

        # Create a button for generating and downloading the file
        if st.button("Generate and Download Results"):
            # Create a temporary file to write the results
            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix=".txt") as temp_file:
                # Write the results to the file
                for toscana_address, match in matches:
                    temp_file.write(f"Toscana: {toscana_address} -> Match: {match}\n")
                
                temp_file_path = temp_file.name
            
            # Provide a download link for the file
            with open(temp_file_path, "rb") as file:
                st.download_button(
                    label="Download Results",
                    data=file,
                    file_name="results.txt",
                    mime="text/plain",
                )
        
def run() -> None:
    # Streamlit app title
    st.title("Close Name Matcher")
    st.write("Please load your files to continue.")
    get_close_match()
    
    if __name__ == "__main__":
        run()