#using OpenAi
#price: 0.01 for gpt-4o-mini, 0.1 for gpt-4o, 0.7 for gpt4-turbo
import streamlit as st
def Open_AI_solution(model,api_key):
    import pandas as pd
    from openai import OpenAI

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

        def check_cost(response, model):
            input_tokens = response.usage.prompt_tokens  # Tokens used for the prompt
            output_tokens = response.usage.completion_tokens  # Tokens used for the completion

            if model == "gpt-4o-mini":
                # Pricing details for GPT-4o-mini
                input_cost_per_million = 0.15  # USD per million input tokens
                output_cost_per_million = 0.60  # USD per million output tokens

            elif model == "gpt-4o":
                # Pricing details for GPT-4-turbo
                input_cost_per_million = 2.5  # USD per million input tokens
                output_cost_per_million = 10  # USD per million output tokens

            elif model == "gpt-4-turbo":
                # Pricing details for GPT-4-turbo
                input_cost_per_million = 10  # USD per million input tokens
                output_cost_per_million = 30  # USD per million output tokens
            
            elif model == "o1-preview":
                # Pricing details for GPT-4-turbo
                input_cost_per_million = 15  # USD per million input tokens
                output_cost_per_million = 60  # USD per million output tokens

            elif model == "o1-mini":
                # Pricing details for GPT-4-turbo
                input_cost_per_million = 3  # USD per million input tokens
                output_cost_per_million = 12  # USD per million output tokens

            # Calculate the cost for input and output tokens
            input_cost = (input_tokens / 1_000_000) * input_cost_per_million
            output_cost = (output_tokens / 1_000_000) * output_cost_per_million
            total_cost = input_cost + output_cost

            return total_cost

        def find_closest_address(address, toscana_address=toscana_address,model=model,api_key = api_key):
            
            client = OpenAI(api_key = api_key)
            
            prompt = f''' You will be provvided with an address. Please find the best match for this address among all the elements in this list {toscana_address}.
            Please base your decision on the similarity of the name (ideally it is the same name written differently).
            only if you are not 100% sure about the match, please return "None".
            It is important that you only return the selected address without any additional expalantion not comments.'''
            response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": str(address)}
            ],
            temperature=0
            )
            costo = check_cost(response, model = model)
            response=response.choices[0].message.content
            
            print('questo esercizio é costato: ',costo)
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
                print(' nessun indirizzo trovato per ', indirizzo)
                indirizzo_match_toscana.append(None)

        indirizzi_match_df = pd.DataFrame()
        indirizzi_match_df['indirizzo_elenchi'] = indirizzo_elenchi
        indirizzi_match_df['indirizzo_toscana'] = indirizzo_match_toscana
        csv_data = indirizzi_match_df.to_csv(index=False)
        st.write('questo esercizio in totale é costato: ',costo_t)
        st.download_button(
            label="Download results File",
            data=csv_data,
            file_name=f'indice_indirizzi_opeai_{model}.csv',
            mime="text/csv",
        )

def run() -> None:
    # Streamlit app title
    st.title("The Match Assistant!(OpenAI)")
    st.write("Please load your files to continue.")
    api_key = st.text_input("<inserisci qui la tua OpenAI api_key>")
    model = st.text_input("please select the model to use: ", "gpt-4o-mini")
    if api_key and  model:
        Open_AI_solution(model =  model,api_key=api_key)
    
    if __name__ == "__main__":
        run()
