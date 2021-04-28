# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/data_datasets__m4.ipynb (unless otherwise specified).

__all__ = ['Yearly', 'Quarterly', 'Monthly', 'Weekly', 'Daily', 'Hourly', 'Other', 'M4Info', 'M4']

# Cell
import os

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from .utils import download_file, Info, TimeSeriesDataclass
from ..tsdataset import TimeSeriesDataset

# Cell
@dataclass
class Yearly:
    seasonality: int = 1
    horizon: int = 6
    freq: str = 'Y'
    name: str = 'Yearly'
    n_ts: int = 23_000

@dataclass
class Quarterly:
    seasonality: int = 4
    horizon: int = 8
    freq: str = 'Q'
    name: str = 'Quarterly'
    n_ts: int = 24_000

@dataclass
class Monthly:
    seasonality: int = 12
    horizon: int = 18
    freq: str = 'M'
    name: str = 'Monthly'
    n_ts: int = 48_000

@dataclass
class Weekly:
    seasonality: int = 52
    horizon: int = 13
    freq: str = 'W'
    name: str = 'Weekly'
    n_ts: int = 359

@dataclass
class Daily:
    seasonality: int = 7
    horizon: int = 14
    freq: str = 'D'
    name: str = 'Daily'
    n_ts: int = 4_227

@dataclass
class Hourly:
    seasonality: int = 24
    horizon: int = 48
    freq: str = 'H'
    name: str = 'Hourly'
    n_ts: int = 414


@dataclass
class Other:
    seasonality: int = 1
    horizon: int = 8
    freq: str = 'D'
    name: str = 'Other'
    n_ts: int = 5_000
    included_groups: Tuple = ('Weekly', 'Daily', 'Hourly')

# Cell
M4Info = Info(groups=('Yearly', 'Quarterly', 'Monthly', 'Weekly', 'Daily', 'Hourly', 'Other'),
              class_groups=(Yearly, Quarterly, Monthly, Weekly, Daily, Hourly, Other))

# Cell
@dataclass
class M4(TimeSeriesDataclass):

    source_url = 'https://raw.githubusercontent.com/Mcompetitions/M4-methods/master/Dataset/'

    @staticmethod
    def load(directory: str,
             group: str) -> Tuple[pd.DataFrame,
                                  Optional[pd.DataFrame],
                                  Optional[pd.DataFrame]]:
        """
        Downloads and loads M4 data.

        Parameters
        ----------
        directory: str
            Directory where data will be downloaded.
        group: str
            Group name.
            Allowed groups: 'Yearly', 'Quarterly', 'Monthly',
                            'Weekly', 'Daily', 'Hourly'.

        Notes
        -----
        [1] Returns train+test sets.
        """
        if group == 'Other':
            #Special case.
            included_dfs = [M4.load(directory, gr) \
                            for gr in M4Info['Other'].included_groups]
            df, *_ = zip(*included_dfs)
            df = pd.concat(df)
        else:

            M4.download(directory)
            path = f'{directory}/m4/datasets'
            class_group = M4Info[group]

            def read_and_melt(file):
                df = pd.read_csv(file)
                df.columns = ['unique_id'] + list(range(1, df.shape[1]))
                df = pd.melt(df, id_vars=['unique_id'], var_name='ds', value_name='y')
                df = df.dropna()

                return df

            df_train = read_and_melt(file=f'{path}/{group}-train.csv')
            df_test = read_and_melt(file=f'{path}/{group}-test.csv')

            len_train = df_train.groupby('unique_id').agg({'ds': 'max'}).reset_index()
            len_train.columns = ['unique_id', 'len_serie']
            df_test = df_test.merge(len_train, on=['unique_id'])
            df_test['ds'] = df_test['ds'] + df_test['len_serie']
            df_test.drop('len_serie', axis=1, inplace=True)

            df = pd.concat([df_train, df_test])
            df = df.sort_values(['unique_id', 'ds']).reset_index(drop=True)

        return df, None, None

    @staticmethod
    def download(directory: str) -> None:
        """Download M4 Dataset."""
        path = f'{directory}/m4/datasets/'
        if not os.path.exists(path):
            for group in M4Info.groups:
                download_file(path, f'{M4.source_url}/Train/{group}-train.csv')
                download_file(path, f'{M4.source_url}/Test/{group}-test.csv')
            download_file(path, f'{M4.source_url}/M4-info.csv')