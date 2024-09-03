from skimage import segmentation, color
from skimage import graph
import numpy as np
import networkx as nx

class Graph:
    
    @staticmethod
    def __mincut_relabel(graph, thresh): #Recursively cuts the graph using the Stoer-Wagner algorithm and asssigns new labels
        if len(graph)<2:
            Graph.__label_all(graph, 'mincut label')
            return
        leastcut, partns = nx.stoer_wagner(graph)
        if leastcut<thresh:
            sub1 = graph.subgraph(partns[0])
            sub2 = graph.subgraph(partns[1])
            Graph.__mincut_relabel(sub1, thresh)
            Graph.__mincut_relabel(sub2, thresh)
            return
        Graph.__label_all('mincut label')

    @staticmethod
    def __label_all(graph, attr_name):
        """Assign a unique integer to the given attribute in the RAG.
        This function assumes that all labels in `rag` are unique. It
        picks up a random label from them and assigns it to the `attr_name`
        attribute of all the nodes.
        rag : RAG
            The Region Adjacency Graph.
        attr_name : string
            The attribute to which a unique integer is assigned.
        """
        node = min(graph.nodes())
        new_label = graph.nodes[node]['labels'][0]
        for n, d in graph.nodes(data=True):
            d[attr_name] = new_label

    def __init__(self, img, n_segments, compactness):
        self.Img = img
        self.Initlabels = segmentation.slic(img, compactness=compactness, n_segments=n_segments, start_label=1)
        self.Graph = graph.rag_mean_color(img, self.Initlabels, mode='similarity')

    def mincut_segment(self, thresh): #Classic Minimum Cut
        Graph.__mincut_relabel(self.Graph, thresh)
        map_array = np.zeros(self.Initlabels.max() + 1, dtype=self.Initlabels.dtype)
        # Mapping from old labels to new
        for n, d in self.Graph.nodes(data=True):
            map_array[d['labels']] = d['mincut label']

        return map_array[self.Initlabels]
    
    def ncut_segment(self, thresh):#Normalized Cut (see Shi, J.; Malik, J., "Normalized cuts and image segmentation")
        return graph.cut_normalized(self.Initlabels, self.Graph, thresh)
    
    def paint(self, nodes):
        return color.label2rgb(nodes, self.Img, kind='avg', bg_label=0)
