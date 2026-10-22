import copy,math,unittest
from universal_portfolio import forward_risk_estimator_a24 as risk
from universal_portfolio.explicit_market_bindings_a24 import digest
class Risk(unittest.TestCase):
 def setUp(self):
  self.body={'binding':{'instrument_id':'synthetic','provider':'test','provider_id':'one','quote_currency':'TST'},'observations':[{'observation_date':f'2026-01-{i+1:02d}','provider_observed_at':f'2026-01-{i+1:02d}T00:00:00+00:00','price':'100'} for i in range(8)]}
  folds=[{'origin':f'2026-01-{i+1:02d}','target_observed_at':f'2026-01-{i+2:02d}','last_training_label_end':f'2026-01-{i:02d}','prediction':p,'realized_return':0.0} for i,p in ((1,.1),(3,-.1),(5,.2))]
  self.e={**self.body['binding'],'source_body_sha256':digest(self.body),'horizon_unit':'OBSERVATIONS','horizon_value':1,'forecast':{'value':0.0,'horizon_unit':'OBSERVATIONS','horizon_value':1,'as_of_provider_observation':self.body['observations'][-1]['provider_observed_at']},'evaluation':{'fold_boundaries':folds}}
 def test_known_empirical_risk_and_no_mutation(self):
  before=copy.deepcopy((self.body,self.e));r=risk.estimate(self.body,self.e);self.assertEqual(r['residual_sample_count'],3);self.assertAlmostEqual(r['risk_estimate']['value'],math.sqrt(.05/3));self.assertAlmostEqual(r['risk_estimate']['negative_scenario_fraction'],2/3);self.assertEqual(before,(self.body,self.e));self.assertFalse(r['comparison_authorized'])
 def test_crps_matches_known_two_point_distribution(self):self.assertAlmostEqual(risk.crps([0.0,1.0],0.0),.25)
 def test_prequential_distribution_uses_only_matured_errors(self):
  r=risk.estimate(self.body,self.e);scores=r['retrospective_distribution_evaluation']['folds'];self.assertEqual(len(scores),1);self.assertLess(scores[0]['last_calibration_target'],scores[0]['origin'])
 def test_future_prediction_change_cannot_change_prior_score(self):
  # Add a later fold: previous distribution evaluation must stay identical.
  before=risk.estimate(self.body,self.e)['retrospective_distribution_evaluation']['folds']
  self.e['evaluation']['fold_boundaries'].append({'origin':'2026-01-07','target_observed_at':'2026-01-08','last_training_label_end':'2026-01-06','prediction':.9,'realized_return':0.0})
  r=risk.estimate(self.body,self.e);self.assertEqual(r['retrospective_distribution_evaluation']['folds'][:len(before)],before);self.assertEqual(r['residual_sample_count'],3)
 def test_in_sample_training_endpoint_rejected(self):
  self.e['evaluation']['fold_boundaries'][0]['last_training_label_end']='2026-01-02'
  self.assertEqual(risk.safe_estimate(self.body,self.e)['status'],'FORWARD_RISK_SOURCE_REJECTED')
 def test_changed_source_rejected(self):
  self.body['observations'][0]['price']='101';self.assertEqual(risk.safe_estimate(self.body,self.e)['reason'],'EXACT_RISK_SOURCE_REQUIRED')
 def test_wrong_outcome_rejected(self):
  self.e['evaluation']['fold_boundaries'][0]['realized_return']=.9
  self.assertEqual(risk.safe_estimate(self.body,self.e)['reason'],'RISK_OUTCOME_SOURCE_MISMATCH')
 def test_unphysical_returns_not_clipped(self):
  self.e['forecast']['value']=-2.;r=risk.estimate(self.body,self.e);self.assertIsNone(r['risk_estimate']);self.assertEqual(r['status'],'PROJECTED_RETURN_SUPPORT_INVALID_NO_CLIPPING')
 def test_insufficient_residuals_not_zero_risk(self):
  self.e['evaluation']['fold_boundaries']=self.e['evaluation']['fold_boundaries'][:1];r=risk.estimate(self.body,self.e);self.assertIsNone(r['risk_estimate']);self.assertEqual(r['status'],'INSUFFICIENT_MATURED_FORECAST_RESIDUALS')
 def test_no_calendar_horizon_promotion(self):self.assertFalse(risk.estimate(self.body,self.e)['calendar_day_horizon_inferred'])
if __name__=='__main__':unittest.main()

class Pipeline(unittest.TestCase):
 def test_existing_producer_carries_separate_estimate_without_rewriting_old_components(self):
  import test_a24_research_economic_components as f
  from universal_portfolio import research_economic_components_a24 as c
  obj=f.Components();obj.setUp()
  try:
   obj.seed();before={p:p.read_bytes() for p in obj.root.rglob('*') if p.is_file()};obj.runproducer();packet=obj.read();estimate=packet['forward_risk_estimate']
   self.assertEqual(estimate['status'],'EMPIRICAL_FORWARD_RISK_ESTIMATED_RESEARCH_ONLY')
   self.assertEqual(packet['components']['risk_measure']['status'],'HISTORICAL_DESCRIPTION_NOT_FORWARD_RISK')
   self.assertEqual(packet['components']['forward_return']['validation_status'],'NOT_VALIDATED_FOR_COMPARATOR')
   view=c.summary(obj.root,obj.demand,now=f.NOW,include_scoped=True)
   self.assertEqual(view['forward_risk_status_counts']['EMPIRICAL_FORWARD_RISK_ESTIMATED_RESEARCH_ONLY'],1)
   self.assertEqual(view['contexts'][0]['forward_risk_estimate'],estimate)
   for p,b in before.items():self.assertEqual(p.read_bytes(),b)
  finally:obj.doCleanups()
