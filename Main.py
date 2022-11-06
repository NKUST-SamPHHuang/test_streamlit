# streamlit run Main.py

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import date, timedelta
from plotly import graph_objects as go



# @st.cache
def load_data(ticker):
    data = yf.download(ticker, START_str, TODAY_str)
    data.reset_index(inplace=True)
    data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d").astype(str)
    data.rename({
        "Date": "日期",
        "Open": "開盤價",
        "High": "最高價",
        "Low": "最低價",
        "Close": "收盤價",
        "Adj Close": "收盤價(修正後)",
        "Volume": "成交股數"
    }, axis=1, inplace=True)
    return data

def get_ticker(ticker):
    return ticker.split("(")[1].split(")")[0]

def plot_raw_data(stock_data):
    stock_candle = go.Candlestick(
        x=stock_data["日期"],
        open=stock_data["開盤價"],
        high=stock_data["最高價"],
        low=stock_data["最低價"],
        close=stock_data["收盤價"],
        increasing_line_color="red",
        decreasing_line_color="green"
    )
    fig = go.Figure(data=stock_candle)
    fig.layout.update(
        title_text = f"{selected_stock}",
        xaxis_rangeslider_visible = False,
    )
    st.plotly_chart(fig)



# 參數設定
TODAY_val = date.today()
TODAY_str = TODAY_val.strftime("%Y-%m-%d")
# year = 4
# START_val = TODAY_val - timedelta(year * 365)
# START_str = START_val.strftime("%Y-%m-%d")
START_str = "2019-1-1"

# 版面設定
st.title("股市資訊")

labeled_stock = st.text_input("輸入股票代號", value="2330")
stocks = ("台積電 (2330)", "國泰金 (2882)", "台灣五十 (0050)", "國泰永續高股息 (00878)")
selected_stock = st.selectbox("選取股票", stocks)




try:
    data = load_data(f"{labeled_stock}.tw")
except:
    pass

if data.empty:
    data_load_state = st.text(f"讀取檔案: {selected_stock}")
    data = load_data(f"{get_ticker(selected_stock)}.tw")
else:
    data_load_state = st.text(f"讀取檔案: {labeled_stock}")

data_load_state = st.text("讀取完成...")




st.title("股價資訊")
st.write(data.head())
st.write(data.tail())

st.title("股價K線")
plot_raw_data(data)

