# Financial model — Shabazi 58 / Ahad Ha'am 1, Neve Tzedek (gush 7422, parcels 47+48)
# All money in NIS (₪), net of VAT unless noted. Base-case assumptions are explicit and editable.
import json, copy

VAT = 1.18

BASE = dict(
    land_m2=473, existing_gross=475, leasable=430,         # m²
    rights_above=993.3,                                     # 210% of 473
    add_gross=420,                                          # working assumption: ~80% of 518 m² max addition
    saleable_ratio=0.88,                                    # saleable / gross of the addition
    units=6,
    # --- rents & yields
    rent_now=170,          # ₪/m²/month, current (to be replaced by actual rent roll)
    rent_restored=210,     # ₪/m²/month after restoration
    vacancy=0.05, opex=0.08,                                # of gross rent (owner-paid: insurance, mgmt, upkeep)
    cap_retail=0.05,       # cap rate prime street retail Neve Tzedek (assumption; national average 7%)
    # --- residential prices (buyer price incl. VAT)
    res_price=95_000,      # ₪/m² saleable, incl. VAT
    # --- construction (net of VAT)
    restore_cost=14_000,   # ₪/m² of existing building (preservation + structural strengthening)
    restore_only_cost=8_000,  # ₪/m² envelope/systems restoration without addition (alternative B)
    add_cost=15_000,       # ₪/m² addition built on a preserved structure
    soft=0.22,             # planning, consultants, preservation file, supervision, permits — % of hard
    contingency=0.08,      # % of hard
    levy=3_000_000,        # betterment levy estimate (needs appraisal)
    parking_fund=200_000,
    tenant_comp=1_000_000, # tenant evacuation / compensation (unknown; protected tenancy could be far higher)
    marketing=0.02,        # % of residential revenue
    fin_rate=0.0575, build_months=24, plan_months=24,      # construction loan rate ~prime+1
    dev_profit=0.16,       # developer profit on cost (Standard 21, Tel Aviv 15–17%)
    grant_units=4, grant=50_000,                            # TLV preservation fund (per existing unit)
    disc=0.07,             # owners' discount rate for NPV
    g=0.02,                # annual rent / hotel income growth
    horizon=10,
    # --- hotel
    rooms=18, adr=1_100, occ=0.62, gop=0.33, ffe_room=180_000, cap_hotel=0.07, fb_rent=0,
    # --- sale transaction costs
    sale_cost=0.025,
)

def noi(p, rent):
    return p['leasable'] * rent * 12 * (1 - p['vacancy']) * (1 - p['opex'])

def gr(p, t):
    return (1 + p['g']) ** max(t - 1, 0)

def npv(rate, flows):
    return sum(cf / (1 + rate) ** t for t, cf in flows)

def dev_costs(p):
    hard_restore = p['existing_gross'] * p['restore_cost']
    hard_add = p['add_gross'] * p['add_cost']
    hard = hard_restore + hard_add
    soft = hard * p['soft']
    cont = hard * p['contingency']
    res_rev_net = p['add_gross'] * p['saleable_ratio'] * p['res_price'] / VAT
    mkt = res_rev_net * p['marketing']
    fixed = p['levy'] + p['parking_fund'] + p['tenant_comp']
    pre_fin = hard + soft + cont + mkt + fixed
    # interest: average 50% drawn over build period
    fin = pre_fin * 0.5 * p['fin_rate'] * (p['build_months'] / 12)
    total = pre_fin + fin
    return dict(hard_restore=hard_restore, hard_add=hard_add, soft=soft, contingency=cont,
                marketing=mkt, levy=p['levy'], parking=p['parking_fund'], tenants=p['tenant_comp'],
                finance=fin, total=total, res_rev_net=res_rev_net)

