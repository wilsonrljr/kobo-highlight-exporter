""" Utils methods for Kobo highlights export"""

import sqlite3
from io import BytesIO
from pathlib import Path
from sqlite3 import Connection, Error

import pandas as pd
import streamlit as st
from PIL import Image

QUERY_ITEMS = """ SELECT
        Bookmark.VolumeID as 'id'
        , content.Title as 'title'
        , content.BookTitle as 'book_title'
        , Bookmark.Text as 'highlight'
        , Bookmark.Annotation as 'user_comments'
        , Bookmark.ExtraAnnotationData as 'extra_comment_date'
        , Bookmark.DateCreated as 'dt_creation'
        , Bookmark.DateModified as 'dt_modified'
        , content.Attribution as 'author'
        FROM Bookmark
        INNER JOIN content
            ON Bookmark.VolumeID = content.ContentID
        """

QUERY_BOOKS = """ SELECT DISTINCT
        Bookmark.VolumeID
        , content.BookTitle
        , content.Title
        , content.Attribution
        FROM Bookmark INNER JOIN content
            ON Bookmark.VolumeID = content.ContentID
            ORDER BY content.Title
        """


@st.experimental_singleton  # @st.cache(allow_output_mutation=True)
def create_connection(db_file):
    """create a sqlite3 database connection."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        return None


def get_project_path():
    """Returns project root path."""
    return str(Path(__file__).parent)


@st.cache(ttl=600)
def load_image(image_name):
    """Load logo from project folder."""
    return Image.open(Path(get_project_path()) / f"{image_name}")


@st.cache(hash_funcs={Connection: id}, ttl=600)  # @st.experimental_memo(ttl=600)
def read_data(options, option, connection):
    """Run query based on user input"""
    return pd.read_sql(options[option], con=connection)


def convert_to_excel(df):
    """convert to xlsx file. Taken from.

    Copy/past from https://discuss.streamlit.io/t/download-button-for-csv-or-xlsx-file/17385/3
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    format1 = workbook.add_format({"num_format": "0.00"})
    worksheet.set_column("A:A", None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data
