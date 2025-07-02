import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os # For checking file existence if needed


st.set_page_config(
    page_title="Project Data Dashboard",
    page_icon="📊",
    layout="wide" 
)

DATA_PATH = 'cleaned_project_data.xlsx'

@st.cache_data # Cache data loading to improve performance
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Data file not found at: {path}")
        return pd.DataFrame() # Return empty DataFrame on error
    try:
        df = pd.read_excel(path, sheet_name='Cleaned Data')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data(DATA_PATH)

if df.empty:
    st.stop() # Stop execution if data failed to load


st.title("📊 Project Performance Dashboard")
st.markdown("Explore key insights from cleaned project data.")


st.sidebar.header("Filter Options")


if 'Project Type' in df.columns:
    project_types = df['Project Type'].unique().tolist()
    selected_project_type = st.sidebar.multiselect(
        "Select Project Type(s)",
        options=project_types,
        default=project_types # Select all by default
    )
    df_filtered = df[df['Project Type'].isin(selected_project_type)]
else:
    df_filtered = df # No filtering if column not found
    st.sidebar.warning(" 'Project Type' column not found for filtering.")


if 'Status' in df.columns:
    status_options = df['Status'].unique().tolist()
    selected_status = st.sidebar.multiselect(
        "Select Project Status(es)",
        options=status_options,
        default=status_options
    )
    df_filtered = df_filtered[df_filtered['Status'].isin(selected_status)]
else:
     st.sidebar.warning(" 'Status' column not found for filtering.")



st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3) # Create 3 columns for KPIs

with col1:
    total_projects = df_filtered['Total Projects'].sum() if 'Total Projects' in df_filtered.columns else 0
    st.metric(label="Total Projects", value=int(total_projects))
with col2:
    # Assuming 'Budget Utilized' is in original currency value (not percentage)
    avg_budget_utilization = (df_filtered['Budget Utilized'].sum() / df_filtered['Budget Allocated'].sum() * 100) if (
        'Budget Utilized' in df_filtered.columns and 'Budget Allocated' in df_filtered.columns and df_filtered['Budget Allocated'].sum() > 0
    ) else 0
    st.metric(label="Avg Budget Utilization", value=f"{avg_budget_utilization:.2f}%")
with col3:
    # Assuming 'Citizen Satisfaction Rate' is already 0-1 scale for plotting or 0-100 for display
    # If it's already divided by 100 in the Excel, multiply by 100 for display in KPI
    avg_satisfaction = df_filtered['Citizen Satisfaction Rate'].mean() * 100 if 'Citizen Satisfaction Rate' in df_filtered.columns else 0
    st.metric(label="Avg Citizen Satisfaction", value=f"{avg_satisfaction:.2f}%")


st.subheader("Visualizations")

# Bar chart: Projects by Status
if 'Status' in df_filtered.columns:
    status_counts = df_filtered['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig_status = px.bar(
        status_counts,
        x='Status',
        y='Count',
        title='Number of Projects by Status',
        color='Status'
    )
    st.plotly_chart(fig_status, use_container_width=True)


if 'Budget Allocated' in df_filtered.columns and 'Project Type' in df_filtered.columns:
    budget_by_type = df_filtered.groupby('Project Type')['Budget Allocated'].sum().reset_index()
    fig_budget_pie = px.pie(
        budget_by_type,
        values='Budget Allocated',
        names='Project Type',
        title='Budget Allocation by Project Type'
    )
    st.plotly_chart(fig_budget_pie, use_container_width=True)


if 'Year' in df_filtered.columns and 'Budget Utilization Percentage' in df_filtered.columns:
   
    df_filtered['Budget Utilization Display'] = df_filtered['Budget Utilization Percentage'] * 100 

    utilization_trend = df_filtered.groupby('Year')['Budget Utilization Display'].mean().reset_index()
    fig_util_trend = px.line(
        utilization_trend,
        x='Year',
        y='Budget Utilization Display',
        title='Average Budget Utilization Trend',
        markers=True
    )
    fig_util_trend.update_yaxes(title_text='Budget Utilization (%)')
    st.plotly_chart(fig_util_trend, use_container_width=True)
elif 'Budget Utilization Percentage' in df_filtered.columns:
     st.info("To show Budget Utilization Trend, ensure a 'Year' column exists in your data.")

# --- Raw Data Display (Optional) ---
st.subheader("Filtered Raw Data")
st.dataframe(df_filtered)

st.markdown("---")
st.markdown("Dashboard created with Streamlit.")
