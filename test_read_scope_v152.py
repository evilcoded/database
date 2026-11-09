"""Request isolation and complete-input reuse; no persistent cache or stale values."""
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import pytest
from universal_portfolio import read_inspection_scope_a24 as cache
from brain.evolution import global_research_lab_a24 as lab


def test_reuse_content_time_path_and_defensive_copy():
 calls=[]
 @cache.reuse_identical_check
 def compute(body, *, now, path=None):
  calls.append(1);return {'value':body['value'], 'nested':[]}
 @cache.inspection_scope
 def run():
  a=compute({'value':1},now='a',path='x');a['nested'].append('modified')
  assert compute({'value':1},now='a',path='x')['nested']==[]
  compute({'value':2},now='a',path='x');compute({'value':1},now='b',path='x');compute({'value':1},now='a',path='y')
 run();assert len(calls)==4
 run();assert len(calls)==8
 compute({'value':1},now='a');compute({'value':1},now='a');assert len(calls)==10


def test_failure_reset_and_no_cached_errors():
 calls=[]
 @cache.reuse_identical_check
 def invalid(body):calls.append(1);raise ValueError('INVALID')
 @cache.inspection_scope
 def run():
  for _ in range(2):
   with pytest.raises(ValueError):invalid({})
  raise RuntimeError('RESET')
 with pytest.raises(RuntimeError):run()
 assert len(calls)==2 and cache._SCOPE.get() is None


def test_limits_and_thread_isolation():
 calls=[]
 @cache.reuse_identical_check
 def read(value):calls.append(value);return [value]
 @cache.inspection_scope
 def run():
  assert read(1)==read(1)
 with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda _:run(),range(2)))
 assert len(calls)==2
 with patch.object(cache,'MAX_BYTES',0):run()
 assert len(calls)==4


def test_real_experiment_exact_output_and_repeated_validation():
 now=dt.datetime(2026,11,9,tzinfo=dt.timezone.utc)
 # Synthetic contract, validation mocked only to count the real experiment path.
 body={'binding':{'instrument_id':'CONTROL','provider':'CONTROL','provider_id':'CONTROL','quote_currency':'BRL'},'fetched_at':now.isoformat(),'series_id':'CONTROL','sampling':'DAILY','observations':[{'observation_date':now.date().isoformat(),'provider_observed_at':now.isoformat(),'price':'1'}]}
 with patch.object(lab.history,'validate_bundle',side_effect=lambda value:value) as validate:
  expected=lab.experiment(body,now=now)
  @cache.inspection_scope
  def run():
   assert lab.experiment(body,now=now)==expected
   assert lab.experiment(body,now=now)==expected
  run();assert validate.call_count==2 # one uncached reference + one request check
  run();assert validate.call_count==3


def test_real_history_forecast_unchanged_and_tampering_rejected():
 import copy
 from test_a24_global_research_lab import Lab, NOW
 f=Lab();f.setUp()
 try:
  body=f.body();expected=lab.experiment(body,now=NOW)
  with patch.object(lab,'fit_predict',wraps=lab.fit_predict) as fit:
   @cache.inspection_scope
   def run():
    assert lab.experiment(body,now=NOW)==expected
    first=fit.call_count
    assert first>20
    assert lab.experiment(copy.deepcopy(body),now=NOW)==expected
    assert fit.call_count==first
    changed=copy.deepcopy(body);changed['observations'][0]['price']='999999'
    with pytest.raises(ValueError):lab.experiment(changed,now=NOW)
    return first
   first=run();assert fit.call_count==first
   run();assert fit.call_count==first*2
 finally:f.doCleanups()
