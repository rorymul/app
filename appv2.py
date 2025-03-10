import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Irish Pension Simulator", page_icon="💰", layout="wide")

def pension_fund_simulation():
    st.title("💰 Irish Pension Fund Simulator & Community Board")
    st.write("""
    Welcome to the Irish Pension Fund Simulator! Adjust your parameters below and run
    the simulation. You can then share your results with the community board below.
    """)

    # --- User inputs ---
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

    # --- Always Show Community Board ---
    st.markdown("## Current Community Results")
    community_file = "community_data.csv"
    if os.path.exists(community_file):
        # If we already have data, show it right away
        loaded_community_df = pd.read_csv(community_file)
        st.dataframe(loaded_community_df.style.format("{:,.2f}"))
    else:
        st.info("No community data found yet. Run a simulation and share your results to populate the board!")
    
    st.markdown("---")

    # --- Run Simulation ---
    if st.button("🚀 Run Simulation"):
        # (Same simulation code as before)
        years_list = [0]
        salary_list = [starting_salary]
        annual_contribution_list = [pension_contribution_rate * starting_salary]
        annual_contribution_fixed_list = [pension_contribution_rate * starting_salary]
        pension_balance_list = [pension_contribution_rate * starting_salary]
        pension_balance_fixed_list = [pension_contribution_rate * starting_salary]
        fees_accumulated_list = [0]
        fees_accumulated_fixed_list = [0]
        pension_after_fees_list = [pension_contribution_rate * starting_salary]
        pension_after_fees_fixed_list = [pension_contribution_rate * starting_salary]

        salary = starting_salary
        pension_balance = pension_contribution_rate * starting_salary
        pension_balance_fixed = pension_contribution_rate * starting_salary
        annual_contribution = pension_contribution_rate * starting_salary
        annual_contribution_fixed = pension_contribution_rate * starting_salary
        total_fees_accumulated = 0
        total_fees_accumulated_fixed = 0

        milestone_year = None
        milestone_found = False

        for year in range(1, int(years) + 1):
            if year <= 5:
                salary_increase = salary * salary_increase_rate_early
                additional_contribution = salary_increase * increase_contribution_rate
                annual_contribution += additional_contribution
                salary *= (1 + salary_increase_rate_early)
            else:
                salary *= (1 + salary_increase_rate_late)
                annual_contribution = max(annual_contribution, salary * pension_contribution_rate)

            annual_contribution_fixed = salary * pension_contribution_rate

            pension_balance = (pension_balance + annual_contribution) * (1 + investment_return)
            pension_balance_fixed = (pension_balance_fixed + annual_contribution_fixed) * (1 + investment_return)

            fees_paid = pension_balance * fee_rate
            pension_balance_after_fees = pension_balance - fees_paid
            total_fees_accumulated += fees_paid

            fees_paid_fixed = pension_balance_fixed * fee_rate
            pension_balance_after_fees_fixed = pension_balance_fixed - fees_paid_fixed
            total_fees_accumulated_fixed += fees_paid_fixed

            years_list.append(year)
            salary_list.append(salary)
            annual_contribution_list.append(annual_contribution)
            annual_contribution_fixed_list.append(annual_contribution_fixed)
            pension_balance_list.append(pension_balance)
            pension_balance_fixed_list.append(pension_balance_fixed)
            fees_accumulated_list.append(total_fees_accumulated)
            fees_accumulated_fixed_list.append(total_fees_accumulated_fixed)
            pension_after_fees_list.append(pension_balance_after_fees)
            pension_after_fees_fixed_list.append(pension_balance_after_fees_fixed)

            if (not milestone_found) and (pension_balance_after_fees >= target_savings):
                milestone_year = year
                milestone_found = True

        df = pd.DataFrame({
            "Year": years_list,
            "Salary (€)": salary_list,
            "Annual Contribution (€) (Increased Contributions)": annual_contribution_list,
            "Annual Contribution (€) (Fixed Contributions)": annual_contribution_fixed_list,
            "Pension Balance Before Fees (€) (Increased Contributions)": pension_balance_list,
            "Pension Balance Before Fees (€) (Fixed Contributions)": pension_balance_fixed_list,
            "Pension Balance After Fees (€) (Increased Contributions)": pension_after_fees_list,
            "Pension Balance After Fees (€) (Fixed Contributions)": pension_after_fees_fixed_list,
            "Total Fees Earned (€) (Increased Contributions)": fees_accumulated_list,
            "Total Fees Earned (€) (Fixed Contributions)": fees_accumulated_fixed_list
        })

        st.subheader("📊 Simulation Results")
        st.dataframe(df.style.format("{:,.2f}"))

        fig = px.line(
            df,
            x="Year",
            y=[
                "Pension Balance After Fees (€) (Increased Contributions)",
                "Pension Balance After Fees (€) (Fixed Contributions)",
                "Total Fees Earned (€) (Increased Contributions)",
                "Total Fees Earned (€) (Fixed Contributions)"
            ],
            labels={"value": "Amount (€)", "Year": "Years"},
            title="Pension Growth & Fees Comparison"
        )
        fig.update_layout(yaxis_tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🏆 Gamification & Milestones")
        if milestone_found:
            st.success(f"Congratulations! You reached your target of €{target_savings:,.2f} in year {milestone_year}!")
            st.balloons()
        else:
            st.info("Target not reached. Keep saving and refining your plan!")

        # Let user share results on the community board
        st.markdown("### Share Your Results with the Community")
        username = st.text_input("Enter a username/nickname:", "Anonymous")

        final_balance_increased = df["Pension Balance After Fees (€) (Increased Contributions)"].iloc[-1]
        final_balance_fixed = df["Pension Balance After Fees (€) (Fixed Contributions)"].iloc[-1]
        year_reached = milestone_year if milestone_found else None

        if st.button("Add My Results"):
            # Load existing data if any
            if os.path.exists(community_file):
                community_df = pd.read_csv(community_file)
            else:
                community_df = pd.DataFrame(columns=[
                    "Username",
                    "Final Balance (Increased)",
                    "Final Balance (Fixed)",
                    "Target Savings",
                    "Year Reached Target"
                ])

            new_record = {
                "Username": username,
                "Final Balance (Increased)": final_balance_increased,
                "Final Balance (Fixed)": final_balance_fixed,
                "Target Savings": target_savings,
                "Year Reached Target": year_reached
            }
            community_df = community_df.append(new_record, ignore_index=True)
            community_df.to_csv(community_file, index=False)
            st.success("Your results have been added to the community board!")

            # Immediately show the updated board
            loaded_community_df = pd.read_csv(community_file)
            st.dataframe(loaded_community_df.style.format("{:,.2f}"))

def main():
    pension_fund_simulation()

if __name__ == '__main__':
    main()
