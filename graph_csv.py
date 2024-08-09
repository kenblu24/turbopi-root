import argparse
import pandas as pd
from matplotlib import pyplot as plt

class Graph():
    
    def graph(self, filename):
        plt.rcParams["figure.figsize"] = [7.00, 3.50]
        plt.rcParams["figure.autolayout"] = True
        
        df = pd.read_csv(filename)
        df.T.plot(kind='line')
        plt.legend(title='Variables', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.show()




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="csv file to be graphed")
    filename = parser.parse_args().filename
    # breakpoint()
    graph = Graph()
    graph.graph(filename)