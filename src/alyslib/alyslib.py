import numpy as np
import pandas as pd
import math
import os


def import_netgen_datasets(data_base_path):
    # first level FS scan
    p = os.path.abspath(data_base_path)
    l1 = []
    for i in os.listdir(p):
        l1.append(os.path.join(p, i))

    # second level FS scan with collection of all the NETWORK GENERAL JSON data
    l2 = []
    for l in l1:
        r1 = []
        for e1 in os.listdir(l):
            if ".yml" not in e1:
                r2 = []
                c = os.path.join(l, e1)
                for e2 in os.listdir(c):
                    if "net.gen" in e2:
                        r2.append(os.path.join(c, e2))
                r1.append(r2)
        l2.append(r1)
    return l2


def build_df_from_json_files(f):
    df1 = [pd.DataFrame(pd.read_json(j)) for j in f]

    for i, df in enumerate(df1):
        df.drop("Type", axis=1, inplace=True)
        df.drop("SubType", axis=1, inplace=True)
        df.drop("Protocol", axis=1, inplace=True)

        df1[i] = df

    if len(df1) > 1:
        df1 = pd.concat(df1)
    else:
        df1 = df1[0]

    df1.reset_index(inplace=True)
    df1.drop("index", axis=1, inplace=True)
    df1["Timestamp"] = df1["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df1["Timestamp"] = pd.to_datetime(df1["Timestamp"])

    return df1


def cmpdiff(df1, df2, key):
    ip1 = set(df1[key])
    ip2 = set(df2[key])

    if ip1 != ip2:
        diff12 = ip1.difference(ip2)
        diff21 = ip2.difference(ip1)

        # df1
        if len(diff12):
            delidx = []
            for el in diff12:
                delidx += list(df1[df1[key] == el].index)
            print(
                "deleting %d items from function param (df1) - %s"
                % (len(delidx), delidx)
            )
            df1.drop(index=delidx, axis=0, inplace=True)
        print()

        # df2
        if len(diff21):
            delidx = []
            for el in diff21:
                delidx += list(df2[df2[key] == el].index)
            print(
                "deleting %d items from function param (df2) - %s"
                % (len(delidx), delidx)
            )
            df2.drop(index=delidx, axis=0, inplace=True)
        print()


def confidence_95_interval(data):
    mean = np.mean(data)
    std = np.std(data)
    z_score = 1.96
    size = len(data)

    err = z_score * (std / math.sqrt(size))

    return (mean - err, mean + err)
