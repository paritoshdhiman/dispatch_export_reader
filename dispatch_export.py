import pandas as pd
import json
import streamlit as st

st.set_page_config(layout='wide')


dracula_css = """
<style>
body {
    background-color: #282a36;
    color: #f8f8f2;
}
.stApp {
    background-color: #282a36;
}
header {
    background-color: #44475a;
}
.css-1q8dd3e {  /* Sidebar background color */
    background-color: #44475a;
}
.css-1v0mbdj {  /* Primary buttons */
    background-color: #bd93f9;
    color: #282a36;
}
.css-1pahdxg {  /* Secondary buttons */
    background-color: #6272a4;
    color: #f8f8f2;
}
</style>
"""

st.markdown(dracula_css, unsafe_allow_html=True)

footer = """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f9f9f9;
            text-align: right;
            padding: 10px;
            font-size: 14px;
            color: #333;
            border-top: 1px solid #eaeaea;
        }
    </style>
    <div class="footer">
        Made with <span style="color: red;">&hearts;</span> {'_id': 'BSD';}
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)

st.markdown(
    """
    <center><a href="https://libertyenergy.com" target="_blank">
        <img src="https://libertyenergy.com/wp-content/uploads/2022/02/los-footer-logo-white.png" alt="Liberty Energy" width="" height="100">
    </a></center>
    """,
    unsafe_allow_html=True
)
st.header("Database Export Breakdown")

crew = st.selectbox('CrewName', options=["",
        "Alliance", "PM Warehouse", "Legacy", "Olympus", "Phantom",
        "Phoenix", "Spartan", "Vapor", "EF Warehouse", "Apache", "DJ Warehouse",
        "Raptor", "DJ Special Services", "BK Special Services", "PR Warehouse",
        "SJ Warehouse", "Discovery", "Fuel", "HazCom", "Browning",
        "WT Special Services", "Independence", "Valor", "Dynasty", "Eclipse",
        "Apex", "Sabre", "Titan", "Easy Company", "Charlie Company", "Cobra",
        "Reaper", "Patriot", "Nighthawk", "Falcon", "Spitfire", "Ironside",
        "Northern Thunder", "Honey Badgers", "HV Warehouse", "MC Warehouse",
        "Constitution", "WC Warehouse", "Republic", "Scorpion", "AP Warehouse",
        "WT SS 2", "Saturn", "Revolution", "Spectre", "Kiowa", "Remington",
        "Barrett", "Ghostrider", "Atlantis", "Lonestar", "Other Warehouse",
        "Rebels", "Justice", "Renegade", "UT Warehouse", "Anthem", "Endeavour", "Wallaroo", "AU Warehouse",
        "BK Warehouse", "Freedom"
    ])


export_file = st.file_uploader('Database JSON')


if export_file is not None:
    data = json.load(export_file)

    collections = data.get("collections", [])

    priority_names = ["shipments", "locations"]
    priority_collections = []
    other_collections = []

    for collection in collections:
        collection_name = collection.get("name", "")
        if collection_name in priority_names:
            priority_collections.append(collection)
        else:
            other_collections.append(collection)

    sorted_collections = priority_collections + other_collections

    for collection in sorted_collections:
        collection_name = collection.get("name", "Unknown Collection")
        docs = collection.get("docs", [])

        # Flatten and convert "docs" to a DataFrame
        if docs:
            df = pd.json_normalize(docs)
            st.subheader(f"Collection: {collection_name}")
            if collection_name == 'shipments':
                df = df[(df['receiverLocation.owner.name'] == crew) | (df['shipperLocation.owner.name'] == crew)].reset_index(drop=True)
                df['items'] = df['items'].astype(str)
                df['notes'] = df['notes'].astype(str)
                st.write(df.sort_values(by=['status'], ascending=[False], inplace=False))
            elif collection_name == 'locations':
                st.write(df[df['owner.name'] == crew].reset_index(drop=True))
            else:
                st.write(df)
        else:
            st.warning(f"No docs found in collection: {collection_name}")
