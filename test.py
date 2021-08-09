
#================================================================================
#this one below works!
#================================================================================
@app.route("/test")
def test():
    #here we will do some testing
    # define time frame
    start = dt.datetime(2021,1,1)
    end = dt.datetime.now()

    # load data 
    ticker = "FUBO"
    stockData = web.DataReader(ticker, 'yahoo', start, end)

        #restructure data
    stockData = stockData[['Open', 'High', 'Low', 'Close']]

    stockData.reset_index(inplace=True)
    stockData['Date'] = stockData['Date'].map(mdates.date2num)

    # Generate the figure **without using pyplot**.
    fig = Figure()
    axx = fig.subplots()
    #axx = plt.subplot()

    axx.grid(True)
    axx.set_axisbelow(True)
        # ax.set_title("Chart Name", color='black')
    axx.set_facecolor('#cff5f5')
    axx.figure.set_facecolor('#121212')
    axx.tick_params(axis='both', which='both', colors='green')
    axx.xaxis_date()

    candlestick_ohlc(axx, stockData.values, width=.7, colorup='g')
    #ax.plot(chartFig)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    datax = base64.b64encode(buf.getbuffer()).decode("ascii")
    imgSrc = f"data:image/png;base64,{datax}"
    return render_template("test.html", imgSrc=imgSrc)

#================================================================================
#this one also works
#=================================================================================
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
#=================================================================================