import pandas as pd, numpy as np
pd.set_option('display.width',300,'display.max_columns',100,'display.max_rows',300)
B=pd.read_pickle('B.pkl'); W=pd.read_pickle('W.pkl')
df=pd.read_pickle('ball_wp.pkl')
last=pd.concat([df.groupby('striker_id').dt.max(),df.groupby('bowler_id').dt.max()],axis=1,keys=['a','b'])
lastbat=df.groupby('striker_id').dt.max(); lastbowl=df.groupby('bowler_id').dt.max()
def z(s): return (s-s.mean())/s.std()
# ---- BATTERS ----
Bq=B[(B.p_balls>=100)&(B.p_inn>=8)].copy()
Bq['last']=lastbat.reindex(Bq.index)
Bq=Bq[Bq.last>=pd.Timestamp('2025-01-01',tz='UTC')]
k=60
mean_bnd=B.p_bnds.sum()/B.p_balls.sum()
Bq['bnd_s']=(Bq.p_bnds+k*mean_bnd)/(Bq.p_balls+k)*100
mean_o=B.p_outs.sum()/B.p_balls.sum()
Bq['out_s']=(Bq.p_outs+k*mean_o)/(Bq.p_balls+k)*100          # outs per 100 balls (lower better)
mean_dot=B.p_dots.sum()/B.p_balls.sum()
Bq['dot_s']=(Bq.p_dots+k*mean_dot)/(Bq.p_balls+k)*100
Bq['sr_s']=(Bq.p_runs+k*(B.p_runs.sum()/B.p_balls.sum()))/(Bq.p_balls+k)*100
Bq['score']=(0.28*z(Bq.bnd_s)+0.22*z(Bq.sr_s)+0.20*(-z(Bq.out_s))+0.10*(-z(Bq.dot_s))+0.10*z(Bq.wpa100)+0.10*z(Bq.hit))
Bq['n_sr']=Bq.n_runs/Bq.n_balls*100
Bq=Bq.sort_values('score',ascending=False)
cols=['name','hand','pos','p_balls','p_inn','p_sr','p_bnd','p_dot','p_bpd','wpa100','hit','n_sr','t_balls','score']
print(Bq[cols].head(30).round(2))
Bq.to_pickle('Bq.pkl')
print(len(Bq))
# ---- BOWLERS ----
Wq=W[(W.p_dels>=120)&(W.p_sp>=8)].copy()
Wq['last']=lastbowl.reindex(Wq.index)
Wq=Wq[Wq.last>=pd.Timestamp('2025-01-01',tz='UTC')]
k=60
Wq['econ_s']=(Wq.p_runs+k*(W.p_runs.sum()/W.p_balls.sum()*(Wq.p_balls/Wq.p_balls)))/(Wq.p_balls+k)*6  # rough shrink
Wq['wk_s']=(Wq.p_wk+k*(W.p_wk.sum()/W.p_balls.sum()))/(Wq.p_balls+k)*24  # wickets per 4 overs
Wq['dot_s']=(Wq.p_dots+k*(W.p_dots.sum()/W.p_dels.sum()))/(Wq.p_dels+k)*100
Wq['bnd_s']=(Wq.p_bnd+k*(W.p_bnd.sum()/W.p_dels.sum()))/(Wq.p_dels+k)*100
Wq['score']=(0.30*(-z(Wq.econ_s))+0.25*z(Wq.wk_s)+0.15*z(Wq.dot_s)+0.15*(-z(Wq.bnd_s))+0.10*z(Wq.wpa100)+0.05*z(Wq.hit))
Wq['t_econ']=Wq.t_runs/Wq.t_balls*6
Wq=Wq.sort_values('score',ascending=False)
cols=['name','btype','p_balls','p_sp','p_econ','p_wk','p_bpw','p_dotp','p_bndp','wpa100','hit','t_econ','score']
print(Wq[cols].head(30).round(2))
Wq.to_pickle('Wq.pkl'); print(len(Wq))
