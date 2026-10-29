"""Original pure decision functions for parity tests; synthetic inputs only."""
def _v38133_brain_experimental(scores, cash_eur, total_wealth):
    ranked=[]
    for src in scores:
        x=dict(src); k=float(x.get('promising_pct') or 0); opp=float(x.get('opportunity') or 0); ent=float(x.get('entry') or 0); asym=float(x.get('asymmetry') or 0); risk=float(x.get('risk') or 0); held=float(x.get('current_value_eur') or 0)>0
        if held and risk>=78 and (asym<45 or k<45): act='VENDA'
        elif held and float(x.get('pnl_pct') or 0)>=5 and (risk>=65 or asym<55): act='REALIZE'
        elif (not held) and k>=65 and opp>=60 and ent>=55 and asym>=55 and risk<=65: act='COMPRE'
        else: act='ACOMPANHE'
        experimental=(act != str(x.get('action') or 'ACOMPANHE').upper()) or act=='COMPRE'
        ranked.append({'currency':x.get('currency'),'quote_currency':x.get('quote_currency'),'provider_id':x.get('provider_id'),'account_id':x.get('account_id'),'quote_currency_source':x.get('quote_currency_source'),'quote_observed_at':x.get('quote_observed_at'),'quote_freshness':x.get('quote_freshness'),'asset':x.get('asset'),'brain_action':act,'experimental':bool(experimental),'display_action':act+'*' if experimental else act,'production_action':str(x.get('action') or 'ACOMPANHE').upper(),'promising_pct':k,'opportunity':opp,'entry':ent,'asymmetry':asym,'risk':risk,'has_position':held,'evidence_status':'NOT_CONSOLIDATED' if experimental else 'OPERATIONAL_PARITY','rationale':f"KPI {k:.1f} | OPP {opp:.1f} | ENT {ent:.1f} | ASY {asym:.1f} | RISK {risk:.1f}",'execution':'MANUAL_ONLY'})
    buys=[r for r in ranked if r['brain_action']=='COMPRE' and r['experimental']]; cash=max(0.0,float(cash_eur or 0))
    if buys and cash>0:
        raw=[max(1.0,r['promising_pct'])*max(.2,1-r['risk']/120)*max(.5,r['entry']/100) for r in buys]; den=sum(raw) or 1.0
        for r,w in zip(buys,raw): r['experimental_cash_suggestion_eur']=round(cash*w/den,2)
    for r in ranked: r.setdefault('experimental_cash_suggestion_eur',0.0)
    return {'schema':'porquinho.brain-experimental-live/1.0','mode':'SHADOW_EXPERIMENTAL','confidence_semantics':'EVIDENCE_QUALITY_NOT_PROBABILITY','automatic_execution':False,'automatic_production_promotion':False,'cash_policy':'100_PERCENT_CASH_EVALUATED_EACH_CYCLE_NO_FORCED_INVESTMENT','cash_available_eur':round(cash,2),'cash_state':'EXPERIMENTAL_ALLOCATION_AVAILABLE' if buys and cash>0 else 'WAITING_FOR_ELIGIBLE_OPPORTUNITY','signals':ranked}

