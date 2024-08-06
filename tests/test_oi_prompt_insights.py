import unittest
import streamlit as st
from streamlit import session_state
from oi_prompt_insights import (
    sidebar_navigation,
    render_about_page,
    render_record_prompt_page,
    render_analytics_page,
    render_insights_page,
)

class TestOIPromptInsights(unittest.TestCase):

    def setUp(self):
        session_state.prompts = []

    def test_sidebar_navigation(self):
        with st.sidebar:
            page = sidebar_navigation()
            self.assertIn(page, ["About", "Record Prompt", "Analytics", "Insights"])

    def test_render_about_page(self):
        render_about_page()
        self.assertIn("Open Interpreter Prompt Insights Tool", st._main.title)

    def test_render_record_prompt_page(self):
        render_record_prompt_page()
        self.assertIn("Record Prompt Results", st._main.title)

    def test_render_analytics_page(self):
        render_analytics_page()
        self.assertIn("Prompt Performance Analytics", st._main.title)

    def test_render_insights_page(self):
        render_insights_page()
        self.assertIn("In-depth Insights", st._main.title)

    def test_prompt_recording(self):
        with st.form("prompt_form"):
            st.selectbox("Task Category", ["Text Processing"])
            st.text_area("Prompt Used", "Test Prompt")
            st.number_input("Execution Time (seconds)", min_value=0.0, step=0.1, value=1.0)
            st.radio("Task Completed Successfully?", ["Yes"])
            st.radio("Was this prompt satisfactory?", ["👍 Yes"])
            st.text_area("Additional Comments", "Test Comment")
            st.file_uploader("Attach a file (optional)", type=["txt"])
            st.form_submit_button("Submit Results")

        self.assertEqual(len(session_state.prompts), 1)
        self.assertEqual(session_state.prompts[0]["Task Category"], "Text Processing")
        self.assertEqual(session_state.prompts[0]["Prompt Text"], "Test Prompt")
        self.assertEqual(session_state.prompts[0]["Execution Time"], 1.0)
        self.assertEqual(session_state.prompts[0]["Task Completion"], "Yes")
        self.assertEqual(session_state.prompts[0]["User Satisfaction"], "👍 Yes")
        self.assertEqual(session_state.prompts[0]["Additional Comments"], "Test Comment")

    def test_analytics_calculations(self):
        session_state.prompts = [
            {"Task Category": "Text Processing", "User Satisfaction": "👍 Yes", "Execution Time": 1.0, "Task Completion": "Yes"},
            {"Task Category": "Text Processing", "User Satisfaction": "👎 No", "Execution Time": 2.0, "Task Completion": "No"},
        ]
        render_analytics_page()
        df = pd.DataFrame(session_state.prompts)
        analytics_df = df.groupby("Task Category").agg({
            "User Satisfaction": lambda x: (x == "👍 Yes").mean(),
            "Execution Time": "mean",
            "Task Completion": lambda x: (x == "Yes").mean(),
        }).reset_index()
        self.assertEqual(analytics_df.loc[0, "Satisfaction Rate"], 50.0)
        self.assertEqual(analytics_df.loc[0, "Avg Execution Time"], 1.5)
        self.assertEqual(analytics_df.loc[0, "Success Rate"], 50.0)

if __name__ == "__main__":
    unittest.main()
