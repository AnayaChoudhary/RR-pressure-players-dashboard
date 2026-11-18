import pandas as pd, numpy as np
pd.set_option('display.width',250,'display.max_columns',100)
df=pd.read_pickle('ball_wp.pkl')
df['PB']=((df.innings==2)&(df.LI>=1.5))|((df.innings==1)&(df.wkts_before>=3)&(df.overid<=10))
df['PW']=((df.innings==2)&(df.LI>=1.5))|(df.overid>=17)
bt=df[~df.is_wide].copy()
bt['dismissed']=bt.is_wicket&(bt.dismissed_player_id==bt.striker_id)
bt['exp']=bt.groupby(['innings','overid']).bat_runs.transform('mean')
bt['rae']=bt.bat_runs-bt.exp-6*bt.dismissed
bt['half']=np.where(bt.dt<pd.Timestamp('2024-07-01',tz='UTC'),'H1','H2')
bt['hit']=bt.is_four|bt.is_six
K=80
def agg(d,k=K):
    g=d.groupby('striker_id').agg(b=('rae','size'),r=('rae','sum'))
    g['v']=g.r/(g.b+k)*100
    return g
res=[]
H1=bt[bt.half=='H1']; H2=bt[bt.half=='H2']

tgt=agg(H2[H2.PB]); 
for lab,src in [('H1 pressure',H1[H1.PB]),('H1 non-pressure',H1[~H1.PB]),('H1 all',H1)]:
    s=agg(src)
    j=s.join(tgt,lsuffix='_s',rsuffix='_t',how='inner')
    j=j[(j.b_s>=60)&(j.b_t>=40)]
    print(lab,len(j),round(j.v_s.corr(j.v_t),3), round(j.v_s.corr(j.v_t,method='spearman'),3))
# blend
sp=agg(H1[H1.PB]); sn=agg(H1[~H1.PB])
j=sp.join(sn,lsuffix='_p',rsuffix='_n').join(tgt.rename(columns={'b':'b_t','r':'r_t','v':'v_t'}),how='inner')
j=j[(j.b_p+j.b_n>=80)&(j.b_t>=40)]
for w in [0,.25,.5,.75,1]:
    j['bl']=w*j.v_p+(1-w)*j.v_n
    print('w_pressure',w,len(j),round(j.bl.corr(j.v_t),3))
# SR-only / bnd metrics stability
def agg2(d,col):
    g=d.groupby('striker_id').agg(b=(col,'size'),x=(col,'mean'))
    return g
for col in ['hit','bat_runs']:
    a=agg2(H1[H1.PB],col); t=agg2(H2[H2.PB],col)
    j=a.join(t,lsuffix='_s',rsuffix='_t',how='inner'); j=j[(j.b_s>=60)&(j.b_t>=40)]
    print(col,len(j),round(j.x_s.corr(j.x_t),3))
a=H1.groupby('striker_id').agg(b=('hit','size'),x=('hit','mean')); 
j=a.join(agg2(H2[H2.PB],'hit'),lsuffix='_s',rsuffix='_t',how='inner'); j=j[(j.b_s>=60)&(j.b_t>=40)]
print('H1 all boundary% -> H2 pressure boundary%',len(j),round(j.x_s.corr(j.x_t),3))
