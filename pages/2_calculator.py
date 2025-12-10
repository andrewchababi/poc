import streamlit as st
import pandas as pd
from enum import Enum

class LabPricingEngine:
    def __init__(self):
        # 1. COSTS (Reagents Only)
        self.reagent_costs = {
            "A1C": 2.07, "ALB": 0.36, "ALP": 0.24, "ALT": 0.14, "AST": 0.09,
            "BILI_TOT": 0.24, "BILI_DIR": 0.17, "CALCIUM": 0.24, "CHOL": 0.24,
            "CK": 0.24, "CO2": 0.50, "CREAT": 1.01, "CRP": 1.21,
            "FERRITIN": 1.21, "FOLATE": 1.38, "FT3": 0.94, "FT4": 0.94,
            "GGT": 0.24, "GLUCOSE": 0.24, "HDL": 0.77, "IRON": 0.15,
            "LDH": 0.13, "LIPASE": 0.55, "MAGNESIUM": 0.22, "PHOS": 0.13,
            "PSA_TOT": 1.32, "PSA_FREE": 1.93, "TRIG": 0.24, "TSH": 0.71,
            "UREA": 0.17, "URIC_ACID": 0.13, "VIT_B12": 1.21, "VIT_D": 3.03,
            "CBC": 0.50, "ELECTROLYTES": 4.69, "HARMONY": 289.00
        }

        # 2. LIST PRICES
        self.list_prices = {
            "A1C": 49, "ALB": 40, "ALP": 31, "ALT": 30, "AST": 30,
            "BILI_TOT": 31, "BILI_DIR": 30, "CALCIUM": 31, "CHOL": 48,
            "CK": 39, "CO2": 34, "CREAT": 39, "CRP": 41,
            "FERRITIN": 41, "FOLATE": 40, "FT3": 31, "FT4": 31,
            "GGT": 31, "GLUCOSE": 31, "HDL": 30, "IRON": 30,
            "LDH": 37, "LIPASE": 37, "MAGNESIUM": 31, "PHOS": 30,
            "PSA_TOT": 42, "PSA_FREE": 43, "TRIG": 32, "TSH": 36,
            "UREA": 30, "URIC_ACID": 30, "VIT_B12": 41, "VIT_D": 59,
            "CBC": 29, "ELECTROLYTES": 46, "HARMONY": 1155
        }

        # 3. OVERHEAD SCENARIOS (Fixed Cost Per Patient)
        self.scenarios = {
            "Today (60 reqs)": 85.00,
            "Q1 '26 (150 reqs)": 34.00,
            "Q3 '26 (300 reqs)": 17.00
        }

    def get_cost(self, code):
        return self.reagent_costs.get(code, 0.0)

    def calculate_quote(self, tests):
        if not tests:
            return None
        
        # --- PRICING LOGIC ---
        line_items = []
        for t in tests:
            code = t.upper().replace(" ", "_")
            fee = self.list_prices.get(code, 0)
            cost = self.get_cost(code)
            overhead_marginal = 1.00
            line_items.append({'code': code, 'fee': fee, 'cost': cost, 'ovh': overhead_marginal})

        # Sort by Price (Highest is Anchor)
        line_items.sort(key=lambda x: x['fee'], reverse=True)
        
        total_price = 0
        total_variable_cost = 0
        breakdown = []
        
        # 1. ANCHOR (100% Price)
        anchor = line_items[0]
        anchor_price = anchor['fee']
        total_price += anchor_price
        total_variable_cost += (anchor['cost'] + anchor['ovh'])
        breakdown.append({
            'type': 'ANCHOR',
            'code': anchor['code'],
            'price': anchor_price,
            'cost': anchor['cost'],
            'overhead': anchor['ovh'],
            'list_price': anchor['fee']
        })

        # 2. ADD-ONS (50% Price, with Floor)
        for item in line_items[1:]:
            target_price = item['fee'] * 0.50
            floor_price = (item['cost'] + item['ovh']) * 3.0
            final_price = max(target_price, floor_price)
            
            total_price += final_price
            total_variable_cost += (item['cost'] + item['ovh'])
            breakdown.append({
                'type': 'ADD-ON',
                'code': item['code'],
                'price': final_price,
                'cost': item['cost'],
                'overhead': item['ovh'],
                'list_price': item['fee']
            })

        contribution_margin = total_price - total_variable_cost
        
        profitability = {}
        for scenario, fixed_ovh in self.scenarios.items():
            net_profit = contribution_margin - fixed_ovh
            profitability[scenario] = {
                'net_profit': net_profit,
                'fixed_overhead': fixed_ovh,
                'is_profitable': net_profit > 0
            }

        return {
            'breakdown': breakdown,
            'total_price': total_price,
            'total_variable_cost': total_variable_cost,
            'contribution_margin': contribution_margin,
            'profitability': profitability,
            'tests_selected': tests
        }


