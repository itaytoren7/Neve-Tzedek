# Scenario analysis for the Shabazi 58 / Ahad Ha'am 1 financial model.
# Run:  python3 analysis.py      → prints the scenario table + sensitivity, writes results.json
import copy, json, os
from financial_model import BASE, run, noi

HERE = os.path.dirname(os.path.abspath(__file__))

# Pessimistic / optimistic overrides (everything else stays at BASE)
LOW = dict(rent_now=140, rent_restored=180, res_price=80_000, restore_cost=18_000, add_cost=18_000,
           levy=4_500_000, tenant_comp=3_000_000, cap_retail=0.055, build_months=30, adr=950, occ=0.52)
HIGH = dict(rent_now=200, rent_restored=240, res_price=110_000, restore_cost=11_000, add_cost=13_000,
            levy=1_500_000, tenant_comp=300_000, cap_retail=0.045, build_months=20, adr=1_300, occ=0.70)

# One-at-a-time sensitivity of alternative C (self-development): key, Hebrew label, pessimistic, optimistic
SENS = (
    ('res_price', 'מחיר הדירות', '80 / 110 אלף ₪ למ״ר', 80_000, 110_000),
    ('add_gross', 'היקף התוספת שתאושר', '330 / 500 מ״ר', 330, 500),
    ('rent_restored', 'שכירות מסחר אחרי שיפוץ', '180 / 240 ₪ למ״ר לחודש', 180, 240),
    ('restore_cost', 'עלות השימור', '18 / 11 אלף ₪ למ״ר', 18_000, 11_000),
    ('levy', 'היטל השבחה', '4.5 / 1.5 מ׳ ₪', 4_500_000, 1_500_000),
    ('add_cost', 'עלות התוספת', '18 / 12.5 אלף ₪ למ״ר', 18_000, 12_500),
    ('tenant_comp', 'פינוי שוכרים', '3.0 / 0.3 מ׳ ₪', 3_000_000, 300_000),
    ('cap_retail', 'שיעור היוון מסחר', '5.5% / 4.5%', 0.055, 0.045),
    ('build_months', 'משך בנייה', '30 / 20 חודשים', 30, 20),
)


def irr(flows, lo=-0.9, hi=1.0):
    f = lambda r: sum(cf / (1 + r) ** t for t, cf in flows)
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2


def summary(p):
    r = run(p)
    sale_now = max(r['A']['net_income'], r['A']['net_residual'])
    return dict(
        A=sale_now, B0=r['B0']['npv'], B=r['B']['npv'], C=r['C']['npv'], D=r['D']['npv'], E=r['E']['npv'],
        C_irr_vs_sale=irr([(0, -sale_now)] + r['C']['flows']),
        E_irr_vs_sale=irr([(0, -sale_now)] + r['E']['flows']),
        C_margin=r['C']['margin_on_cost'], C_profit=r['C']['profit_on_residential'], C_cost=r['C']['costs']['total'],
        C_rev=r['C']['revenue_res'], C_equity=r['C']['equity'], E_share=r['E']['owner_share'],
        D_yield=r['D']['yield_on_cost'], D_capex=r['D']['capex'], D_ebitda=r['D']['ebitda'],
        noi_now=noi(p, p['rent_now']), noi_after=noi(p, p['rent_restored']),
        retail_after=r['C']['retail_value_after'], B_capex=r['B']['capex'],
    )


def scenarios():
    return {name: summary(dict(copy.deepcopy(BASE), **over)) for name, over in (('low', LOW), ('base', {}), ('high', HIGH))}


def sensitivity():
    p = copy.deepcopy(BASE)
    base = run(p)['C']['npv']
    out = []
    for key, label, detail, lo_v, hi_v in SENS:
        out.append(dict(key=key, label=label, detail=detail,
                        lo=run(dict(p, **{key: lo_v}))['C']['npv'], hi=run(dict(p, **{key: hi_v}))['C']['npv']))
    return base, out


if __name__ == '__main__':
    res = scenarios()
    fmt = lambda v: 'None' if v is None else (f"{v / 1e6:8.2f}M" if abs(v) > 1000 else f"{v:8.3f}")
    print(f"{'':16s}{'low':>10s}{'base':>10s}{'high':>10s}")
    for k in res['base']:
        print(f"{k:16s}", ' '.join(fmt(res[n][k]) for n in ('low', 'base', 'high')))
    base_c, sens = sensitivity()
    print(f"\nAlternative C NPV, base = {base_c / 1e6:.2f}M — one assumption at a time:")
    for s in sens:
        print(f"  {s['label']:28s} {s['lo'] / 1e6:6.2f}M  →  {s['hi'] / 1e6:6.2f}M")
    costs = run(copy.deepcopy(BASE))['C']['costs']
    json.dump(dict(scenarios=res, sensitivity=dict(base=base_c, rows=sens), costs_C_base=costs),
              open(os.path.join(HERE, 'results.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    print('\nwrote results.json')
