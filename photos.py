import os
import polars as pl


import sqlite3
from pathlib import Path
import polars as pl

# df = pl.from_dicts(vec)

DB_LOCATION_OTHER = (Path.home() / "Pictures/photos.sqlite").as_posix()

DB_LOCATION = (Path.home() 
                 / "Pictures/Photos Library.photoslibrary/database/Photos.sqlite"
                 ).as_posix()

def query(sql):
    db_path = DB_LOCATION 

    sqliteConnection = sqlite3.connect(db_path)
    cursor = sqliteConnection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    # Create a list of dictionaries
    results_with_keys = [dict(zip(columns, result)) for result in results]
    return results_with_keys

def get_raw_df():
    vec = query(
        """
    SELECT 
        strftime('%Y-%m-%d', (ZASSET.ZDATECREATED + 978307200), 'unixepoch'
        ) AS date_created,
        ZFILENAME as filename
        
    FROM ZASSET
    -- limit 10
        """
    )
    df = pl.from_dicts(vec)
    df = df.with_columns(
        (pl.col("filename").str.split(".").list.last().str.to_lowercase().alias("extension"))
    )
    return df

def get_original_names():

    cols = ["ZORIGINALFILENAME", "ZEXIFTIMESTAMPSTRING","ZORIGINALFILESIZE", "ZLOCATIONHASH", "ZORIGINALWIDTH",
"ZORIGINALHEIGHT", ]
    sql = f"select {', '.join(cols)} from ZADDITIONALASSETATTRIBUTES  "
    vec = query(sql)
    # return vec
    df = pl.from_dicts(vec) # .select(cols)
    return df

def get_primary():
    sql = "select * from Z_METADATA "
    vec = query(sql)
    # return vec
    df = pl.from_dicts(vec) # .select(cols)
    return df
