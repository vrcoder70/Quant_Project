import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import seaborn as sns

class SMABackTest():
    def __init__(self, symbol, start, end, sma_s, sma_l):
        plt.style.use('ggplot')
        self.symbol = symbol
        self.start = start
        self.end = end
        self.sma_s = sma_s
        self.sma_l = sma_l
        self.stock = self.get_data()
        self.description = {
            'Returns' : self.stock['Returns Buy and Hold'].iloc[-1],
            'Strategy Return' : self.stock['Strategy Return'].iloc[-1],
            'Max Drowdown' : self.stock['Drowdown'].max(),
            'Max Drowdown Index' : self.stock['Drowdown'].idxmax(),
            'Max Drowdown PCT' : self.stock['Drowdown PCT'].max(),
            'Max Drowdown PCT Index' : self.stock['Drowdown PCT'].idxmax(),
        }

    def get_data(self):
        data = yf.download(tickers=self.symbol, start=self.start, end=self.end)

        data[f'SMA{self.sma_s}'] = data.Close.rolling(window=self.sma_s, min_periods=self.sma_s).mean()
        data[f'SMA{self.sma_l}'] = data.Close.rolling(window=self.sma_l, min_periods=self.sma_l).mean()

        data.dropna(inplace=True)
        data['Daily Returns'] = np.log(data.Close.div(data.Close.shift(1)))
        data.dropna(inplace=True)

        data['Returns Buy and Hold'] = data['Daily Returns'].cumsum().apply(np.exp)
        data['Cumulative Max'] = data['Returns Buy and Hold'].cummax()
        data['Drowdown'] = data['Returns Buy and Hold'] - data['Cumulative Max']
        data['Drowdown PCT'] = data['Drowdown'].div(data['Cumulative Max'])

        data['Position'] = np.where(data[f'SMA{self.sma_s}'] > data[f'SMA{self.sma_l}'], 1, -1)
        data['Strategy'] = data['Daily Returns'] * data['Position'].shift(1)
        data['Strategy Return'] = data['Strategy'].cumsum().apply(np.exp)
        

        return data

    def visualize_sma_data(self):
        self.stock[['Close',f'SMA{self.sma_s}', f'SMA{self.sma_l}']].plot(figsize=(12,10), fontsize=12)
        plt.legend(loc='upper left', fontsize=13)
        plt.title(label=f'{self.symbol} Price | SMA{self.sma_s} | SMA{self.sma_l}', fontsize=18)
        plt.xlabel(xlabel='Time Period', fontsize=13)
        plt.ylabel(ylabel='Price in Dollor', fontsize=13)
        plt.show()

    def visualize_returns(self):
        self.stock[['Cumulative Max', 'Returns Buy and Hold']].plot(figsize=(12,10), fontsize=12)
        plt.legend(loc='upper left', fontsize=13)
        plt.title(label=f'{self.symbol} Drowdowns', fontsize=18)
        plt.xlabel(xlabel='Time Period', fontsize=13)
        plt.ylabel(ylabel='Price in Dollor', fontsize=13)
        plt.show()

    def compare_strategy(self):        
        self.stock[['Strategy Return', 'Returns Buy and Hold']].plot(figsize=(12,10), fontsize=12)
        plt.legend(loc='upper left', fontsize=13)
        plt.title(label=f'{self.symbol} Buy and Hold vs Strategy Return', fontsize=18)
        plt.xlabel(xlabel='Time Period', fontsize=13)
        plt.ylabel(ylabel='Price in Dollor', fontsize=13)
        plt.show()