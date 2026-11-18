import pandas as pd, numpy as np
pd.set_option('display.width',320,'display.max_columns',100,'display.max_rows',300)
df=pd.read_pickle('ball_wp.pkl'); mt=pd.read_pickle('mt.pkl'); pl=pd.read_pickle('pl.pkl')
df['ipl']=df.match_id.map(mt.ipl)
df['PB']=((df.innings==2)&(df.LI>=1.5))|((df.innings==1)&(df.wkts_before>=3)&(df.overid<=10))
df['PW']=((df.innings==2)&(df.LI>=1.5))|(df.overid>=17)
def z(s): return (s-s.mean())/s.std()
K=60
# ---------- IPL-only RR profile ----------
I=df[df.ipl]
def prof(col,team):
    x=I[I[col]==team]; return x
rows=[]
for t in sorted(set(I.batting_team_id)):
    b=I[I.batting_team_id==t]; w=I[I.bowling_team_id==t]
    r={'team':t}
    for ph in ['PP','Middle','Death']:
        bb=b[b.phase==ph]; ww=w[w.phase==ph]
        r['bat_'+ph]=bb.team_runs.sum()/bb.legal.sum()*6
        r['bowl_'+ph]=ww.bowl_runs.sum()/ww.legal.sum()*6
        r['wk_'+ph]=ww.legal.sum()/ww.is_bowler_wkt.sum()
    hb=b[(b.innings==2)&(b.LI>=1.5)&~b.is_wide]; hw=w[(w.innings==2)&(w.LI>=1.5)]
    r['hp_bat_sr']=hb.bat_runs.sum()/len(hb)*100; r['hp_bowl_econ']=hw.bowl_runs.sum()/hw.legal.sum()*6
    ch=b[b.innings==2].groupby('match_id').bat_win.first(); r['chase_win']=ch.mean(); r['chases']=len(ch)
    rows.append(r)
T=pd.DataFrame(rows).set_index('team')
tn=pd.read_csv('/mnt/user-data/uploads/competition_team_player_mapping.csv').drop_duplicates('team_id').set_index('team_id').team_name
T.index=T.index.map(tn)
rk=T.copy()
for c in T.columns: rk[c]=T[c].rank(ascending=('bowl' in c or c.startswith('wk_')),method='min')
print(T.round(2).T)
print('RR ranks of 10 (1=best):'); print(rk.loc['Rajasthan Royals'])
# ---------- player metrics, baseline by ipl flag ----------
bt=df[~df.is_wide].copy()
bt['out']=bt.is_wicket&(bt.dismissed_player_id==bt.striker_id)
bt['exp']=bt.groupby(['ipl','innings','overid']).bat_runs.transform('mean')
bt['bnd']=bt.is_four|bt.is_six; bt['dot']=bt.bat_runs==0
bt['rae']=bt.bat_runs-bt.exp
P=bt[bt.PB]
g=P.groupby('striker_id').agg(name=('striker_name','first'),hand=('batting_type','first'),pos=('batting_order','median'),b=('rae','size'),runs=('bat_runs','sum'),
    outs=('out','sum'),bnd=('bnd','sum'),dots=('dot','sum'),rae=('rae','sum'),wpa=('wpa','sum'),inns=('match_id','nunique'))
ip=P[P.ipl].groupby('striker_id').agg(ib=('rae','size'),ir=('bat_runs','sum'))
g=g.join(ip).fillna({'ib':0,'ir':0}); g['i_sr']=g.ir/g.ib.replace(0,np.nan)*100
last=df.groupby('striker_id').dt.max()
g['last']=last
base=lambda c:g[c].sum()/g.b.sum()
g['bnd_s']=(g.bnd+K*base('bnd'))/(g.b+K)*100
g['out_s']=(g.outs+K*base('outs'))/(g.b+K)*100
g['dot_s']=(g.dots+K*base('dots'))/(g.b+K)*100
g['rae_s']=(g.rae)/(g.b+K)*100
g['wpa100']=g.wpa/(g.b+80)*10000
g['sr']=g.runs/g.b*100
q=g[(g.b>=100)&(g['last']>=pd.Timestamp('2025-06-01',tz='UTC'))].copy()
q['score']=0.28*z(q.bnd_s)+0.22*z(q.rae_s)+0.20*(-z(q.out_s))+0.10*(-z(q.dot_s))+0.10*z(q.wpa100)+0.10*z(q.inns.clip(upper=30))
q=q.join(pl)
q['ipl26']=q.ipl26.fillna('—')
q=q.sort_values('score',ascending=False)
print(q[['name','hand','pos','b','inns','sr','bnd_s','out_s','dot_s','i_sr','ib','nat','ipl26','iplyrs','score']].head(40).round(2))
q.to_pickle('q_bat.pkl')
# bowlers
bw=df.copy()
bw['exp']=bw.groupby(['ipl','innings','overid']).bowl_runs.transform('mean')
bw['wk']=bw.is_bowler_wkt; bw['dot']=(bw.bowl_runs==0)&bw.legal; bw['bc']=bw.is_four|bw.is_six
PW=bw[bw.PW]
w=PW.groupby('bowler_id').agg(name=('bowler_name','first'),btype=('bowling_type','first'),ps=('pace_or_spin','first'),d=('legal','size'),b=('legal','sum'),
   runs=('bowl_runs','sum'),wk=('wk','sum'),dots=('dot','sum'),bc=('bc','sum'),wpa=('wpa','sum'),mats=('match_id','nunique'))
ipw=PW[PW.ipl].groupby('bowler_id').agg(ib=('legal','sum'),ir=('bowl_runs','sum'),iwk=('wk','sum'))
w=w.join(ipw).fillna({'ib':0,'ir':0,'iwk':0}); w['i_econ']=w.ir/w.ib.replace(0,np.nan)*6
dd=df[df.overid>=17].groupby('bowler_id').agg(db=('legal','sum'),dr=('bowl_runs','sum')); w=w.join(dd); w['d_econ']=w.dr/w.db*6
w['last']=df.groupby('bowler_id').dt.max()
Kb=100
bs=lambda c,n:(w[c]+Kb*w[c].sum()/w[n].sum())/(w[n]+Kb)
w['econ_s']=(w.runs+Kb*w.runs.sum()/w.b.sum())/(w.b+Kb)*6
w['wk_s']=bs('wk','b')*24; w['dot_s']=bs('dots','d')*100; w['bc_s']=bs('bc','d')*100
w['wpa100']=-w.wpa/(w.d+80)*10000
w=w.join(pl)
qw=w[(w.d>=150)&(w['last']>=pd.Timestamp('2025-06-01',tz='UTC'))].copy()
qw['score']=0.30*(-z(qw.econ_s))+0.25*z(qw.wk_s)+0.15*z(qw.dot_s)+0.15*(-z(qw.bc_s))+0.10*z(qw.wpa100)+0.05*z(qw.mats.clip(upper=30))
qw['ipl26']=qw.ipl26.fillna('—'); qw=qw.sort_values('score',ascending=False)
print(qw[['name','btype','b','econ_s','wk_s','dot_s','bc_s','i_econ','ib','d_econ','db','nat','ipl26','iplyrs','score']].head(40).round(2))
qw.to_pickle('q_bowl.pkl')
