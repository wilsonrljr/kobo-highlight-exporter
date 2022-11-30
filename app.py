""" Main page of Kobo highlight exporter"""
import pathlib
import uuid
from sqlite3 import Error
import streamlit as st
from utils import (
    create_connection,
    QUERY_BOOKS,
    QUERY_ITEMS,
    load_image,
    read_data,
    convert_to_excel,
)


options = {"Books": QUERY_BOOKS, "Items": QUERY_ITEMS}
df = None
connection = None
# Page config
st.set_page_config(page_title="Note", layout="wide")

with st.expander("Export notes and highlights from Kobo", expanded=False):
    st.write("This is an app to export notes from Kobo")
    st.write("")

st.write("")
st.sidebar.image(load_image("kobo-logo.jpg"), use_column_width=True)

st.sidebar.title("1. Database")

# Load data

with st.sidebar.expander("Database", expanded=True):
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file:
        fp = pathlib.Path(str(uuid.uuid4()))
        try:
            fp.write_bytes(uploaded_file.getvalue())
            connection = create_connection(str(fp))
        except Error as e:
            raise e


# Column names
with st.sidebar.expander("Options", expanded=True):
    # option = st.multiselect("What do you want to download?", list(options.keys()))
    option = st.selectbox(
        label="What do you want to download?",
        options=(list(options.keys())[0], list(options.keys())[1]),
    )
    st.write("You selected:", option)
    if option and connection is not None:
        data_load_state = st.text("Loading data...")
        df = read_data(options, option, connection)
        data_load_state.text("Done! (using st.cache)")

# Filtering
with st.sidebar.expander("Filtering", expanded=True):
    if option and df is not None:
        cols = st.multiselect("What columns do you want to see?", df.columns)
        df = df[cols]
        st.write(f"You're using the following columns: {cols}")

if st.checkbox("Show data"):
    st.table(df)


download = st.sidebar.checkbox("Download Data", value=False)

if download:
    with st.sidebar.expander("Click here to download", expanded=False):
        if df is not None:
            df_xlsx = convert_to_excel(df)
            st.download_button(
                label="📥 Download Current Result",
                data=df_xlsx,
                file_name="df_test.xlsx",
            )
        else:
            st.write("There is not data to export!")
