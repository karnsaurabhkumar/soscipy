import re

import numpy as np
import pandas as pd

import sparse_dot_topn.sparse_dot_topn as ct
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def matrix_max_val_loc(mat):
    return np.unravel_index(np.argmax(mat, axis=None), mat.shape)


def intersection_count(l1, l2):
    return set(l1).intersection(set(l2))


def prim_key_candidate(dataframe):
    val = {}
    for i, c in enumerate(dataframe):
        val[i] = len(dataframe[c].unique())
    temp = sort_dict(val)
    temp = list(temp.keys())[-3:]
    temp.sort()
    return temp


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


def get_primary_keys(df1, df2):
    candidates = np.zeros((3, 3))
    temp1 = prim_key_candidate(df1)
    temp2 = prim_key_candidate(df2)
    for i in range(len(temp1)):
        for j in range(len(temp2)):
            l1 = df2[df2.columns[temp1[i]]].values
            l2 = df1[df1.columns[temp2[j]]].values
            candidates[i][j] = len(intersection_count(l1, l2))
    if candidates.max() <= 0:
        return -1, -1
    else:
        return matrix_max_val_loc(candidates)


def combine(df1, df2, outer=True):
    """
    Combines two dataframe after identifying its primary key
    :param df1: Dataframe1
    :param df2: Dataframe2
    :param outer: bool, if set True will return outer join of the dataset
    :return: a joint dataframe
    """
    left_on, right_on = get_primary_keys(df1, df2)
    list1 = list(df1[df1.columns[left_on]])
    list2 = list(df2[df2.columns[right_on]])
    primary_key_joins = string_matcher(list1, list2)
    matched_list = primary_key_joins.get_matched_list()
    matched_list = matched_list[matched_list.similairity < 0.99]
    df2[df2.columns[right_on]] = df2[df2.columns[right_on]].apply(lambda x: lookup(x, matched_list))
    if outer:
        temp = pd.merge(df1, df2, left_on=df1.columns[left_on], right_on=df2.columns[right_on], how='outer')
    else:
        temp = pd.merge(df1, df2, left_on=df1.columns[left_on], right_on=df2.columns[right_on])
        temp = temp.drop([df2.columns[right_on]], axis=1)
    return temp


def lookup(string, matches_df):
    """
    Lookup function to identify the similar name from the matched list
    :param string: Input string for the left side dataframe
    :param matches_df: Matched string table
    :return: output string
    """
    val = matches_df[matches_df['left_side'] == string]['right_side']
    if len(val) > 0:
        return val.values[0]
    else:
        return string


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
    assert all(elem in data.columns for elem in col_name)
    columns = {}
    for loc, col in enumerate(col_name):
        columns[col] = new_col_name[loc]
    data = data.rename(columns=columns)
    assert isinstance(data, object)
    return data


class string_matcher():
    def __init__(self, list1, list2, top_n=10, similarity=0.8):
        self.list1 = list1
        self.list2 = list2
        self.names = self.list1 + self.list2
        self.top_n = top_n
        self.similarity = similarity

    def ngrams(self, string, n=3):
        string = re.sub(r'[,-./]|\sBD', r'', string)
        ngrams = zip(*[string[i:] for i in range(n)])
        return [''.join(ngram) for ngram in ngrams]

    def awesome_cossim_top(self, A, B, ntop, lower_bound=0):
        # force A and B as a CSR matrix.
        # If they have already been CSR, there is no overhead
        A = A.tocsr()
        B = B.tocsr()
        M, _ = A.shape
        _, N = B.shape

        idx_dtype = np.int32

        nnz_max = M * ntop

        indptr = np.zeros(M + 1, dtype=idx_dtype)
        indices = np.zeros(nnz_max, dtype=idx_dtype)
        data = np.zeros(nnz_max, dtype=A.dtype)

        ct.sparse_dot_topn(
            M, N, np.asarray(A.indptr, dtype=idx_dtype),
            np.asarray(A.indices, dtype=idx_dtype),
            A.data,
            np.asarray(B.indptr, dtype=idx_dtype),
            np.asarray(B.indices, dtype=idx_dtype),
            B.data,
            ntop,
            lower_bound,
            indptr, indices, data)

        return csr_matrix((data, indices, indptr), shape=(M, N))

    def get_matches_df(self, sparse_matrix, name_vector, top=100):
        non_zeros = sparse_matrix.nonzero()
        sparserows = non_zeros[0]
        sparsecols = non_zeros[1]

        if top:
            nr_matches = top
        else:
            nr_matches = sparsecols.size

        left_side = np.empty([nr_matches], dtype=object)
        right_side = np.empty([nr_matches], dtype=object)
        similairity = np.zeros(nr_matches)

        for index in range(0, nr_matches):
            left_side[index] = name_vector[sparserows[index]]
            right_side[index] = name_vector[sparsecols[index]]
            similairity[index] = sparse_matrix.data[index]

        return pd.DataFrame({'left_side': left_side,
                             'right_side': right_side,
                             'similairity': similairity})

    def get_matched_list(self):
        vectorizer = TfidfVectorizer(min_df=1, analyzer=self.ngrams)
        tf_idf_matrix = vectorizer.fit_transform(self.names)
        matches = self.awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), self.top_n, self.similarity)
        matches_df = self.get_matches_df(matches, self.names, top=len(self.names))
        return matches_df

