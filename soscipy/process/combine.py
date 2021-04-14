import re

import numpy as np
import pandas as pd
import sparse_dot_topn.sparse_dot_topn as ct
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def combine(df1, df2):
    assert type(df1) == pd.core.frame.DataFrame, 'Input must be a pandas dataframe'
    assert type(df2) == pd.core.frame.DataFrame, 'Input must be a pandas dataframe'


class string_matcher():
    def __init__(self, list1, list2, top_n=10, similarity=0.8):
        self.list1 = list1
        self.list2 = list2
        self.names = list1.append(list2)
        self.names = self.names.values
        self.top_n = top_n
        self.similarity = similarity

    def ngrams(self, string, n=3):
        string = re.sub(r'[,-./]|\sBD', r'', string)
        ngrams = zip(*[string[i:] for i in range(n)])
        return [''.join(ngram) for ngram in ngrams]

    def awesome_cossim_top(A, B, ntop, lower_bound=0):
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

    def get_matches_df(sparse_matrix, name_vector, top=100):
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
        vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
        tf_idf_matrix = vectorizer.fit_transform(self.names)
        matches = awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), self.top_n, self.similarity)
        matches_df = get_matches_df(matches, self.names, top=len(names))
        return matches_df
