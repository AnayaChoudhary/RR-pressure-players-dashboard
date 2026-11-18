import pandas as pd, numpy as np
pd.set_option('display.width',280,'display.max_columns',100,'display.max_rows',300)
df=pd.read_pickle('ball_wp.pkl')
# ---------- pressure flags ----------
df['A']=(df.innings==2)&(df.LI>=1.5)                      # live chase, high leverage
df['C']=(df.innings==1)&(df.wkts_before>=3)&(df.overid<=10)   # rebuild after early wickets
df['D']=(df.overid>=17)                                    # death overs (bowler skill)
df['PB']=df.A|df.C                                          # batter pressure
df['PW']=df.A|df.D                                          # bowler pressure
# baselines: expected bat runs per legal-faced ball by (innings, over)
bt=df[~df.is_wide].copy()
base_b=bt.groupby(['innings','overid']).bat_runs.mean().rename('exp_bat')
bt=bt.merge(base_b.reset_index(),on=['innings','overid'])
bt['dismissed']=bt.is_wicket&(bt.dismissed_player_id==bt.striker_id)
# value of a dismissal in runs (avg runs a wicket costs ~ use league avg runs lost). calibrate: ~ 7 runs for PP/mid... use over-specific from wpa ratio
# simpler: runs-above-expected incl dismissal penalty of 7 runs
bt['rae']=bt.bat_runs-bt.exp_bat-7*bt.dismissed.astype(float)*0  # raw (no penalty) kept separately
bt['rae_pen']=bt.bat_runs-bt.exp_bat-6.0*bt.dismissed
bt['dot']=(bt.bat_runs==0)&bt.legal
bt['bnd']=bt.is_four|bt.is_six
bt['year']=bt.dt.dt.year
bt['half']=np.where(bt.dt<pd.Timestamp('2024-07-01',tz='UTC'),'H1','H2')
def bat_table(d,tag):
    g=d.groupby('striker_id').agg(name=('striker_name','first'),hand=('batting_type','first'),
        balls=('bat_runs','size'),runs=('bat_runs','sum'),outs=('dismissed','sum'),dots=('dot','sum'),bnds=('bnd','sum'),
        wpa=('wpa','sum'),rae=('rae_pen','sum'),inns=('match_id','nunique'),pos=('batting_order','median'))
    g.columns=[f'{tag}_{c}' if c not in('name','hand','pos') else c for c in g.columns]
    return g
P=bt[bt.PB]; N=bt[~bt.PB]
bp=bat_table(P,'p'); bn=bat_table(N,'n')
B=bp.join(bn[[c for c in bn.columns if c.startswith('n_')]],how='left').fillna(0)
# overall
tot=bt.groupby('striker_id').agg(t_balls=('bat_runs','size'),t_runs=('bat_runs','sum'))
B=B.join(tot)
B['p_sr']=B.p_runs/B.p_balls*100
B['p_dot']=B.p_dots/B.p_balls*100
B['p_bnd']=B.p_bnds/B.p_balls*100
B['p_bpd']=B.p_balls/B.p_outs.replace(0,np.nan)
B['n_sr']=B.n_runs/B.n_balls.replace(0,np.nan)*100
K=80  # shrinkage balls
B['wpa100']=B.p_wpa/(B.p_balls+K)*100*100  # in WP% points per 100 balls
B['rae100']=B.p_rae/(B.p_balls+K)*100
# innings-level hit rate
inn=P.groupby(['striker_id','match_id']).agg(w=('wpa','sum'),b=('bat_runs','size'),r=('bat_runs','sum'),o=('dismissed','max'),rae=('rae_pen','sum')).reset_index()
inn=inn[inn.b>=6]
hr=inn.groupby('striker_id').agg(p_inn=('w','size'),pos_inn=('w',lambda s:(s>0).sum()),rae_pos=('rae',lambda s:(s>0).sum()))
B=B.join(hr)
B['hit']=(B.pos_inn+2)/(B.p_inn+4)   # shrunk to 50%
B['hit_rae']=(B.rae_pos+2)/(B.p_inn+4)
# split-half stability
for h in ['H1','H2']:
    x=P[P.half==h].groupby('striker_id').agg(b=('bat_runs','size'),w=('wpa','sum'),r=('rae_pen','sum'))
    B[f'{h}_b']=x.b; B[f'{h}_w']=x.w/(x.b+K)*100*100; B[f'{h}_r']=x.r/(x.b+K)*100
