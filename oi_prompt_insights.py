import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64

# App configuration
st.set_page_config(page_title="Open Interpreter Prompt Insights Tool", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if 'prompts' not in st.session_state:
    st.session_state.prompts = []

# Import custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar navigation
def sidebar_navigation():
    st.sidebar.title("")
    page = st.sidebar.radio("Go to", ["About", "Record Prompt", "Analytics", "Insights"])
    return page

# Page content rendering
def render_about_page():
    st.title("Open Interpreter Prompt Insights Tool")
    st.markdown("""
    Welcome to the Open Interpreter Prompt Insights Tool!

    This tool helps you track and analyze the effectiveness of prompts used in common tasks. 
    Our goal is to collect data and generate insights that can be shared with the project team and end users.

    **Key Features:**
    - Record prompt performance for various tasks
    - Attach relevant files to your prompt records
    - Analyze prompt effectiveness through interactive visualizations
    - Discover best practices and tips for crafting effective prompts

    Get started by recording your prompt results or exploring the analytics dashboard!
    """)

def render_record_prompt_page():
    st.title("Record Prompt Results")

    with st.form("prompt_form"):
        task_category = st.selectbox(
            "Task Category",
            ["Text Processing", "Code Generation", "Data Analysis", "Image Analysis", "Audio Processing", "Other"],
        )
        prompt_text = st.text_area("Prompt Used", help="Enter the exact prompt you used for this task")
        execution_time = st.number_input(
            "Execution Time (seconds)", min_value=0.0, step=0.1, help="How long did the task take to complete?"
        )
        task_completion = st.radio("Task Completed Successfully?", ["Yes", "No"])
        user_satisfaction = st.radio("Was this prompt satisfactory?", ["👍 Yes", "👎 No"], index=None)
        additional_comments = st.text_area("Additional Comments (optional)")

        uploaded_file = st.file_uploader("Attach a file (optional)", type=["txt", "pdf", "png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Submit Results")

        if submitted:
            if task_category and prompt_text and execution_time is not None and user_satisfaction:
                prompt_data = {
                    "Task Category": task_category,
                    "Prompt Text": prompt_text,
                    "Execution Time": execution_time,
                    "Task Completion": task_completion,
                    "User Satisfaction": user_satisfaction,
                    "Additional Comments": additional_comments,
                    "Timestamp": datetime.now().isoformat(),
                }

                if uploaded_file is not None:
                    file_contents = uploaded_file.read()
                    encoded_file = base64.b64encode(file_contents).decode()
                    prompt_data["Attachment"] = {
                        "filename": uploaded_file.name,
                        "content": encoded_file,
                        "type": uploaded_file.type,
                    }

                st.session_state.prompts.append(prompt_data)
                st.success("Thank you! Your results have been recorded successfully.")
            else:
                st.error("Please fill in all required fields.")

def render_analytics_page():
    st.title("Prompt Performance Analytics")

    if not st.session_state.prompts:
        st.info("No prompt data recorded yet. Start by recording your prompt results!")
    else:
        df = pd.DataFrame(st.session_state.prompts)

        analytics_df = df.groupby("Task Category").agg({
            "User Satisfaction": lambda x: (x == "👍 Yes").mean(),
            "Execution Time": "mean",
            "Task Completion": lambda x: (x == "Yes").mean(),
        }).reset_index()

        analytics_df.columns = ["Task Category", "Satisfaction Rate", "Avg Execution Time", "Success Rate"]
        analytics_df["Satisfaction Rate"] *= 100
        analytics_df["Success Rate"] *= 100

        st.subheader("Quick Stats")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Prompts", len(df))
        with col2:
            st.metric("Top Category", analytics_df.loc[analytics_df["Satisfaction Rate"].idxmax(), "Task Category"])
        with col3:
            st.metric("Highest Satisfaction Rate", f"{analytics_df['Satisfaction Rate'].max():.1f}%")
        with col4:
            st.metric("Fastest Execution", f"{analytics_df['Avg Execution Time'].min():.2f}s")

        st.subheader("Performance Insights")
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(analytics_df, x="Task Category", y="Satisfaction Rate", title="Satisfaction Rate by Task Category")
            fig1.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.bar(analytics_df, x="Task Category", y="Success Rate", title="Success Rate by Task Category")
            fig2.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Detailed Data")
        st.dataframe(analytics_df)

def render_insights_page():
    st.title("In-depth Insights")
    
    st.markdown("""
    <div style="text-align: center; padding: 50px; background-color: var(--card-bg); border-radius: 10px;">
        <h2>Coming Soon!</h2>
        <p>We're working on bringing you more detailed insights and analytics. Check back later for updates!</p>
    </div>
    """, unsafe_allow_html=True)

# Main application logic
page = sidebar_navigation()

if page == "About":
    render_about_page()
elif page == "Record Prompt":
    render_record_prompt_page()
elif page == "Analytics":
    render_analytics_page()
elif page == "Insights":
    render_insights_page()

# Footer
st.sidebar.markdown("---")
st.sidebar.info("OI Prompt Insights - v1.0")

# Session State Management
if st.sidebar.button("Clear All Data"):
    st.session_state.prompts = []
    st.sidebar.success("All data has been cleared.")

# Display current data count
prompt_count = len(st.session_state.prompts)
st.sidebar.metric("Recorded Prompts", prompt_count)
