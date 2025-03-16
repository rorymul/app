import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import os
import datetime

# --- Config ---
st.set_page_config(page_title="Irish Pension Simulator", page_icon="💰", layout="wide")

# CSV filenames
COMMUNITY_FILE = "community_data.csv"  # Stores user simulation results
COMMENTS_FILE = "comments_data.csv"    # Stores user comments

def load_community_data():
    """Load the community data from CSV, or create an empty DataFrame if not found."""
    if os.path.exists(COMMUNITY_FILE):
        return pd.read_csv(COMMUNITY_FILE)
    else:
        return pd.DataFrame(columns=[
            "Username",
            "Final Balance (CUAN)",
            "Final Balance (Auto-Enrolment)",
            "Target Savings",
            "Year Reached Target"
        ])

def save_community_data(df):
    df.to_csv(COMMUNITY_FILE, index=False)

def load_comments_data():
    """Load the comments data from CSV, or create an empty DataFrame if not found."""
    if os.path.exists(COMMENTS_FILE):
        return pd.read_csv(COMMENTS_FILE)
    else:
        return pd.DataFrame(columns=[
            "Timestamp",
            "Commenter",
            "TargetUser",
            "Comment"
        ])

def save_comments_data(df):
    df.to_csv(COMMENTS_FILE, index=False)

def display_community_board():
    """Display the community board with all user results."""
    st.markdown("## Community Board")
    community_df = load_community_data()
    if community_df.empty:
        st.info("No community data found yet. Run a simulation and share your results to populate the board!")
    else:
        st.dataframe(community_df.style.format("{:,.2f}"))

def display_comments_section():
    """Display the comments section where users can see and post comments."""
    st.markdown("## Discussion & Comments")
    community_df = load_community_data()
    comments_df = load_comments_data()

    if community_df.empty:
        st.info("No users in the community board yet. Run a simulation and share results first!")
        return

    st.subheader("All Comments")
    if comments_df.empty:
        st.info("No comments yet. Be the first to comment!")
    else:
        comments_df = comments_df.sort_values(by="Timestamp", ascending=False)
        st.table(comments_df)

    st.subheader("Add a New Comment")
    commenter_name = st.text_input("Your name (or nickname):", "Anonymous")
    target_user = st.selectbox("Which user do you want to comment on?", community_df["Username"].unique())
    comment_text = st.text_area("Your comment here:")

    if st.button("Post Comment"):
        if not comment_text.strip():
            st.warning("Please enter a comment before posting.")
        else:
            new_comment = {
                "Timestamp": datetime.datetime.now().isoformat(timespec='seconds'),
                "Commenter": commenter_name,
                "TargetUser": target_user,
                "Comment": comment_text
            }
            comments_df = comments_df.append(new_comment, ignore_index=True)
            save_comments_data(comments_df)
            st.success("Your comment has been posted!")
            st.experimental_rerun()

