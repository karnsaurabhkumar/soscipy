import pandas as pd


def dat2csv(f_path, data):
    import os
    if not os.path.isfile(f_path):
        pd.DataFrame().to_csv(f_path)
    assert os.path.isfile(f_path), 'Please enter a valid file name'
    assert type(data) == pd.core.frame.DataFrame, 'Only dataframes are allowed'
    data.to_csv(f_path, mode='a', header=False, index=False)
    return 1

