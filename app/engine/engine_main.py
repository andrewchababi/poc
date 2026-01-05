class FinalPricingEngine:
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
            "Today": 85.00,
            "Jan 1 '26": 65.00  # Explicit $65 model
        }
        
        # 4. SURCHARGES (Pass-Through)
        self.donation_per_req = 5.00
        self.rev_share_per_req = 0.50

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
            overhead_marginal = 1.00 
            line_items.append({'code': code, 'fee': fee, 'cost': cost, 'ovh': overhead_marginal})

        line_items.sort(key=lambda x: x['fee'], reverse=True)
        
        total_price = 0
        reagent_lab_cost = 0 
        
        breakdown = []
        
        # 1. ANCHOR
        anchor = line_items[0]
        anchor_price = anchor['fee']
        total_price += anchor_price
        reagent_lab_cost += (anchor['cost'] + anchor['ovh'])
        breakdown.append(f"ANCHOR: {anchor['code']:<10} ${anchor_price:.2f}")

        # 2. ADD-ONS
        for item in line_items[1:]:
            target_price = item['fee'] * 0.50
            floor_price = (item['cost'] + item['ovh']) * 3.0
            final_price = max(target_price, floor_price)
            
            total_price += final_price
            reagent_lab_cost += (item['cost'] + item['ovh'])
            breakdown.append(f"ADD-ON: {item['code']:<10} ${final_price:.2f} (List: ${item['fee']})")

        # 3. SURCHARGES
        total_price += self.donation_per_req
        total_price += self.rev_share_per_req
        
        breakdown.append(f"SURCHARGE 1:     ${self.donation_per_req:.2f} (Charity)")
        breakdown.append(f"SURCHARGE 2:     ${self.rev_share_per_req:.2f} (Rev Share)")

        # --- OUTPUT ---
        print(f"\n{'='*40}")
        print(f"FINAL QUOTE: {' + '.join(tests)}")
        print(f"{'-'*40}")
        for line in breakdown:
            print(line)
        print(f"{'-'*40}")
        
        total_pass_through = self.donation_per_req + self.rev_share_per_req
        contribution = total_price - (reagent_lab_cost + total_pass_through)
        
        print(f"TOTAL PATIENT PRICE:    ${total_price:.2f}")
        print(f"Contribution Margin:    ${contribution:.2f}")
        
        print(f"\n--- NET PROFIT FORECAST ---")
        for scenario, fixed_ovh in self.scenarios.items():
            net_profit = contribution - fixed_ovh
            status = "✅ PROFIT" if net_profit > 0 else "❌ LOSS  "
            print(f"{scenario:<10} (Fixed ${fixed_ovh:.0f}): {status} ${net_profit:>.2f}")
        print(f"{'='*40}\n")

# Example: Run this for your key bundle types
engine = FinalPricingEngine()
engine.calculate_quote(["TSH", "FERRITIN"])
engine.calculate_quote(["TSH", "FERRITIN", "VIT_B12", "MAGNESIUM"])