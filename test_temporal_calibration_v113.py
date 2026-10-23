import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from universal_portfolio.temporal_calibration_a24 import folds, walk_forward

ROOT = Path(os.environ.get('PORQUINHO_TEST_ROOT','/workspace/porquinho-a24/project'))
spec=importlib.util.spec_from_file_location('training_v113_test',ROOT/'training.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)

class Temporal(unittest.TestCase):
    def sample(self,n=240):
        dates=pd.date_range('2020-01-01',periods=n,tz='UTC')
        return np.column_stack((np.arange(n),np.sin(np.arange(n)),np.ones(n))),np.arange(n,dtype=float),dates,dates+pd.Timedelta(days=90)
    def test_every_training_label_strictly_matured_before_test(self):
        X,y,d,l=self.sample()
        seen=0
        for train,test,a,b in folds(X,y,d,l,min_train_dates=60):
            self.assertTrue((l[train] < d[test][0]).all())
            self.assertGreaterEqual(len(set(d[train])),60)
            seen+=1
        self.assertGreater(seen,0)
    def test_same_date_label_is_excluded(self):
        X,y,d,l=self.sample()
        for train,test,*_ in folds(X,y,d,l,min_train_dates=60):
            self.assertNotIn(test[0]-90,train)
    def test_scaling_fitted_only_on_training(self):
        X,y,d,l=self.sample()
        train,test,a,b=next(folds(X,y,d,l,min_train_dates=60))
        np.testing.assert_allclose(a.mean(axis=0),0,atol=1e-14)
        self.assertEqual(a[:,2].tolist(),[0]*len(train))
        expected=(X[test]-X[train].mean(axis=0))/np.where(X[train].std(axis=0,ddof=1)==0,1,X[train].std(axis=0,ddof=1))
        np.testing.assert_allclose(b,expected)
    def test_future_outlier_cannot_change_earlier_normalization(self):
        X,y,d,l=self.sample()
        original=next(folds(X,y,d,l,min_train_dates=60))
        X[-1]=1e20
        changed=next(folds(X,y,d,l,min_train_dates=60))
        np.testing.assert_array_equal(original[2],changed[2])
        np.testing.assert_array_equal(original[3],changed[3])
    def test_missing_label_timestamps_refused(self):
        X,y,d,_=self.sample()
        with self.assertRaisesRegex(ValueError,'MATURITY'):t.walk_forward(X,y,d)
    def test_future_targets_not_in_training_even_when_origins_precede_test(self):
        X,y,d,l=self.sample()
        l=d+pd.Timedelta(days=500)
        self.assertEqual(list(folds(X,y,d,l,min_train_dates=60)),[])
    def test_insufficient_folds_never_fabricate_activation_metrics(self):
        X,y,d,l=self.sample(100)
        out=walk_forward(X,y,d,label_dates=l,ridge_fit=t.ridge_fit,min_train_dates=60)
        self.assertEqual(out['n'],0);self.assertIsNone(out['corr']);self.assertIsNone(out['directional_hit_rate'])
    def test_metrics_and_ridge_are_computed_from_purged_folds(self):
        X,y,d,l=self.sample()
        out=walk_forward(X,y,d,label_dates=l,ridge_fit=t.ridge_fit,min_train_dates=60)
        self.assertGreater(out['n'],10);self.assertTrue(out['label_maturity_purged']);self.assertTrue(out['normalization_fit_on_training_only'])
    def test_invalid_data_refused(self):
        X,y,d,l=self.sample()
        X[0,0]=np.inf
        with self.assertRaisesRegex(ValueError,'FINITE'):list(folds(X,y,d,l,min_train_dates=60))
        X[0,0]=0
        with self.assertRaisesRegex(ValueError,'AFTER'):list(folds(X,y,d,d,min_train_dates=60))
    def history(self):
        return pd.DataFrame({'date':pd.date_range('2020-01-01',periods=200,tz='UTC'),'asset':'SYNTHETIC','price_eur':np.linspace(100,180,200),'volume_eur':1e6,'market_cap_eur':1e8})
    def test_maturity_uses_actual_ninetieth_observation_not_calendar_guess(self):
        df=self.history();df['date']=pd.bdate_range('2020-01-01',periods=200,tz='UTC')
        x=t.make_features(df)
        self.assertEqual(x.iloc[0]['target_observed_at'],df.iloc[90]['date'])
        self.assertGreater((x.iloc[0]['target_observed_at']-x.iloc[0]['date']).days,90)
    def test_intraday_duplicates_rejected(self):
        df=self.history();df.loc[1,'date']=df.loc[0,'date']+pd.Timedelta(minutes=10)
        with self.assertRaisesRegex(ValueError,'ONE_DAILY'):t.make_features(df)
    def test_brl_not_relabelled_eur(self):
        df=self.history();df['quote_currency']='BRL'
        with self.assertRaisesRegex(ValueError,'EUR_HISTORY'):t.make_features(df)
    def test_feature_formula_and_ridge_unchanged(self):
        ns={'np':np,'pd':pd,'FEATURES':t.FEATURES}
        exec(compile(ORIGINAL_PURE_FUNCTIONS,'original','exec'),ns)
        oldx=ns['make_features'](self.history());newx=t.make_features(self.history())
        np.testing.assert_allclose(oldx[t.FEATURES+['forward_90d']],newx[t.FEATURES+['forward_90d']])
        X,y,_,_=self.sample()
        np.testing.assert_array_equal(ns['ridge_fit'](X,y),t.ridge_fit(X,y))

ORIGINAL_PURE_FUNCTIONS="def clamp(x): return np.clip(x,0,100)\n\ndef make_features(df):\n    x=df.copy(); x['date']=pd.to_datetime(x['date']); x=x.sort_values(['asset','date'])\n    x['ch7']=x.groupby('asset').price_eur.pct_change(7)*100; x['ch30']=x.groupby('asset').price_eur.pct_change(30)*100\n    # Identity-neutral cross-sectional methodological reference.\n    # Legacy btc7/btc30 column names remain only for model/schema compatibility.\n    reference=x.groupby('date',as_index=False)[['ch7','ch30']].median().rename(columns={'ch7':'btc7','ch30':'btc30'})\n    x=x.merge(reference,on='date',how='left')\n    x['btc7']=x['btc7'].fillna(0); x['btc30']=x['btc30'].fillna(0)\n    x['liq_ratio']=(x['volume_eur']/x['market_cap_eur']).replace([np.inf,-np.inf],np.nan).fillna(0)\n    x['momentum']=clamp(50+x.ch7.fillna(0)*2.2+x.ch30.fillna(0)*.7)\n    x['rs']=clamp(50+(x.ch7.fillna(0)-x.btc7)*2+(x.ch30.fillna(0)-x.btc30)*.4)\n    x['liquidity']=clamp(35+np.minimum(55,x.liq_ratio*180))\n    x['accumulation']=clamp(45+x.liq_ratio*2600+np.maximum(x.ch7.fillna(0),0)*.6)\n    x['reversal']=clamp(30+np.maximum(x.ch7.fillna(0)-12,0)*3+np.maximum(x.ch30.fillna(0)-35,0)*1.2)\n    x['entry']=clamp(72+np.minimum(10,np.maximum(-10,-x.ch7.fillna(0)*.7))-np.maximum(x.ch7.fillna(0)-8,0)*2-np.maximum(x.ch7.fillna(0)-18,0))\n    x.loc[(x.ch7<-12)&(x.ch30<-15),'entry']-=8\n    x['risk']=clamp(25+abs(x.ch7.fillna(0))*.9+np.maximum(0,35-x.liquidity)*.45)\n    x['opportunity']=clamp(.20*x.momentum+.18*x.rs+.12*x.liquidity+.10*x.accumulation+.20*(100-x.reversal)+.10*55+.10*np.where(x.market_cap_eur>5e9,70,55))\n    x['asymmetry']=clamp(55+(100-x.risk)*.35+np.maximum(0,75-x.momentum)*.15)\n    # Regime proxy: identity-neutral cross-sectional reference vs cross-sectional median.\n    cross=x.groupby('date')['ch30'].transform('median').fillna(0)\n    x['regime']=clamp(50+(x.btc30-cross)*.7)\n    x['risk_inverse']=100-x.risk\n    x['forward_90d']=x.groupby('asset').price_eur.shift(-90)/x.price_eur*100-100\n    return x.dropna(subset=['forward_90d']+FEATURES)\n\ndef ridge_fit(X,y,alpha=1.0):\n    X1=np.c_[np.ones(len(X)),X]\n    reg=np.eye(X1.shape[1]); reg[0,0]=0\n    return np.linalg.solve(X1.T@X1+alpha*reg,X1.T@y)"

if __name__=='__main__':unittest.main()
