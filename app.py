import streamlit as st
import pdfplumber
import pandas as pd
import json

st.title("Pathways Advisement")

uploaded_file = st.file_uploader('Provide your Degree Progress Report (DPR)', type = 'pdf')
if uploaded_file is not None:
    fields = ['Term', 'Subject', 'Catalog Nbr', 'Course Title', 'Grade', 'Units', 'Type']
    df = pd.DataFrame(columns = fields)

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if table[0] == fields:
                    for row in table[1:]:
                        df.loc[len(df)] = row

    st.dataframe(df)

file = open('Utilities/majors/major_paths.json')
offerings = json.load(file)
offerings = offerings.keys()
file.close()

st.selectbox("Select your major", offerings, None)