def alt_A(p):
    """Sell as-is today. Value = max(income value, residual value to a developer) — reported both."""
    v_income = noi(p, p['rent_now']) / p['cap_retail']
    rlv = residual_land_value(p)
    return dict(income_value=v_income, residual_value=rlv,
                net_income=v_income * (1 - p['sale_cost']), net_residual=rlv * (1 - p['sale_cost']))

def residual_land_value(p):
    """What a developer can pay for the site as-is: completed value − costs − profit − owners' lost rent."""
    c = dev_costs(p)
    retail_value_after = noi(p, p['rent_restored']) / p['cap_retail']
    gdv = c['res_rev_net'] + retail_value_after
    lost_rent = noi(p, p['rent_now']) * (p['build_months'] / 12)
    profit = p['dev_profit'] * c['total']
    # holding/planning period: discount completion value back by plan+build months at 8%
    t = (p['plan_months'] + p['build_months']) / 12
    rlv = (gdv - c['total'] - profit - lost_rent) / (1.08 ** t)
    return rlv

def alt_B0(p):
    """Status quo: keep leasing without works. NPV over horizon + exit at cap rate."""
    n = noi(p, p['rent_now'])
    flows = [(t, n * gr(p, t)) for t in range(1, p['horizon'] + 1)]
    exit_v = n * gr(p, p['horizon'] + 1) / p['cap_retail'] * (1 - p['sale_cost'])
    flows.append((p['horizon'], exit_v))
    return dict(noi=n, npv=npv(p['disc'], flows), exit=exit_v)

def alt_B(p):
    """Restore building (no addition), re-lease at higher rent."""
    capex = p['existing_gross'] * p['restore_only_cost'] * (1 + p['soft'] + p['contingency'])
    grant = p['grant_units'] * p['grant']
    n0, n1 = noi(p, p['rent_now']), noi(p, p['rent_restored'])
    flows = [(0, -capex / 2), (1, -capex / 2 + grant + n0 * 0.5)]  # year 1: works, half income
    flows += [(t, n1 * gr(p, t)) for t in range(2, p['horizon'] + 1)]
    exit_v = n1 * gr(p, p['horizon'] + 1) / p['cap_retail'] * (1 - p['sale_cost'])
    flows.append((p['horizon'], exit_v))
    return dict(capex=capex, grant=grant, noi_after=n1, npv=npv(p['disc'], flows), exit=exit_v)

def alt_C(p):
    """Owners self-develop: restore + addition, sell apartments, keep restored retail."""
    c = dev_costs(p)
    grant = p['grant_units'] * p['grant']
    n0, n1 = noi(p, p['rent_now']), noi(p, p['rent_restored'])
    plan_y = p['plan_months'] / 12
    build_y = p['build_months'] / 12
    # flows (years): planning period: rent continues, planning soft costs paid (40% of soft);
    soft_plan = c['soft'] * 0.4
    flows = []
    flows.append((0.5, -soft_plan))
    flows.append((1, n0)); flows.append((2, n0 * gr(p, 2)))
    # build period: rent lost; costs spread; tenant comp + levy at start
    t0 = plan_y
    flows.append((t0, -(c['levy'] + c['parking'] + c['tenants'])))
    spend = c['total'] - soft_plan - c['levy'] - c['parking'] - c['tenants'] - c['marketing']
    steps = 4
    for i in range(steps):
        flows.append((t0 + (i + 0.5) * build_y / steps, -spend / steps))
    # presales: 40% of units during construction (paid gradually); rest at completion
    rev = c['res_rev_net']
    flows.append((t0 + build_y * 0.75, rev * 0.4 * (1 - p['marketing'])))
    flows.append((t0 + build_y + 0.25, rev * 0.6 * (1 - p['marketing']) + grant))
    # retail after completion
    end = t0 + build_y
    y = end + 1
    while y <= p['horizon']:
        flows.append((y, n1 * gr(p, y))); y += 1
    exit_v = n1 * gr(p, p['horizon'] + 1) / p['cap_retail'] * (1 - p['sale_cost'])
    flows.append((p['horizon'], exit_v))
    profit_static = rev + grant - c['total']
    peak_equity_need = c['total'] * 0.25  # typical 20–30% equity in bank-financed project
    return dict(costs=c, revenue_res=rev, profit_on_residential=profit_static,
                margin_on_cost=profit_static / c['total'], retail_value_after=n1 / p['cap_retail'],
                npv=npv(p['disc'], flows), equity=peak_equity_need, flows=flows)

