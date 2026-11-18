import pandas as pd, numpy as np
pd.set_option('display.width',300,'display.max_columns',100,'display.max_rows',300)
m=pd.read_csv('/mnt/user-data/uploads/competition_team_player_mapping.csv')
df=pd.read_pickle('ball_wp.pkl')
tn=m.drop_duplicates('team_id').set_index('team_id').team_name
ipl_teams=set(m[m.comp_name.str.startswith('IPL')].team_id)
print({t:tn[t] for t in ipl_teams})
mt=df.groupby('match_id').agg(t1=('batting_team_id','first'),dt=('dt','min')).join(df.groupby('match_id').bowling_team_id.first().rename('t2'))
mt['ipl']=mt.t1.isin(ipl_teams)&mt.t2.isin(ipl_teams)
mt['year']=mt.dt.dt.year
print(mt.groupby('year').ipl.agg(['sum','size']))
print(mt[mt.ipl].groupby('year').size())
# T20I matches count with national
print(mt[~mt.ipl].t1.map(tn).value_counts().head(12))
mt.to_pickle('mt.pkl')
# nationality: player -> national teams (team_id<=... non-IPL non-A teams)
nat_teams=set(tn.index)-ipl_teams
nat=m[m.team_id.isin(nat_teams)&~m.team_name.str.contains(' A$')].groupby('player_id').team_name.agg(lambda s:s.value_counts().index[0])
ipl26=m[m.comp_name=='IPL 2026'].set_index('player_id').team_name
iplyears=m[m.comp_name.str.startswith('IPL')].groupby('player_id').comp_name.agg(lambda s:','.join(sorted(x[-4:] for x in s.unique())))
pl=pd.DataFrame({'nat':nat,'ipl26':ipl26,'iplyrs':iplyears})
pl.to_pickle('pl.pkl')
print(pl.notna().sum())
# check data ids vs mapping ids overlap
ids=set(df.striker_id)|set(df.bowler_id)
print(len(ids), len(ids&set(m.player_id)))
