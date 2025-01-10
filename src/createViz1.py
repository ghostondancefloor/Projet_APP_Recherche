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

# Streamlit App
st.title("Researcher Publication Tracker")

# Sidebar for filters
st.sidebar.title("Filters")

# Sort researchers alphabetically
sorted_researchers = ['All Researchers'] + sorted(df['customAuthorName'].unique())

# Select the researcher to view their publications
researcher = st.sidebar.selectbox("Select Researcher", sorted_researchers)

# Time period filter (year range slider)
start_year, end_year = st.sidebar.slider(
    "Select time period",
    min_value=int(df['publicationYear'].min()),  # Ensure min_value is int
    max_value=int(df['publicationYear'].max()),  # Ensure max_value is int
    value=(2005, 2010),
    step=1
)

# Choose whether to view the data by Month or Year
view_by = st.sidebar.radio("View publications by:", ("Month", "Year"))

# Filter the data by the selected time period
filtered_df = df[(df['publicationYear'] >= start_year) & (df['publicationYear'] <= end_year)]

# Further filter by researcher selection
if researcher != 'All Researchers':
    filtered_df = filtered_df[filtered_df['customAuthorName'] == researcher]

# Debug output for filtered data
st.sidebar.subheader("Debugging Info")
st.sidebar.write("Filtered Dataframe", filtered_df)

if view_by == "Month":
    # Group by Month and Count publications
    publication_count_by_month = filtered_df.groupby('publicationMonth').size().reset_index(name='count')

    # Convert the publicationMonth to a string format 'YYYY-MM' for better display on the X-axis
    publication_count_by_month['publicationMonth'] = publication_count_by_month['publicationMonth'].dt.strftime('%Y-%m')

    # Plot using Plotly for better interactivity
    fig = px.bar(publication_count_by_month, x='publicationMonth', y='count', 
                 title=f"Publications per Month by {researcher}" if researcher != 'All Researchers' else "Publications per Month for All Researchers",
                 labels={'publicationMonth': 'Month', 'count': 'Number of Publications'})

    # Show the plot
    st.plotly_chart(fig)

elif view_by == "Year":
    # Group by Year and Count publications
    publication_count_by_year = filtered_df.groupby('publicationYear').size().reset_index(name='count')

    # Plot using Plotly
    fig = px.bar(publication_count_by_year, x='publicationYear', y='count', 
                 title=f"Publications per Year by {researcher}" if researcher != 'All Researchers' else "Publications per Year for All Researchers",
                 labels={'publicationYear': 'Year', 'count': 'Number of Publications'})

    st.plotly_chart(fig)

# Show raw data as a table
st.subheader("Raw Data")
st.dataframe(filtered_df)