def alt_D(p):
    """Boutique hotel in the whole building (rooms in addition + part of ground floor)."""
    c = dev_costs(p)
    # no residential sales; hotel fit-out on top of construction
    capex = c['total'] - c['marketing'] + p['rooms'] * p['ffe_room']
    rooms_rev = p['rooms'] * p['adr'] * p['occ'] * 365
    total_rev = rooms_rev * 1.25     # + F&B / other ≈ 25% of rooms
    ebitda = total_rev * p['gop'] - total_rev * 0.04  # FF&E reserve
    value = ebitda / p['cap_hotel']
    n0 = noi(p, p['rent_now'])
    t0 = p['plan_months'] / 12; build_y = p['build_months'] / 12
    flows = [(1, n0), (2, n0 * gr(p, 2)), (t0 + build_y / 2, -capex)]
    y = t0 + build_y + 1
    ramp = [0.7, 0.9]
    k = 0
    while y <= p['horizon']:
        f = ramp[k] if k < len(ramp) else 1.0
        flows.append((y, ebitda * f * gr(p, y))); y += 1; k += 1
    flows.append((p['horizon'], value * gr(p, p['horizon'] + 1) * (1 - p['sale_cost'])))
    return dict(capex=capex, rooms_rev=rooms_rev, total_rev=total_rev, ebitda=ebitda,
                value=value, npv=npv(p['disc'], flows), yield_on_cost=ebitda / capex, flows=flows)

def alt_E(p):
    """Combination deal: developer restores the whole building and builds the addition at its cost,
    gets a share of the new apartments; owners keep the restored ground floor + the remaining apartments.
    Solve for the owners' share of new apartments that leaves the developer its required profit."""
    c = dev_costs(p)
    rev = c['res_rev_net']
    # developer bears all development costs except owners' own lost rent
    dev_cost = c['total']
    # developer needs: (1-s)*rev >= dev_cost*(1+profit)
    s = 1 - dev_cost * (1 + p['dev_profit']) / rev
    s = max(s, -1)
    n0, n1 = noi(p, p['rent_now']), noi(p, p['rent_restored'])
    t0 = p['plan_months'] / 12; build_y = p['build_months'] / 12
    flows = [(1, n0), (2, n0 * gr(p, 2))]
    # owners receive share s of apartments at completion (value at net-of-VAT prices; could keep or sell)
    flows.append((t0 + build_y + 0.25, max(s, 0) * rev))
    if s < 0:  # owners must contribute cash (or give part of the retail) to close the gap
        flows.append((t0, s * rev))
    y = t0 + build_y + 1
    while y <= p['horizon']:
        flows.append((y, n1 * gr(p, y))); y += 1
    flows.append((p['horizon'], n1 * gr(p, p['horizon'] + 1) / p['cap_retail'] * (1 - p['sale_cost'])))
    return dict(owner_share=s, owner_units=max(s, 0) * p['units'], npv=npv(p['disc'], flows), flows=flows)

def run(p):
    return dict(A=alt_A(p), B0=alt_B0(p), B=alt_B(p), C=alt_C(p), D=alt_D(p), E=alt_E(p))

def m(x): return round(x / 1e6, 2)


if __name__ == '__main__':
    r = run(copy.deepcopy(BASE))
    for k in ('A', 'B0', 'B', 'C', 'D', 'E'):
        v = r[k].get('npv', r[k].get('net_income'))
        print(k, round(v / 1e6, 2), 'M NIS')
