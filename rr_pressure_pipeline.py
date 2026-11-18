"""
RR pressure-player pipeline (SupeRR Selector S2, Round 1) - created by Anaya
Usage: python rr_pressure_pipeline.py --data /path/to/csvs --out outputs
Needs: pandas, numpy, scikit-learn
"""
import argparse, os
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold

K_BAT, K_BOWL = 60, 100                      # shrinkage (balls)
CUTOFF = pd.Timestamp('2025-06-01', tz='UTC')  # must be active since
LI_HIGH = 1.5                                  # leverage threshold for "live chase"

def z(s): return (s - s.mean()) / s.std()

# ---------- 1. ball features ----------
def load_balls(path):
    df = pd.read_csv(path)
    df['dt'] = pd.to_datetime(df.delivery_ist_time)
    df = df.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True)
    df = df[df.innings.isin([1, 2])].copy()
    df['is_wide'] = df.extras_type.eq('wide')
    df['is_nb'] = df.extras_type.isin(['Overstep', 'other'])
    df['legal'] = ~(df.is_wide | df.is_nb)
    df['team_runs'] = df.runs + df.extras1_runs + df.extras_2_runs
    charged = df.extras_type.isin(['wide', 'Overstep', 'other', 'Penalty'])
    df['bowl_runs'] = np.where(charged, df.team_runs, df.runs)
    df['wk'] = df.is_wicket & df.dismissal_type.isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])
    g = df.groupby(['match_id', 'innings'])
    df['cum_runs'] = g.team_runs.cumsum()
    df['cum_wkts'] = g.is_wicket.cumsum()
    df['cum_legal'] = g.legal.cumsum()
    df['runs_before'] = df.cum_runs - df.team_runs
    df['wkts_before'] = df.cum_wkts - df.is_wicket.astype(int)
    df['legal_before'] = df.cum_legal - df.legal.astype(int)
    df['inn1_total'] = df.match_id.map(df[df.innings == 1].groupby('match_id').team_runs.sum())
    df['target'] = df.inn1_total + 1
    df['phase'] = pd.cut(df.overid, [0, 6, 15, 20], labels=['PP', 'Middle', 'Death'])
    return df

def complete_matches(df):
    g = df.groupby(['match_id', 'innings']).agg(legal=('legal', 'sum'), w=('is_wicket', 'sum'),
                                                runs=('team_runs', 'sum')).unstack()
    g.columns = [f'{a}{b}' for a, b in g.columns]
    c1 = (g.legal1 >= 119) | (g.w1 >= 10)
    win = g.runs2 >= g.runs1 + 1
    c2 = win | (g.legal2 >= 119) | (g.w2 >= 10)
    return g[c1 & c2].index, win

# ---------- 2. win probability + leverage ----------
def feats(d, after):
    r, l, w = (d.cum_runs, d.cum_legal, d.cum_wkts) if after else (d.runs_before, d.legal_before, d.wkts_before)
    X = pd.DataFrame({'inn': d.innings.values, 'balls_left': (120 - l).values, 'runs': r.values, 'wkts': w.values})
    ch = d.innings.values == 2
    X['need'] = np.where(ch, (d.target - r).values, np.nan)
    X['rrr'] = np.where(ch, X.need / np.clip(X.balls_left, 1, None) * 6, np.nan)
    X['crr'] = X.runs / np.clip(120 - X.balls_left, 1, None) * 6
    return X

def add_leverage(df):
    ok, chase_win = complete_matches(df)
    df = df[df.match_id.isin(ok)].copy()
    df['bat_win'] = np.where(df.innings == 2, df.match_id.map(chase_win), 1 - df.match_id.map(chase_win)).astype(int)
    Xa, Xb, y = feats(df, True), feats(df, False), df.bat_win.values
    pa, pb = np.zeros(len(df)), np.zeros(len(df))
    for tr, te in GroupKFold(5).split(Xa, y, df.match_id.values):      # cross-fit by match: no leakage
        m = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.06, max_iter=250,
                                           min_samples_leaf=200, l2_regularization=1.0).fit(Xa.iloc[tr], y[tr])
        pa[te], pb[te] = m.predict_proba(Xa.iloc[te])[:, 1], m.predict_proba(Xb.iloc[te])[:, 1]
    df['wp_after'], df['wp_before'] = pa, pb
    last = df.groupby(['match_id', 'innings']).innings_ball_num.transform('max') == df.innings_ball_num
    end = ((df.innings == 2) & last) | ((df.innings == 2) & (df.cum_runs >= df.target))
    df.loc[end, 'wp_after'] = df.loc[end, 'bat_win'].astype(float)
    prev = df.groupby(['match_id', 'innings']).wp_after.shift(1)
    df['wp_before'] = prev.fillna(df.wp_before)
    df['wpa'] = df.wp_after - df.wp_before
    df['wpbin'] = pd.cut(df.wp_before, np.linspace(0, 1, 11), include_lowest=True)
    lev = df.groupby(['innings', 'overid', 'wpbin'], observed=True).wpa.transform(lambda s: s.abs().mean())
    df['LI'] = lev / df.wpa.abs().mean()                                # leverage index (1 = average ball)
    return df

# ---------- 3. pressure flags ----------
def flag_pressure(df, ipl_ids):
    df['ipl'] = df.match_id.isin(ipl_ids)
    live = (df.innings == 2) & (df.LI >= LI_HIGH)
    rebuild = (df.innings == 1) & (df.wkts_before >= 3) & (df.overid <= 10)
    df['PB'] = live | rebuild                    # batter pressure
    df['PW'] = live | (df.overid >= 17)          # bowler pressure (live chase or death)
    return df

