@app.route("/hello")
def hello():
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


    #=======================================================
# define time frame
start = dt.datetime(2021,1,1)
end = dt.datetime.now()

    # load data 
ticker = "AMD"
stockData = web.DataReader(ticker, 'yahoo', start, end)

    #restructure data
stockData = stockData[['Open', 'High', 'Low', 'Close']]

stockData.reset_index(inplace=True)
stockData['Date'] = stockData['Date'].map(mdates.date2num)

# Generate the figure **without using pyplot**.
fig = Figure()
ax = fig.subplots

ax.grid(False)
ax.set_axisbelow(True)
    # ax.set_title("Chart Name", color='black')
ax.set_facecolor('#cff5f5')
ax.figure.set_facecolor('#121212')
ax.tick_params(axis='both', which='both', colors='green')
ax.xaxis_date()

candlestick_ohlc(ax, data.values, width=0.5, colorup='g')


# Save it to a temporary buffer.
buf = BytesIO()
fig.savefig(buf, format="png")
# Embed the result in the html output.
data = base64.b64encode(buf.getbuffer()).decode("ascii")
return f"<img src='data:image/png;base64,{data}'/>"