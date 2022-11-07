# D:
# cd Others
# cd "[20221106] Streamlit Demo"
# streamlit run Main.py
# https://docs.streamlit.io/

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import date
from plotly import graph_objects as go
from plotly.subplots import make_subplots


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

def plot_raw_data(stock_data):
    stock_candle = go.Candlestick(
        x=stock_data["日期"],
        open=stock_data["開盤價"],
        high=stock_data["最高價"],
        low=stock_data["最低價"],
        close=stock_data["收盤價"],
        increasing_line_color="red",
        decreasing_line_color="green",
        name="K線"
    )
    volume_bar = go.Bar(x=data["日期"], y=data["成交股數"], name="成交股數")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(
        stock_candle,
        row=1, col=1
    )
    fig.add_trace(
        volume_bar,
        row=2, col=1
    )
    fig.layout.update(
        xaxis_rangeslider_visible = False,
    )
    fig.update_xaxes(title_text="日期")
    fig.update_yaxes(title_text="股價", row=1, col=1)
    fig.update_yaxes(title_text="成交股數", row=2, col=1)
    st.plotly_chart(fig)

def rename_describe(stock_data):
    return stock_data.rename({
        "count": "總筆數",
        "mean": "平均值",
        "std": "標準差",
        "mean": "平均值",
        "min": "最小值",
        "25%": "第1四分位數",
        "50%": "中位數",
        "75%": "第3四分位數",
        "max": "最大值",
    }, axis=0)

def reform_number_format(stock_data):
    for x in stock_data.columns:
        stock_data[x] = stock_data[x].map(lambda x: f"{x:,.0f}")
    return stock_data


# 參數設定
TODAY_val = date.today()
TODAY_str = TODAY_val.strftime("%Y-%m-%d")
START_str = "2019-1-1"

# 版面設定
st.title("股市資訊")


# 資料取得

labeled_stock = st.text_input("輸入股票代號", value="0050")
data_load_state = st.text(f"讀取檔案: {labeled_stock}")
try:
    data = load_data(f"{labeled_stock}.tw")
    status = True
except:
    data_load_state = st.text("查詢失敗")
    status = False
    

if status:
    if data.empty:
        data_load_state = st.text("查無此代碼")
    else:
        data_load_state = st.text("讀取完成...")

    if not data.empty:
        # 資料呈現
        st.title("股價資訊")
        st.subheader("最前5筆資料")
        st.write(data.head())
        st.subheader("最後5筆資料")
        st.write(data.tail())
        st.subheader("資料摘要")
        st.write(reform_number_format(rename_describe(data.describe())))
        

        # 資料繪圖
        st.title("股價K線")
        plot_raw_data(data)

        # 完整資料呈現
        st.subheader(f"完整資料: {START_str} 至 {TODAY_str}")
        st.write(data)