# ---------- 4. batters ----------
def rate_batters(df):
    b = df[~df.is_wide].copy()
    b['out'] = b.is_wicket & (b.dismissed_player_id == b.striker_id)
    b['exp'] = b.groupby(['ipl', 'innings', 'overid']).runs.transform('mean')   # IPL vs T20I baseline
    b['rae'] = b.runs - b.exp
    b['bnd'] = b.is_four | b.is_six
    b['dotb'] = b.runs == 0
    P = b[b.PB]
    g = P.groupby('striker_id').agg(name=('striker_name', 'first'), b=('rae', 'size'), runs=('runs', 'sum'),
        outs=('out', 'sum'), bnd=('bnd', 'sum'), dots=('dotb', 'sum'), rae=('rae', 'sum'), wpa=('wpa', 'sum'),
        inns=('match_id', 'nunique'))
    g['last'] = df.groupby('striker_id').dt.max()
    sh = lambda c: (g[c] + K_BAT * g[c].sum() / g.b.sum()) / (g.b + K_BAT) * 100
    g['sr'], g['bnd_s'], g['out_s'], g['dot_s'] = g.runs / g.b * 100, sh('bnd'), sh('outs'), sh('dots')
    g['rae_s'] = g.rae / (g.b + K_BAT) * 100
    g['wpa100'] = g.wpa / (g.b + 80) * 10000
    q = g[(g.b >= 100) & (g['last'] >= CUTOFF)].copy()
    q['score'] = (0.28 * z(q.bnd_s) + 0.22 * z(q.rae_s) - 0.20 * z(q.out_s) - 0.10 * z(q.dot_s)
                  + 0.10 * z(q.wpa100) + 0.10 * z(q.inns.clip(upper=30)))
    return q.sort_values('score', ascending=False)

# ---------- 5. bowlers ----------
def rate_bowlers(df):
    w = df.copy()
    w['dotb'] = (w.bowl_runs == 0) & w.legal
    w['bc'] = w.is_four | w.is_six
    P = w[w.PW]
    g = P.groupby('bowler_id').agg(name=('bowler_name', 'first'), d=('legal', 'size'), b=('legal', 'sum'),
        runs=('bowl_runs', 'sum'), wk=('wk', 'sum'), dots=('dotb', 'sum'), bc=('bc', 'sum'), wpa=('wpa', 'sum'),
        spells=('match_id', 'nunique'))
    g['last'] = df.groupby('bowler_id').dt.max()
    sh = lambda c, n: (g[c] + K_BOWL * g[c].sum() / g[n].sum()) / (g[n] + K_BOWL)
    g['econ_s'] = sh('runs', 'b') * 6
    g['wk_s'], g['dot_s'], g['bc_s'] = sh('wk', 'b') * 24, sh('dots', 'd') * 100, sh('bc', 'd') * 100
    g['wpa100'] = -g.wpa / (g.d + 80) * 10000
    q = g[(g.d >= 150) & (g.spells >= 10) & (g['last'] >= CUTOFF)].copy()
    q['score'] = (-0.30 * z(q.econ_s) + 0.25 * z(q.wk_s) + 0.15 * z(q.dot_s) - 0.15 * z(q.bc_s)
                  + 0.10 * z(q.wpa100) + 0.05 * z(q.spells.clip(upper=30)))
    return q.sort_values('score', ascending=False)

# ---------- 6. validation: does pressure form repeat? ----------
def split_half(df, split='2024-07-01'):
    b = df[~df.is_wide & df.PB].copy()
    b['exp'] = b.groupby(['ipl', 'innings', 'overid']).runs.transform('mean')
    b['bnd'] = (b.is_four | b.is_six).astype(float)
    b['rpb'] = b.runs
    b['half'] = np.where(b.dt < pd.Timestamp(split, tz='UTC'), 'H1', 'H2')
    out = {}
    for col in ['bnd', 'rpb', 'wpa']:
        a = b[b.half == 'H1'].groupby('striker_id')[col].agg(['mean', 'size'])
        t = b[b.half == 'H2'].groupby('striker_id')[col].agg(['mean', 'size'])
        j = a.join(t, lsuffix='_1', rsuffix='_2', how='inner')
        j = j[(j.size_1 >= 60) & (j.size_2 >= 40)]
        out[col] = round(j.mean_1.corr(j.mean_2), 3)
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data', default='.'); ap.add_argument('--out', default='outputs')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    P = lambda f: os.path.join(a.data, f)
    matches, comps = pd.read_csv(P('matches.csv')), pd.read_csv(P('competitions.csv'))
    m = matches.merge(comps[['comp_id', 'comp_name']], on='comp_id')
    ipl_ids = set(m[m.comp_name.str.startswith('IPL', na=False)].match_id)
    df = add_leverage(load_balls(P('ball_by_ball.csv')))
    df = flag_pressure(df, ipl_ids)
    print('pressure share of balls:', round(df.PB.mean(), 3), '| repeatability (r):', split_half(df))
    bat, bowl = rate_batters(df), rate_bowlers(df)
    bat.to_csv(os.path.join(a.out, 'batters_ranked.csv')); bowl.to_csv(os.path.join(a.out, 'bowlers_ranked.csv'))
    print(bat[['name', 'b', 'sr', 'bnd_s', 'out_s', 'score']].head(10).round(2))
    print(bowl[['name', 'b', 'econ_s', 'wk_s', 'dot_s', 'score']].head(10).round(2))
    # Availability filter (optional): drop players in retained.txt (one name per line), then re-read the CSVs.
