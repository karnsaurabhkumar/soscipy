import seaborn as sns


def lrmd(x, y):
    """
    Linear regression with marginal distribution
    :param x:
    :param y:
    :return:
    """
    sns.set_theme(style="darkgrid")
    tips = sns.load_dataset("tips")
    g = sns.jointplot(x=x, y=y, data=tips,
                      kind="reg", truncate=False,
                      xlim=(x.min(), x.max()), ylim=(y.min(), y.max()),
                      color="m", height=7)


def heatmap(df, independent_variable, swap_axis=False):
    """
    Takes a 3 column dataframe as input with two dependent variable and one independent variable
    :param df: A pandas dataframe
    :param independent_variable: variable with numeric value
    :param swap_axis: bool, set to False. If turned true, will swap the x and y axis
    :return: returns a seaborn heatmap
    """
    cols = list(df.columns)
    cols.remove(independent_variable)
    if swap_axis:
        temp = df.pivot(cols[0], cols[1], independent_variable)
    else:
        temp = df.pivot(cols[1], cols[0], independent_variable)
    return sns.heatmap(temp, annot=True, fmt="d", linewidths=.5)
