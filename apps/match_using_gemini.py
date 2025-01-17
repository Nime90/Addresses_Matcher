#using Gemini
#price: 0.005 
import streamlit as st
def gemini_solution(model,api_key):
    import streamlit as st
    import pandas as pd

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

        toscana_address = ''
        for t in toscana_scuole_geo["indirizzo_geocoding"].unique():
            toscana_address = toscana_address + str(t)+'\n ' 

        elenchi_address = '' 
        for e in elenchi_sezioni['INDIRIZZO'].unique():
            elenchi_address = elenchi_address + str(e)+'\n ' 

        def gemini_assistant(input_s, model_s, api_key):
            import google.generativeai as genai, os
            from types import SimpleNamespace

            genai.configure(api_key=api_key)
            generation_config = {"temperature": 0}
            def calculate_gemini_cost(response):
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                
                input_cost_per_million = 0.075  # $ per million input tokens
                output_cost_per_million = 0.30  # $ per million output tokens

                input_cost = (input_tokens / 1000000) * input_cost_per_million
                output_cost = (output_tokens / 1000000) * output_cost_per_million

                total_cost = input_cost + output_cost
                return total_cost

            model = genai.GenerativeModel(model_s,generation_config=generation_config)
            response = model.generate_content(input_s)
            cost = calculate_gemini_cost(response)
            response_full = SimpleNamespace(text=response.text, cost=cost)
            return response_full

        def find_closest_address(address, toscana_address=toscana_address,model=model,api_key = api_key):
            
            prompt = f''' Given this address: "{address}". Please carefully look at every single address in this list {toscana_address} and find the best match for the given address.
            Please base your decision on the similarity of the name (ideally it is the same name written differently).
            It is important that you only return the selected address. No additional expalantion not comments.'''
            response_cost = gemini_assistant(input_s=prompt, model_s=model, api_key=api_key)
            costo = response_cost.cost
            response=response_cost.text
            
            #st.write('questo esercizio é costato: ',costo)
            return response, costo

        indirizzo_match_toscana = []
        indirizzo_elenchi = []
        costo_t = 0.0
        for indirizzo in elenchi_sezioni['INDIRIZZO'].unique():
            indirizzo_elenchi.append(indirizzo)
            try:
                closest_match, costo=find_closest_address(indirizzo)
                costo_t = costo_t + costo
                indirizzo_match_toscana.append(closest_match)
            except:
                st.write(' nessun indirizzo trovato per ', indirizzo)
                indirizzo_match_toscana.append(None)

        indirizzi_match_df = pd.DataFrame()
        indirizzi_match_df['indirizzo_elenchi'] = indirizzo_elenchi
        indirizzi_match_df['indirizzo_toscana'] = indirizzo_match_toscana
        csv_data = indirizzi_match_df.to_csv(index=False)
        st.write('questo esercizio in totale é costato: ',costo_t)
        st.download_button(
            label="Download results File",
            data=csv_data,
            file_name=f'indice_indirizzi_gemini_{model}.csv',
            mime="text/csv",
        )

def run() -> None:
    # Streamlit app title
    st.title("The Match Assistant!(Gemini)")
    st.write("Please load your files to continue.")
    api_key = st.text_input("<inserisci qui la tua gemini api_key>")
    model = st.text_input("please select the model to use: ", "gemini-2.0-flash-exp")
    if api_key and  model:
        gemini_solution(model=model ,api_key=api_key)
    
    if __name__ == "__main__":
        run()