def run_pension_simulator():
    st.title("💰 CUAN: Helping you save for retirement! 💰")
    st.write("""
    We want to help you save for your future and allow you to retire with enough to support yourself!
    Run our simulation and edit the parameters so you can see how much money you need to start saving and 
    how changing your contributions in just the first 5 years of working will make a big change to potential savings!
    """)

    # --- User Inputs ---
    col1, col2, col3 = st.columns(3)
    with col1:
        starting_salary = st.number_input("Starting Salary (€):", value=50000.0, step=1000.0)
        salary_increase_rate_early = st.number_input("Early Salary Increase Rate (e.g., 0.10):", value=0.10, step=0.01, format="%.2f")
    with col2:
        salary_increase_rate_late = st.number_input("Late Salary Increase Rate (e.g., 0.02):", value=0.02, step=0.01, format="%.2f")
        pension_contribution_rate = st.number_input("Pension Contribution Rate (e.g., 0.10):", value=0.10, step=0.01, format="%.2f")
    with col3:
        increase_contribution_rate = st.number_input("Increase Contribution Rate (e.g., 0.60):", value=0.60, step=0.05, format="%.2f")
        investment_return = st.number_input("Annual Investment Return (e.g., 0.07):", value=0.07, step=0.01, format="%.2f")

    col4, col5 = st.columns(2)
    with col4:
        fee_rate = st.number_input("Annual Fee Rate (e.g., 0.01):", value=0.01, step=0.005, format="%.3f")
    with col5:
        years = st.number_input("Years to Simulate:", value=30, step=1)

    target_savings = st.number_input("Target Retirement Savings (€):", value=1000000.0, step=50000.0)

    # --- Show Community Board right away ---
    display_community_board()

    st.markdown("---")
    if st.button("🚀 Run Simulation"):
        # --- Simulation Logic (CUAN vs Auto-Enrolment) ---
        def get_auto_enrolment_rate(year):
            """Returns the staged auto-enrolment rate for a given year."""
            if 1 <= year <= 3:
                return 0.015
            elif 4 <= year <= 6:
                return 0.03
            elif 7 <= year <= 9:
                return 0.045
            else:
                return 0.06

        # Initialize lists to store simulation results
        years_list = [0]
        salary_list = [starting_salary]

        # CUAN scenario
        annual_contribution_cuan = pension_contribution_rate * starting_salary
        pension_balance_cuan = annual_contribution_rate = annual_contribution_cuan  = pension_contribution_rate * starting_salary
        pension_balance_cuan = annual_contribution_cuan  # starting value
        fees_accumulated_cuan = 0

        # Auto-Enrolment scenario
        auto_rate = get_auto_enrolment_rate(1)
        annual_contribution_auto = auto_rate * starting_salary
        pension_balance_auto = annual_contribution_auto
        fees_accumulated_auto = 0

        # Lists for storing yearly simulation results
        annual_contribution_cuan_list = [annual_contribution_cuan]
        annual_contribution_auto_list = [annual_contribution_auto]
        pension_balance_cuan_list = [pension_balance_cuan]
        pension_balance_auto_list = [pension_balance_auto]
        fees_accumulated_cuan_list = [fees_accumulated_cuan]
        fees_accumulated_auto_list = [fees_accumulated_auto]
        pension_after_fees_cuan_list = [pension_balance_cuan]
        pension_after_fees_auto_list = [pension_balance_auto]

        salary_current = starting_salary
        milestone_year = None
        milestone_found = False

        for year in range(1, int(years) + 1):
            # Update salary and CUAN scenario contributions
            if year <= 5:
                salary_increase = salary_current * salary_increase_rate_early
                additional_contribution = salary_increase * increase_contribution_rate
                annual_contribution_cuan += additional_contribution
                salary_current *= (1 + salary_increase_rate_early)
            else:
                salary_current *= (1 + salary_increase_rate_late)
                annual_contribution_cuan = max(annual_contribution_cuan, salary_current * pension_contribution_rate)

            # Auto-Enrolment scenario: get rate for current year
            auto_rate = get_auto_enrolment_rate(year)
            annual_contribution_auto = salary_current * auto_rate

            # Calculate new balances and fees for CUAN
            pension_balance_cuan = (pension_balance_cuan + annual_contribution_cuan) * (1 + investment_return)
            fees_paid_cuan = pension_balance_cuan * fee_rate
            pension_balance_cuan_after_fees = pension_balance_cuan - fees_paid_cuan
            fees_accumulated_cuan += fees_paid_cuan

            # Calculate new balances and fees for Auto-Enrolment
            pension_balance_auto = (pension_balance_auto + annual_contribution_auto) * (1 + investment_return)
            fees_paid_auto = pension_balance_auto * fee_rate
            pension_balance_auto_after_fees = pension_balance_auto - fees_paid_auto
            fees_accumulated_auto += fees_paid_auto

            # Append yearly results
            years_list.append(year)
            salary_list.append(salary_current)
            annual_contribution_cuan_list.append(annual_contribution_cuan)
            annual_contribution_auto_list.append(annual_contribution_auto)
            pension_balance_cuan_list.append(pension_balance_cuan)
            pension_balance_auto_list.append(pension_balance_auto)
            fees_accumulated_cuan_list.append(fees_accumulated_cuan)
            fees_accumulated_auto_list.append(fees_accumulated_auto)
            pension_after_fees_cuan_list.append(pension_balance_cuan_after_fees)
            pension_after_fees_auto_list.append(pension_balance_auto_after_fees)

            if (not milestone_found) and (pension_balance_cuan_after_fees >= target_savings):
                milestone_year = year
                milestone_found = True

        # Create DataFrame with simulation results (with CUAN vs Auto-Enrolment titles)
        df = pd.DataFrame({
            "Year": years_list,
            "Salary (€)": salary_list,
            "Annual Contribution (€) (CUAN)": annual_contribution_cuan_list,
            "Annual Contribution (€) (Auto-Enrolment)": annual_contribution_auto_list,
            "Pension Balance Before Fees (€) (CUAN)": pension_balance_cuan_list,
            "Pension Balance Before Fees (€) (Auto-Enrolment)": pension_balance_auto_list,
            "Pension Balance After Fees (€) (CUAN)": pension_after_fees_cuan_list,
            "Pension Balance After Fees (€) (Auto-Enrolment)": pension_after_fees_auto_list,
            "Total Fees Earned (€) (CUAN)": fees_accumulated_cuan_list,
            "Total Fees Earned (€) (Auto-Enrolment)": fees_accumulated_auto_list
        })

        st.subheader("📊 Simulation Results")
        st.dataframe(df.style.format("{:,.2f}"))

        fig = px.line(
            df,
            x="Year",
            y=[
                "Pension Balance After Fees (€) (CUAN)",
                "Pension Balance After Fees (€) (Auto-Enrolment)",
                "Total Fees Earned (€) (CUAN)",
                "Total Fees Earned (€) (Auto-Enrolment)"
            ],
            labels={"value": "Amount (€)", "Year": "Years"},
            title="Pension Growth & Fees Comparison: CUAN vs Auto-Enrolment"
        )
        fig.update_layout(yaxis_tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🏆 Gamification & Milestones")
        if milestone_found:
            st.success(f"Congratulations! You reached your target of €{target_savings:,.2f} in year {milestone_year}!")
            st.balloons()
        else:
            st.info("Target not reached. Keep saving and refining your plan!")

        # --- Share Results on the Community Board ---
        st.markdown("### Share Your Results")
        username = st.text_input("Enter a username/nickname:", "Anonymous")

        final_balance_cuan = df["Pension Balance After Fees (€) (CUAN)"].iloc[-1]
        final_balance_auto = df["Pension Balance After Fees (€) (Auto-Enrolment)"].iloc[-1]
        year_reached = milestone_year if milestone_found else None

        if st.button("Add My Results to the Board"):
            community_df = load_community_data()
            new_record = {
                "Username": username,
                "Final Balance (CUAN)": final_balance_cuan,
                "Final Balance (Auto-Enrolment)": final_balance_auto,
                "Target Savings": target_savings,
                "Year Reached Target": year_reached
            }
            community_df = community_df.append(new_record, ignore_index=True)
            save_community_data(community_df)
            st.success("Your results have been added to the community board!")
            st.experimental_rerun()

    # --- Comments Section (Always visible) ---
    st.markdown("---")
    display_comments_section()

def main():
    run_pension_simulator()

if __name__ == '__main__':
    main()
