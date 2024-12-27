import pandas as pd
import json
import streamlit as st

# Streamlit configuration and styling
st.set_page_config(layout="wide")

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
"""
st.markdown(dracula_css, unsafe_allow_html=True)

st.markdown(
    """
    <center><a href="https://libertyenergy.com" target="_blank">
        <img src="https://libertyenergy.com/wp-content/uploads/2022/02/los-footer-logo-white.png" alt="Liberty Energy" height="100">
    </a></center>
    <div class="footer">
        Made with <span style="color: red;">&hearts;</span> {'_id': 'BSD';}
    </div>
    """,
    unsafe_allow_html=True,
)

# Utility functions
def normalize_and_filter(docs, crew=None, collection_type=None):
    """Normalize and filter the collection data."""
    df = pd.json_normalize(docs) if docs else pd.DataFrame()
    if collection_type == "shipments":
        df = df[
            (df["receiverLocation.owner.name"] == crew) | (df["shipperLocation.owner.name"] == crew)
        ].reset_index(drop=True)
    elif collection_type == "locations":
        df = df[df["owner.name"] == crew].reset_index(drop=True)
    return df

def compare_dataframes(df1, df2):
    unique_in_1 = df1[df1["id"].isin(set(df1["id"]).difference(set(df2["id"])))]
    unique_in_1 = unique_in_1[unique_in_1['id'] != unique_in_1['code']].reset_index(drop=True)
    unique_in_1['items'] = unique_in_1['items'].astype(str)
    unique_in_1['notes'] = unique_in_1['notes'].astype(str)

    unique_in_2 = df2[df2["id"].isin(set(df2["id"]).difference(set(df1["id"])))].reset_index(drop=True)
    unique_in_2['items'] = unique_in_2['items'].astype(str)
    unique_in_2['notes'] = unique_in_2['notes'].astype(str)

    common = df1[df1["id"].isin(set(df1["id"]).intersection(set(df2["id"])))].reset_index(drop=True)
    common['items'] = common['items'].astype(str)
    common['notes'] = common['notes'].astype(str)

    return unique_in_1, unique_in_2, common

# Sidebar controls
st.header("Database Export Breakdown")
c1, c2 = st.columns(2)
with c1:
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
with c2:
    op_type = st.selectbox("Operation Type", options=["Extract JSON", "Compare JSONs"])

# File uploads
if op_type == "Extract JSON":
    export_file = st.file_uploader("Database JSON")
else:
    with c1:
        export_file = st.file_uploader("Database JSON - 1")
    with c2:
        export_file_2 = st.file_uploader("Database JSON - 2")

if crew == '':
    st.write('Select a crew!')

execute_op = st.button("Execute")

# Operations
if execute_op:
    if op_type == "Extract JSON" and export_file:
        data = json.load(export_file)
        collections = data.get("collections", [])

        # Sort collections by priority
        priority_names = ["shipments", "locations"]
        sorted_collections = sorted(
            collections, key=lambda col: priority_names.index(col["name"]) if col["name"] in priority_names else len(priority_names)
        )

        # Display each collection
        for collection in sorted_collections:
            collection_name = collection.get("name", "Unknown Collection")
            docs = collection.get("docs", [])
            df = normalize_and_filter(docs, crew, collection_name)
            if not df.empty:
                if collection_name == 'shipments':
                    st.subheader(f"Collection: {collection_name}")
                    df['items'] = df['items'].astype(str)
                    df['notes'] = df['notes'].astype(str)
                    st.dataframe(df)
                else:
                    st.dataframe(df)
            else:
                st.warning(f"No data found for {collection_name}.")

    elif op_type == "Compare JSONs" and export_file and export_file_2:
        # Load JSON data
        data1 = json.load(export_file)
        data2 = json.load(export_file_2)

        # Extract and compare `shipments` collection
        docs1 = next((col["docs"] for col in data1.get("collections", []) if col["name"] == "shipments"), [])
        docs2 = next((col["docs"] for col in data2.get("collections", []) if col["name"] == "shipments"), [])
        df1 = pd.json_normalize(docs1) if docs1 else pd.DataFrame()
        df2 = pd.json_normalize(docs2) if docs2 else pd.DataFrame()

        unique_in_1, unique_in_2, common = compare_dataframes(df1, df2)

        # Display results
        st.subheader("Comparison for Shipments Collection")
        if not unique_in_1.empty:
            st.write("Unique to JSON 1:")
            st.dataframe(unique_in_1)
        if not unique_in_2.empty:
            st.write("Unique to JSON 2:")
            st.dataframe(unique_in_2)
        if not common.empty:
            st.write("Common elements:")
            st.dataframe(common)
    else:
        st.error("Please upload the required JSON file(s).")
