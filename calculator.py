import pandas as pd 
import numpy as np

class Calculator:
    def __init__(self):
        pass

    def calculate_weight(self, dnc_i, DN_count):
        """
        Calculate the weight w_i for each file
        if dnc_i >= DN_count * 3/4, then w_i = 4,
        else if dnc_i >= DN_count * 1/2, then w_i = 3,
        else if dnc_i >= DN_count * 1/4, then w_i = 2,
        else w_i = 1
        """
        if dnc_i >= DN_count * 0.75:
            return 4
        elif dnc_i >= DN_count * 0.5:
            return 3
        elif dnc_i >= DN_count * 0.25:
            return 2
        else:
            return 1
        

    def calculate_popularity_degree(self, ac_i, dnc_i, w_i, crf_i):
        """
         (PD_i) of each file
        PD_i = (ac_i * dnc_i * w_i) / crf_i
        """
        if crf_i == 0:
            crf_i = 1
        return (ac_i * dnc_i * w_i) / crf_i  
    

    def calculate_threshold(self, file_metrics, DN_count):
        """
        Calculate the threshold,
        T = (1/n * sum(PD_i)) / DN_count
        """
        n = len(file_metrics)
        sum_PD = file_metrics['PD_i'].sum()
        mean_PD = sum_PD / n
        T = mean_PD / DN_count
        return T