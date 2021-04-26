import numpy as np
from matplotlib import pyplot as plt


class diverge_graph:
    """
    diverge graph object that provides a quick set of defaults to create beautiful diverging plots
    """

    def __init__(self, df, labels, val, xlabel=None, ylabel=None, TITLE=None, figsize=(5, 10), dpi=80, tfont=20,
                 lfont=12, linewidth=10, cmap='RdYlGn'):
        self.z_scores = self.__z_score__(self.values)
        self.labels = df[labels]
        if not xlabel:
            self.xlabel = labels
        else:
            self.xlabel = xlabel

        if not ylabel:
            self.ylabel = val
        else:
            self.ylabel = ylabel

        self.values = df[val].values
        self.figsize = figsize
        self.plt = plt
        self.tfont = tfont
        self.lfont = lfont
        self.dpi = dpi
        self.linewidth = linewidth
        if not TITLE:
            self.chart_title = f"Diverging graph: {self.xlabel} vs {self.ylabel}"
        else:
            self.chart_title = TITLE

    def __z_score__(self, val):
        return (val - val.mean()) / val.std()

    def __color__(self, __range):
        return ['C1' if val < 0 else 'C2' for val in __range]

    def plot(self):
        order = np.argsort(self.z_scores)
        self.z_scores.sort()
        self.values = [self.values[i] for i in order]
        self.labels = [self.labels[i] for i in order]

        self.plt.figure(figsize=self.figsize, dpi=self.dpi, facecolor='oldlace')
        self.plt.hlines(y=range(len(self.labels)),
                        xmin=0,
                        xmax=self.z_scores,
                        color=self.__color__(self.z_scores),
                        alpha=0.5,
                        linewidth=self.linewidth)
        self.plt.gca().set(ylabel=self.ylabel, xlabel=self.xlabel)
        self.plt.yticks(range(len(self.labels)), self.labels, fontsize=self.lfont)
        self.plt.title(self.chart_title, fontdict={'size': self.tfont, 'family': 'Tahoma'})
        self.plt.grid(linestyle='--', alpha=0.5)
        self.plt.show()
