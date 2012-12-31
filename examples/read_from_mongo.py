import monary
import time
import argparse
import numpy as np
import pandas as pd
from scipy import stats

def load_data(mon, db, collection, columns, selection={}):
    arrs = mon.query(db, collection, selection, columns,
            ['int64', ] * len(columns))
    df = np.matrix(arrs).transpose()
    df = pd.DataFrame(df, columns=columns)
    return df

def load_durations(mon):
    durations_columns = [
            'node',
            'true_start', 'start',
            'end', 'true_end'
    ]
    df = load_data(mon, 'stats', 'infections', durations_columns)
    df = df.set_index('node')
    df.index.name = 'node'
    df['duration'] = df.end - df.start
    return df

def load_evolution(mon):
    distributions_columns = [
        'current_time', 'real_time', 'susceptible',
        'infected', 'recovered']
    df = load_data(mon, 'stats', 'distributions',
            distributions_columns)
    df = df.set_index('current_time')
    df.index.name = 'step'
    df = df.drop([-1])
    return df

def lag_distribution(durations, expo=0.4):
    binned = np.bincount(durations.duration)
    normalized_binned = (binned.astype(float)
            / durations.duration.count())
    geom_dist = stats.geom(expo)
    expected_values = geom_dist.pmf(
            np.arange(len(normalized_binned)))
    df = pd.DataFrame(
            {'Duration frequency': normalized_binned,
             'Expected values': expected_values})
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-t', '--token',
            default=str(time.time()))
    parser.add_argument(
            '-e', '--expo',
            default=0.4,
            type=float)
    ns = parser.parse_args()

    mon = monary.Monary()

    durations = load_durations(mon)
    evolution = load_evolution(mon)
    durations_hist = lag_distribution(durations, ns.expo)

    durations.to_csv('durations-%s.csv' % ns.token)
    evolution.to_csv('evolution-%s.csv' % ns.token)
    durations_hist.to_csv('durations-hist-%s.csv' % ns.token)

    excel_file = pd.ExcelWriter('SIR-%s.xls' % ns.token)
    evolution.to_excel(excel_file, 'evolution')
    durations_hist.to_excel(excel_file, 'durations hist')
    excel_file.save()

