import numpy as np
import pandas as pd
import math
import pathlib
from itertools import combinations


def import_data(data_dir, filter):
    l = []
    root = pathlib.Path().cwd().joinpath(data_dir)
    for tidx, tdir in enumerate([d for d in root.iterdir() if d.is_dir()]):
        l.append([])
        for iidx, idir in enumerate([d for d in tdir.iterdir() if d.is_dir()]):
            l[tidx].append([])
            for jdata in idir.glob(f"*.{filter}.json"):
                l[tidx][iidx].append(jdata)
    return l


def json_to_df(file_path):
    dfl = [pd.DataFrame(pd.read_json(j)) for j in file_path]
    for i, df in enumerate(dfl):
        df.drop("Type", axis=1, inplace=True)
        df.drop("SubType", axis=1, inplace=True)
        df.drop("Protocol", axis=1, inplace=True)
        dfl[i] = df
    if len(dfl) > 1:
        dfl = pd.concat(dfl)
    else:
        dfl = dfl[0]
    dfl.reset_index(inplace=True)
    dfl.drop("index", axis=1, inplace=True)
    dfl["Timestamp"] = dfl["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    dfl["Timestamp"] = pd.to_datetime(dfl["Timestamp"])
    return dfl


def build_dfs(dataset):
    l = []
    for i in range(len(dataset)):
        l.append([])
        for file_path in dataset[i]:
            l[i].append(json_to_df(file_path))
    return l


def clean_network_noise(dfmerge):
    for df1, df2 in combinations(dfmerge, 2):
        diff_by_key(df1, df2, "SendIP")
        diff_by_key(df1, df2, "RecvIP")


def diff_by_key(df1, df2, key):
    ip1 = set(df1[key])
    ip2 = set(df2[key])
    if ip1 != ip2:
        diff12 = ip1.difference(ip2)
        diff21 = ip2.difference(ip1)
        if len(diff12):
            delidx = []
            for el in diff12:
                delidx += list(df1[df1[key] == el].index)
            print(f"dataframe {id(df1)}, removed {len(delidx)} items, {delidx[:5]}")
            df1.drop(index=delidx, axis=0, inplace=True)
        if len(diff21):
            delidx = []
            for el in diff21:
                delidx += list(df2[df2[key] == el].index)
            print(f"dataframe {id(df2)}, removed {len(delidx)} items, {delidx[:5]}")
            df2.drop(index=delidx, axis=0, inplace=True)


def sort_by_key(dfmerge, key):
    for df in dfmerge:
        df.sort_values(key, inplace=True)


def cmp_elapsed(dfmerge):
    for df in dfmerge:
        df["Elapsed"] = pd.to_datetime(df.Timestamp - df.Timestamp.min(), unit="ns")
        df.Elapsed = df.Elapsed.dt.time


def clean_timedelta_outliers(dfmerge):
    for df in dfmerge:
        sendIPs = list(set(df["SendIP"]))

        for ip in sendIPs:
            q3 = df[df.SendIP == ip].TimeDelta.quantile(0.75)

            idx = list(df[(df.TimeDelta > q3) & (df.SendIP == ip)].index)
            df.drop(index=idx, axis=0, inplace=True)


def cmp_conf_interval(data, z_score=1.96):
    mean = np.mean(data)
    std = np.std(data)
    size = len(data)
    err = z_score * (std / np.sqrt(size))
    return (mean - err, mean + err)