def _v38140_opportunity_intelligence(scores, brain, cash_eur):
    brain_by_asset={str(x.get('asset','')).upper():x for x in (brain or {}).get('signals',[])}
    cash=max(0.0,float(cash_eur or 0)); rows=[]
    for src in scores:
        asset=str(src.get('asset','')).upper(); prod=str(src.get('action') or 'ACOMPANHE').upper(); b=brain_by_asset.get(asset,{})
        b_act=str(b.get('brain_action') or prod).upper(); experimental=bool(b.get('experimental',False)); consolidated=(prod=='COMPRE')
        experimental_buy=(b_act=='COMPRE' and experimental and not consolidated)
        lane='CONSOLIDATED' if consolidated else ('EXPERIMENTAL' if experimental_buy else 'MONITOR')
        display='COMPRE' if consolidated else ('COMPRE*' if experimental_buy else (b.get('display_action') or prod))
        # V38142_OPPORTUNITY_EXPLAINABILITY — descriptive/read-only
        k=float(src.get('promising_pct') or 0); opp=float(src.get('opportunity') or 0); ent=float(src.get('entry') or 0); asym=float(src.get('asymmetry') or 0); risk=float(src.get('risk') or 0)
        checks=[('KPI',k,65,'>='),('OPP',opp,60,'>='),('ENT',ent,55,'>='),('ASY',asym,55,'>='),('RISK',risk,65,'<=')]
        favorable=[]; limiting=[]
        for name,val,thr,op in checks:
            ok=(val>=thr) if op=='>=' else (val<=thr)
            (favorable if ok else limiting).append(f"{name} {val:.1f} {op} {thr:.1f}" if ok else f"{name} {val:.1f} falha {op} {thr:.1f}")
        ar=CFG['action_rules']; pg={'buy_min_promising':float(ar['buy_min_promising']),'buy_min_entry':float(ar['buy_min_entry']),'buy_max_risk':float(ar['buy_max_risk'])}
        pf=[]
        if k<pg['buy_min_promising']: pf.append(f"KPI {k:.1f} < {pg['buy_min_promising']:.1f}")
        if ent<pg['buy_min_entry']: pf.append(f"ENT {ent:.1f} < {pg['buy_min_entry']:.1f}")
        if risk>pg['buy_max_risk']: pf.append(f"RISK {risk:.1f} > {pg['buy_max_risk']:.1f}")
        expl={'schema':'porquinho.opportunity-explainability/1.0','descriptive_only':True,'brain_rule':'NOT_HELD + KPI>=65 + OPP>=60 + ENT>=55 + ASY>=55 + RISK<=65' if experimental_buy else ('PRODUCTION_COMPRE' if consolidated else 'NO_EXPERIMENTAL_BUY'),'favorable_factors':favorable,'limiting_factors':limiting,'production_buy_gate':pg,'production_failed_gates':pf,'raw_features':{q:src.get(q) for q in ('regime','momentum_quality','relative_strength','liquidity','accumulation','reversal_risk')},'allocation_formula':'max(1,KPI) * max(0.2,1-RISK/120) * max(0.5,ENT/100), proporcional dentro da faixa escolhida','automatic_execution':False,'automatic_promotion':False,'production_effect':'NONE'}
        rows.append({'asset':asset,'decision_lane':lane,'display_action':display,'production_action':prod,'brain_action':b_act,'experimental':experimental,'evidence_status':b.get('evidence_status','PRODUCTION_SIGNAL' if consolidated else 'MONITORING'),'confidence_semantics':'EVIDENCE_QUALITY_NOT_PROBABILITY','promising_pct':k,'opportunity':opp,'entry':ent,'asymmetry':asym,'risk':risk,'has_position':float(src.get('current_value_eur') or 0)>0,'suggested_allocation_eur':0.0,'execution':'MANUAL_ONLY','explainability':expl})
    consolidated=[x for x in rows if x['decision_lane']=='CONSOLIDATED']; experimental=[x for x in rows if x['decision_lane']=='EXPERIMENTAL']
    chosen=consolidated if consolidated else experimental; allocation_lane='CONSOLIDATED' if consolidated else ('EXPERIMENTAL' if experimental else 'NONE')
    # V38160_OPPORTUNITY_RANKING_CAPITAL_COMPETITION
    # Describes the already-existing allocation formula. It does not change eligibility,
    # thresholds, target_weights, or execution.
    if chosen and cash>0:
        weights=[max(1.0,x['promising_pct'])*max(.2,1-x['risk']/120)*max(.5,x['entry']/100) for x in chosen]; den=sum(weights) or 1.0
        allocations=[round(cash*w/den,2) for w in weights]
        if allocations: allocations[-1]=round(allocations[-1]+round(cash-sum(allocations),2),2)
        for row,amount,w in zip(chosen,allocations,weights):
            row['suggested_allocation_eur']=amount
            row['_competition_weight']=w
    chosen_ranked=sorted(chosen,key=lambda x:(-float(x.get('_competition_weight') or 0),-x['promising_pct'],-x['opportunity'],x['risk'],x['asset']))
    for pos,row in enumerate(chosen_ranked,1):
        n=len(chosen_ranked); share=(100.0*float(row.get('suggested_allocation_eur') or 0)/cash) if cash>0 else 0.0
        row['capital_competition']={
            'schema':'porquinho.capital-competition/1.0','descriptive_only':True,
            'rank_in_lane':pos,'eligible_in_lane':n,'allocation_share_pct':round(share,1),
            'competition_weight':round(float(row.get('_competition_weight') or 0),4),
            'formula':'max(1,KPI) * max(0.2,1-RISK/120) * max(0.5,ENT/100)',
            'ranking_semantics':'RELATIVE_WITHIN_SELECTED_LANE_NOT_PROBABILITY',
            'allocation_semantics':'PROPORTIONAL_SHARE_OF_AVAILABLE_CASH_NOT_IDEAL_POSITION_SIZE',
            'single_candidate_semantics':'100_PERCENT_ONLY_BECAUSE_NO_OTHER_ELIGIBLE_CANDIDATE_IN_SELECTED_LANE' if n==1 else 'COMPETES_PROPORTIONALLY_WITH_OTHER_ELIGIBLE_CANDIDATES_IN_SELECTED_LANE',
            'lane_priority':'CONSOLIDATED_OVER_EXPERIMENTAL',
            'automatic_execution':False,'automatic_promotion':False,'production_effect':'NONE'
        }
    for row in rows:
        row.pop('_competition_weight',None)
        if 'capital_competition' not in row:
            row['capital_competition']={'schema':'porquinho.capital-competition/1.0','descriptive_only':True,'rank_in_lane':None,'eligible_in_lane':len(chosen_ranked),'allocation_share_pct':0.0,'competition_weight':None,'ranking_semantics':'NOT_IN_SELECTED_ALLOCATION_LANE','allocation_semantics':'NO_ALLOCATION_FROM_CURRENT_SELECTED_LANE','lane_priority':'CONSOLIDATED_OVER_EXPERIMENTAL','automatic_execution':False,'automatic_promotion':False,'production_effect':'NONE'}
    allocated=round(sum(x['suggested_allocation_eur'] for x in rows),2)
    ranked=sorted(rows,key=lambda x:(0 if x['decision_lane']=='CONSOLIDATED' else 1 if x['decision_lane']=='EXPERIMENTAL' else 2,-x['promising_pct'],-x['opportunity'],x['risk'],x['asset']))
    return {'schema':'porquinho.opportunity-intelligence/1.0','mode':'READ_ONLY_DECISION_PROJECTION','cash_available_eur':round(cash,2),'cash_policy':'100_PERCENT_CASH_EVALUATED_NO_FORCED_INVESTMENT','allocation_lane':allocation_lane,'allocated_cash_eur':allocated,'unallocated_cash_eur':round(cash-allocated,2),'consolidated_opportunity_count':len(consolidated),'experimental_opportunity_count':len(experimental),'competition_summary':{'schema':'porquinho.capital-competition-summary/1.0','selected_lane':allocation_lane,'eligible_competitors':len(chosen_ranked),'cash_available_eur':round(cash,2),'single_candidate_is_not_ideal_position_size':len(chosen_ranked)==1,'ranking_is_descriptive':True,'automatic_execution':False,'automatic_promotion':False,'production_effect':'NONE'},'star_semantics':'NOT_CONSOLIDATED_EVIDENCE','confidence_semantics':'EVIDENCE_QUALITY_NOT_PROBABILITY','execution':'MANUAL_ONLY','automatic_execution':False,'automatic_promotion':False,'production_effect':'NONE','opportunities':ranked}

def target_weights(scores, total_wealth):
    eligible=[x for x in scores if x['action'] in ('COMPRE','MANTENHA')]
    eligible=sorted(eligible,key=lambda x:(x['promising_pct']*.55+x['asymmetry']*.20+(100-x['risk'])*.25),reverse=True)[:CFG['max_positions']]
    if not eligible:return {}
    raw=np.array([max(1,x['promising_pct'])*max(.2,1-x['risk']/120)*max(.5,x['entry']/100) for x in eligible],dtype=float)
    raw/=raw.sum(); cap=CFG['position_sizing']['max_position_pct']/100
    weights=np.zeros(len(raw)); free=np.ones(len(raw),dtype=bool); remaining=1.0
    for _ in range(len(raw)+1):
        if not free.any(): break
        idx=np.where(free)[0]; sub=raw[free]; sub=sub/sub.sum()*remaining; over=sub>cap
        if not over.any(): weights[idx]=sub; remaining=0; break
        for j in idx[over]: weights[j]=cap; remaining-=cap; free[j]=False
    return {x['asset']:round(float(w*100),1) for x,w in zip(eligible,weights) if w>0}