B=B.fillna({'H1_b':0,'H2_b':0})
B.to_pickle('B.pkl')
# validation: split-half correlation
v=B[(B.H1_b>=40)&(B.H2_b>=40)]
print('n for split-half',len(v),'corr WPA/100',v.H1_w.corr(v.H2_w),'corr RAE/100',v.H1_r.corr(v.H2_r))
# compare with non-pressure SR consistency
print('pressure balls total',len(P),'players',len(B))
# ---------- bowlers ----------
bw=df.copy()
bw['year']=bw.dt.dt.year
base_w=bw.groupby(['innings','overid']).bowl_runs.mean()  # per delivery incl extras
base_w=base_w.rename('exp_bowl').reset_index()
bw=bw.merge(base_w,on=['innings','overid'])
bw['wk']=bw.is_bowler_wkt
bw['rs']=bw.exp_bowl-bw.bowl_runs+6.0*bw.wk   # runs saved incl wicket value
bw['dot']=(bw.bowl_runs==0)&bw.legal
bw['bnd_c']=bw.is_four|bw.is_six
bw['half']=np.where(bw.dt<pd.Timestamp('2024-07-01',tz='UTC'),'H1','H2')
def bowl_table(d,tag):
    g=d.groupby('bowler_id').agg(name=('bowler_name','first'),btype=('bowling_type','first'),ps=('pace_or_spin','first'),
        balls=('legal','sum'),dels=('legal','size'),runs=('bowl_runs','sum'),wk=('wk','sum'),dots=('dot','sum'),bnd=('bnd_c','sum'),
        wpa=('wpa','sum'),rs=('rs','sum'),mat=('match_id','nunique'))
    g.columns=[f'{tag}_{c}' if c not in('name','btype','ps') else c for c in g.columns]
    return g
PW=bw[bw.PW]
W=bowl_table(PW,'p')
W['p_econ']=W.p_runs/W.p_balls*6
W['p_dotp']=W.p_dots/W.p_dels*100
W['p_bndp']=W.p_bnd/W.p_dels*100
W['p_bpw']=W.p_balls/W.p_wk.replace(0,np.nan)
W['wpa100']=-W.p_wpa/(W.p_dels+K)*100*100
W['rs100']=W.p_rs/(W.p_dels+K)*100
tw=bw.groupby('bowler_id').agg(t_balls=('legal','sum'),t_runs=('bowl_runs','sum'))
W=W.join(tw); W['t_econ']=W.t_runs/W.t_balls*6
# per-match spell hit rate (≥6 pressure deliveries)
sp=PW.groupby(['bowler_id','match_id']).agg(d=('legal','size'),rs=('rs','sum')).reset_index()
sp=sp[sp.d>=6]
hw=sp.groupby('bowler_id').agg(p_sp=('rs','size'),pos_sp=('rs',lambda s:(s>0).sum()))
W=W.join(hw); W['hit']=(W.pos_sp+2)/(W.p_sp+4)
for h in ['H1','H2']:
    x=PW[PW.half==h].groupby('bowler_id').agg(b=('legal','size'),r=('rs','sum'))
    W[f'{h}_b']=x.b; W[f'{h}_r']=x.r/(x.b+K)*100
W=W.fillna({'H1_b':0,'H2_b':0})
W.to_pickle('W.pkl')
v=W[(W.H1_b>=40)&(W.H2_b>=40)]
print('bowler split-half n',len(v),'corr RS/100',v.H1_r.corr(v.H2_r))
print(PW.shape, len(W))
