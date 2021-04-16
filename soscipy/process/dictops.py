def sort_dict(dictionary):
    """
    Takes a dictionary as an input and sorts the dictionary
    :param dictionary: a key value pair dictionary
    :return: a sorted dictionar
    """
    return dict(sorted(dictionary.items(), key=lambda item: item[1]))


def invert_dict(dictionary):
    """
    Takes a dictionary as input and reverse the key value pair
    :param dictionary: a key value pair dictionary
    :return: a sorted dictionary
    """
    return {v: k for k, v in dictionary.items()}