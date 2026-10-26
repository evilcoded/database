"""Original pure scoring function, unchanged numerical regression reference."""
def score_asset(m, regime, btc, model=None):
    ch7=safe(m.get('price_change_percentage_7d_in_currency')); ch30=safe(m.get('price_change_percentage_30d_in_currency'))
    vol=safe(m.get('total_volume')); cap=safe(m.get('market_cap')); ath_change=abs(safe(m.get('ath_change_percentage')))
    momentum=clamp(50+ch7*2.2+ch30*0.7)
    rs=clamp(50+(ch7-btc['ch7'])*2+(ch30-btc['ch30'])*0.4)
    liquidity=clamp(35+min(55,(vol/max(cap,1))*180))
    accumulation=clamp(45+(vol/max(cap,1))*2600+max(ch7,0)*0.6)
    reversal=clamp(30+max(ch7-12,0)*3+max(ch30-35,0)*1.2)
    entry=clamp(72+min(10,max(-10,-ch7*0.7))-max(ch7-8,0)*2-max(ch7-18,0))
    if ch7 < -12 and ch30 < -15: entry-=8
    risk=clamp(25+abs(ch7)*0.9+max(0,ath_change-25)*0.35+max(0,35-liquidity)*0.45)
    a=str(m.get('symbol','')).upper()
    opportunity=clamp(.20*momentum+.18*rs+.12*liquidity+.10*accumulation+.20*(100-reversal)+.10*(70 if regime>=60 else 45)+.10*(70 if cap>5e9 else 55))
    asym=clamp(55+(100-risk)*.35+max(0,75-momentum)*.15)
    promising=clamp(.30*opportunity+.22*entry+.18*asym+.12*regime+.18*(100-risk))
    # Optional walk-forward learned calibration adjusts only the component mix, never the hard risk/entry gates.
    if model and model.get('trained') and model.get('calibration_usable',False):
        base=np.array([opportunity,entry,asym,regime,100-risk],dtype=float)
        w=np.array(model.get('kpi_weights',[.30,.22,.18,.12,.18]),dtype=float)
        if len(w)==5 and np.isfinite(w).all() and w.sum()>0:
            w=w/w.sum(); promising=clamp(float(np.dot(base,w)))
    return {'regime':round(regime,1),'momentum_quality':round(momentum,1),'relative_strength':round(rs,1),'liquidity':round(liquidity,1),'accumulation':round(accumulation,1),'reversal_risk':round(reversal,1),'opportunity':round(opportunity,1),'entry':round(entry,1),'asymmetry':round(asym,1),'risk':round(risk,1),'promising_pct':round(promising,1),'speculative':False}
