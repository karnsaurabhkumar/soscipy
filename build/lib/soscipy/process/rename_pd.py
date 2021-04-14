def rename_pd(data, col_name, new_col_name):

    """
    Function to return renamed columns for a pandas dataframe
    :param data: Dataframe as input
    :param col_name: List of column names that needs to be renamed
    :param new_col_name:
    :return:
    """
    assert type(col_name) == list, 'Column names must be a list of strings'
    assert type(new_col_name) == list, 'New column names must be a list of strings'
    assert len(col_name) == len(new_col_name), 'Length of column names and new names must be equal'
    assert all(elem in col_name for elem in data.columns)
    columns = {}
    for loc, col in enumerate(col_name):
        columns[col] = new_col_name[loc]
    data = data.rename(columns=columns)
    return data