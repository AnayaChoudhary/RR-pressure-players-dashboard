import pandas as pd, numpy as np
df=pd.read_csv('/mnt/user-data/uploads/ball_by_ball.csv')
df['dt']=pd.to_datetime(df.delivery_ist_time)
df=df.sort_values(['match_id','innings','innings_ball_num']).reset_index(drop=True)
# only regular innings 1,2 for pressure (innings 3/4 = super overs, keep separately)
df['is_wide']=df.extras_type.eq('wide')
df['is_nb']=df.extras_type.isin(['Overstep','other'])
df['legal']=~(df.is_wide|df.is_nb)
df['bat_runs']=df.runs
df['team_runs']=df.runs+df.extras1_runs+df.extras_2_runs
# bowler-charged runs: bat runs + wides + noballs extras (not byes/lb)
df['bowl_runs']=np.where(df.extras_type.isin(['wide','Overstep','other','Penalty']),df.runs+df.extras1_runs+df.extras_2_runs,df.runs)
df['is_bowler_wkt']=df.is_wicket & df.dismissal_type.isin(['Caught','Bowled','LBW','Stump','Hit Wicket'])
df['cum_runs']=df.groupby(['match_id','innings']).team_runs.cumsum()
df['cum_wkts']=df.groupby(['match_id','innings']).is_wicket.cumsum()
df['cum_legal']=df.groupby(['match_id','innings']).legal.cumsum()
# state BEFORE the ball
df['runs_before']=df.cum_runs-df.team_runs
df['wkts_before']=df.cum_wkts-df.is_wicket.astype(int)
df['legal_before']=df.cum_legal-df.legal.astype(int)
tot=df[df.innings==1].groupby('match_id').team_runs.sum().rename('inn1_total')
df=df.merge(tot,on='match_id',how='left')
df['target']=df.inn1_total+1
chase=df.innings==2
df['balls_left']=120-df.legal_before
df['runs_needed']=np.where(chase,df.target-df.runs_before,np.nan)
df['rrr']=np.where(chase,df.runs_needed/np.clip(df.balls_left,1,None)*6,np.nan)
df['crr']=df.runs_before/np.clip(df.legal_before,1,None)*6
df['phase']=pd.cut(df.overid,[0,6,15,20],labels=['PP','Middle','Death'])
df['year']=df.dt.dt.year
df.to_pickle('ball.pkl')
print(df.shape)
# sanity: innings 1 totals, chase results
last=df[df.innings==2].groupby('match_id').agg(runs=('cum_runs','max'),target=('target','first'),w=('cum_wkts','max'),b=('cum_legal','max'))
last['won']=last.runs>=last.target
print(last.won.mean(), last.describe())
print(df[df.innings==2].rrr.describe())
print(df[(df.innings==2)].balls_left.describe())
