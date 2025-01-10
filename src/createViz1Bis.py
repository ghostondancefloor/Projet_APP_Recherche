import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data from the CSV file
df = pd.read_csv('../fluxdonnee/hal_results.csv')

# Standardize date format for incomplete dates
def preprocess_dates(date_str):
    if pd.isna(date_str):
        return None
    if len(date_str) == 4:  # Year only (e.g., "2010")
        return f"{date_str}-01-01"
    elif len(date_str) == 7:  # Year and month only (e.g., "2005-05")
        return f"{date_str}-01"
    return date_str  # Full date (e.g., "2005-05-01")

df['publicationDate_s'] = df['publicationDate_s'].apply(preprocess_dates)
df['publicationDate_s'] = pd.to_datetime(df['publicationDate_s'], errors='coerce')

# Check for invalid or missing dates after preprocessing
invalid_dates = df[df['publicationDate_s'].isna()]
if not invalid_dates.empty:
    st.sidebar.warning(f"{len(invalid_dates)} rows have invalid or missing dates after preprocessing.")

# Create a 'year' and 'month' column for the publication dates
df['publicationYear'] = df['publicationDate_s'].dt.year
df['publicationMonth'] = df['publicationDate_s'].dt.to_period('M')

# Streamlit App for USMB (Université Savoie Mont Blanc)
st.title("USMB Publication Tracker")

# Sidebar for filters
st.sidebar.title("Filters")

# Time period filter (year range slider)
start_year, end_year = st.sidebar.slider(
    "Select time period",
    min_value=int(df['publicationYear'].min()),  # Ensure min_value is int
    max_value=int(df['publicationYear'].max()),  # Ensure max_value is int
    value=(2005, 2010),
    step=1
)

# Filter the data by the selected time period for USMB publications
# Now filtering by 'instStructName_s' column
usmb_df = df[df['instStructName_s'].str.contains('Université Savoie Mont Blanc', na=False)]  # Use 'instStructName_s' column

# Further filter by the selected time range
usmb_filtered_df = usmb_df[(usmb_df['publicationYear'] >= start_year) & (usmb_df['publicationYear'] <= end_year)]

# Choose whether to view the data by Month or Year
view_by = st.sidebar.radio("View publications by:", ("Month", "Year"))

if view_by == "Month":
    # Group by Month and Count publications
    publication_count_by_month = usmb_filtered_df.groupby('publicationMonth').size().reset_index(name='count')

    # Convert the publicationMonth to a string format 'YYYY-MM' for better display on the X-axis
    publication_count_by_month['publicationMonth'] = publication_count_by_month['publicationMonth'].dt.strftime('%Y-%m')

    # Plot using Plotly for better interactivity
    fig = px.bar(publication_count_by_month, x='publicationMonth', y='count', 
                 title="USMB Publications per Month",
                 labels={'publicationMonth': 'Month', 'count': 'Number of Publications'})

    # Show the plot
    st.plotly_chart(fig)

elif view_by == "Year":
    # Group by Year and Count publications
    publication_count_by_year = usmb_filtered_df.groupby('publicationYear').size().reset_index(name='count')

    # Plot using Plotly
    fig = px.bar(publication_count_by_year, x='publicationYear', y='count', 
                 title="USMB Publications per Year",
                 labels={'publicationYear': 'Year', 'count': 'Number of Publications'})
    st.plotly_chart(fig)

# Show raw data as a table
st.subheader("Raw Data")
st.dataframe(usmb_filtered_df)