# Page config
st.set_page_config(page_title="Lab Pricing Engine", layout="wide", initial_sidebar_state="collapsed")

st.title("💊 Lab Pricing Engine")
st.markdown("Calculate patient pricing and profitability for lab test panels")

# Initialize engine
engine = LabPricingEngine()

# Get all available tests
all_tests = sorted(list(engine.list_prices.keys()))

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Test Selection")
    
    # Quick presets
    st.markdown("**Quick Presets:**")
    col_preset1, col_preset2 = st.columns(2)
    
    with col_preset1:
        if st.button("🔬 Thyroid Panel", use_container_width=True):
            st.session_state.selected_tests = ["TSH", "FT3", "FT4"]
    
    with col_preset2:
        if st.button("🩸 Lipid Panel", use_container_width=True):
            st.session_state.selected_tests = ["CHOL", "HDL", "TRIG"]
    
    col_preset3, col_preset4 = st.columns(2)
    
    with col_preset3:
        if st.button("⚡ Iron Panel", use_container_width=True):
            st.session_state.selected_tests = ["IRON", "FERRITIN"]
    
    with col_preset4:
        if st.button("🧪 CBC", use_container_width=True):
            st.session_state.selected_tests = ["CBC"]
    
    st.divider()
    
    st.markdown("**Custom Selection:**")
    selected_tests = st.multiselect(
        "Select tests to include in panel",
        options=all_tests,
        default=st.session_state.get('selected_tests', []),
        key="selected_tests",
        help="Choose one or more tests. The highest-priced test becomes the anchor (100% price). Others get 50% discount with a cost-based floor."
    )


# Calculate if tests are selected
if selected_tests:
    result = engine.calculate_quote(selected_tests)
    
    if result:
        with col2:
            st.subheader("📊 Quote Summary")
            
            # Key metrics at the top
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric(
                    "Patient Price",
                    f"${result['total_price']:.2f}",
                    delta=None,
                    delta_color="off"
                )
            
            with metric_col2:
                st.metric(
                    "Variable Cost",
                    f"${result['total_variable_cost']:.2f}",
                    delta=None,
                    delta_color="off"
                )
            
            with metric_col3:
                st.metric(
                    "Contribution Margin",
                    f"${result['contribution_margin']:.2f}",
                    delta=None,
                    delta_color="off"
                )
        
        # Breakdown table
        st.subheader("💰 Pricing Breakdown")
        
        breakdown_df = pd.DataFrame([
            {
                'Test': item['code'],
                'Type': item['type'],
                'Reagent Cost': f"${item['cost']:.2f}",
                'Overhead': f"${item['overhead']:.2f}",
                'List Price': f"${item['list_price']:.2f}",
                'Final Price': f"${item['price']:.2f}"
            }
            for item in result['breakdown']
        ])
        
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        
        # Profitability scenarios
        st.subheader("📈 Profitability Forecast")
        
        scenario_cols = st.columns(len(result['profitability']))
        
        for idx, (scenario, data) in enumerate(result['profitability'].items()):
            with scenario_cols[idx]:
                color = "green" if data['is_profitable'] else "red"
                delta_prefix = "+" if data['is_profitable'] else ""
                
                st.metric(
                    scenario,
                    f"${data['net_profit']:.2f}",
                    delta=f"{delta_prefix}Ovh: ${data['fixed_overhead']:.0f}",
                    delta_color="off"
                )
        
        # Detailed profitability breakdown
        with st.expander("📋 Detailed Profitability Analysis"):
            prof_data = []
            for scenario, data in result['profitability'].items():
                prof_data.append({
                    'Scenario': scenario,
                    'Fixed Overhead': f"${data['fixed_overhead']:.2f}",
                    'Contribution Margin': f"${result['contribution_margin']:.2f}",
                    'Net Profit/Loss': f"${data['net_profit']:.2f}",
                    'Status': '✅ Profitable' if data['is_profitable'] else '❌ Loss'
                })
            
            prof_df = pd.DataFrame(prof_data)
            st.dataframe(prof_df, use_container_width=True, hide_index=True)
        
        # Cost analysis
        with st.expander("🔍 Cost Analysis"):
            st.write(f"**Total Reagent Cost:** ${sum(item['cost'] for item in result['breakdown']):.2f}")
            st.write(f"**Total Overhead (Lab Labor):** ${sum(item['overhead'] for item in result['breakdown']):.2f}")
            st.write(f"**Gross Profit Margin:** {((result['contribution_margin'] / result['total_price']) * 100):.1f}%")

else:
    with col2:
        st.info("👈 Select tests from the left panel to generate a quote")