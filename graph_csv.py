import argparse
import pandas as pd
from matplotlib import pyplot as plt

class Graph():
    
    def graph(self, filename):
        plt.rcParams["figure.figsize"] = [7.00, 3.50]
        plt.rcParams["figure.autolayout"] = True
        columns = ["Name", "Marks"]
        df = pd.read_csv(filename, usecols=columns)
        print("Contents in csv file:", df)
        plt.plot(df.Name, df.Marks)
        plt.show()




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="csv file to be graphed")
    filename = parser.parse_args().filename
    breakpoint()
    graph = Graph(filename)
    graph.graph()