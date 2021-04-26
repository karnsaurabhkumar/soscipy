import world_bank_data as wb
from soscipy.process import dfops


def world_bank_data(url, date):
    """
    Takes a URL for input and extracts the indicator string. This is then used to extract data from world bank data
    :param url: URL of the data page
    :return: Dataframe with indicator as the last column
    """
    indicator = url.split('?')[0].split('/')[-1]
    data = wb.get_series(indicator, date=date, mrv=1).to_frame().reset_index()
    series = data['Series'].unique()[0]
    data = data.drop(['Series'], axis=1)
    data = dfops.rename_pd(data, [data.columns[-1]], [series])
    return data
