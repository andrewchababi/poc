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
        # Based on $5100 daily fixed cost estimate ($85 * 60)
        self.scenarios = {
            "Today (60 reqs)": 85.00,
            "Q1 '26 (150 reqs)": 34.00,
            "Q3 '26 (300 reqs)": 17.00
        }

    def get_cost(self, code):
        return self.reagent_costs.get(code, 0.0)

    def calculate_quote(self, tests):
        if not tests: return
        
        # --- PRICING LOGIC ---
        line_items = []
        for t in tests:
            code = t.upper().replace(" ", "_")
            fee = self.list_prices.get(code, 0)
            cost = self.get_cost(code)
            # Overhead logic: $3 for single, $1 if bundled.
            # We'll apply $1 per test since this function generates bundles.
            overhead_marginal = 1.00 
            line_items.append({'code': code, 'fee': fee, 'cost': cost, 'ovh': overhead_marginal})

        # Sort by Price (Highest is Anchor)
        line_items.sort(key=lambda x: x['fee'], reverse=True)
        
        total_price = 0
        total_variable_cost = 0 # Reagents + Marginal Overhead ($1/test)
        
        breakdown = []
        
        # 1. ANCHOR (100% Price)
        anchor = line_items[0]
        anchor_price = anchor['fee']
        total_price += anchor_price
        total_variable_cost += (anchor['cost'] + anchor['ovh'])
        breakdown.append(f"ANCHOR: {anchor['code']:<10} ${anchor_price:.2f}")

        # 2. ADD-ONS (50% Price, with Floor)
        for item in line_items[1:]:
            target_price = item['fee'] * 0.50
            floor_price = (item['cost'] + item['ovh']) * 3.0
            final_price = max(target_price, floor_price)
            
            total_price += final_price
            total_variable_cost += (item['cost'] + item['ovh'])
            breakdown.append(f"ADD-ON: {item['code']:<10} ${final_price:.2f} (List: ${item['fee']})")

        # --- OUTPUT ---
        print(f"\n{'='*40}")
        print(f"SPONTANEOUS PANEL QUOTE: {' + '.join(tests)}")
        print(f"{'-'*40}")
        for line in breakdown:
            print(line)
        print(f"{'-'*40}")
        print(f"TOTAL PATIENT PRICE:  ${total_price:.2f}")
        print(f"Total Variable Cost:  ${total_variable_cost:.2f} (Reagents + Lab Labor)")
        
        contribution_margin = total_price - total_variable_cost
        print(f"Contribution Margin:  ${contribution_margin:.2f} (Pays down fixed overhead)")
        
        print(f"\n--- PROFITABILITY FORECAST ---")
        for scenario, fixed_ovh in self.scenarios.items():
            # Net Profit = Contribution - Fixed Overhead per Patient
            net_profit = contribution_margin - fixed_ovh
            status = "✅ PROFIT" if net_profit > 0 else "❌ LOSS  "
            print(f"{scenario:<18} (Ovh ${fixed_ovh:.0f}): {status} ${net_profit:>.2f}")
        print(f"{'='*40}\n")

# --- TEST SCENARIOS ---
engine = LabPricingEngine()

# Scenario A: Small Bundle (The "Loss Leader" problem)
# TSH + Ferritin. 
# Today: LOSS (because revenue < $85). 
# Future: PROFIT (because revenue > $34).
engine.calculate_quote(["TSH", "FERRITIN"])

# Scenario B: The "Upsell" (Adding 2 cheap tests fixes the profit)
# TSH + Ferritin + B12 + Magnesium
# Today: BREAK-EVEN (Revenue approaches $85).
# Future: HUGE PROFIT.
engine.calculate_quote(["TSH", "FERRITIN", "VIT_B12", "MAGNESIUM"])


tests = input("Please choose the tests: \n")
tests = tests.split(" ")

engine.calculate_quote(tests)

