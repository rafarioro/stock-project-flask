from flask import Flask, request, render_template, url_for, redirect, flash, session
from requests.sessions import default_headers
from models import db, connect_db, User, Watchlist
import requests
import operator
import datetime as dt
from io import BytesIO
import base64
import pandas_datareader as web
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
from charts import chartFunc
from forms import UserForm, UserLogin, WatchlistForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///website' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "secretKey"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
#===========================================================
@app.route("/", methods=['GET', 'POST'])
def homeApp():
    return render_template("index.html") 
#===========================================================
#===========================================================
@app.route("/register", methods=['GET', 'POST'])
def user_register():
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        new_user = User.register(name, email, password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.email.errors.append('Email taken, please use another')
            return render_template('register.html', form=form)
        session['email'] = new_user.email
        return redirect("/")

    return render_template("register.html", form=form)
#===========================================================
#===========================================================
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = UserLogin()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        userLogin = User.authenticate(email, password)
    
        if userLogin:
            flash("Welcome") #"""{loginUser.email?}"""
            session['email'] = userLogin.email
            return redirect("/")
        else:
            form.email.errors = ['Invalid Credentials']
      
    return render_template('login.html', form=form)
    #userUserName =  User.query.filter_by(name=userName).first().name
    #return render_template("users.html", userUserName=userUserName) 
#============================================================
#============================================================
@app.route('/logout')
def logout_user():
    session.pop('email')
    flash("You've logged out")
    return redirect('/')
#============================================================
#============================================================
@app.route('/watchlist-delete/<int:id>', methods=["POST"])
def watchlist_del(id):
    """Delete Tickers from watchlist"""
    tickertoDelete = Watchlist.query.get_or_404(id)
    if tickertoDelete.email_id == session['email']:
        db.session.delete(tickertoDelete)
        db.session.commit()
        flash('Ticker deleted')
        return redirect('/watchlist-test')
    
    return redirect('/watchlist-test')
#============================================================
#============================================================
@app.route("/watchlist-test", methods=['GET', 'POST'])
def watchlist():
    form = WatchlistForm()
    if "email" not in session:
        flash("Please login to add watchlist data")
        return redirect('/')

    #get tickers from watchlist table
    testTickers = Watchlist.query.with_entities(Watchlist.ticker).filter(Watchlist.email_id == session['email']).all()
    #added this in order to access the TICKER id in the watchlist, in order to delete individual tickers, i needed to access the ticker db id.
    allTickers = Watchlist.query.filter(Watchlist.email_id == session['email']).all()
    #check if the logged in user has a watchlist setup. I couldnt fix an empty table with a new user. So I started them all with the SPY watlist ticker
    if len(testTickers) == 0:
        flash('watchlist is empty')
        newWatchlistTicker = Watchlist(ticker="SPY", email_id=session['email'])
            
        db.session.add(newWatchlistTicker)
        db.session.commit()
        return redirect('/watchlist-test')

    strippedTickers = [x[0] for x in testTickers] # https://stackoverflow.com/questions/49207257/remove-brackets-from-selected-row-sqlalchemy

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"

    #becuase i couldnt plug in a list directly to the querystring, I needed to remove brackets and quotes
    def listStripper(list): #https://www.codeleaks.io/print-list-without-brackets-and-quotes-in-python/
        separator = ", "
        return separator.join(list)

    #pass in the ticker list into the function, then pass that return variable into querystring
    strippedList = listStripper(strippedTickers)

    querystring = {"region":"US","symbols":f"{strippedList}"} #figure out how to get from list
    headers = {
        'x-rapidapi-key': "3b0e1aa5d4msh7224630a28298fep1b78e7jsn66fc99cfd3c6",
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    watchlistResponseData = response.json()

    if form.validate_on_submit():
        tickerWatch = form.ticker.data
        tickerWatchU = tickerWatch.upper()

        if tickerWatchU not in strippedTickers:

            newWatchlistTicker = Watchlist(ticker=tickerWatch, email_id=session['email'])

            db.session.add(newWatchlistTicker)
            db.session.commit()
            flash('Stock added to wathclist')
            return redirect('/watchlist-test')

    return render_template("watchlist-test.html", form=form,  strippedTickers=strippedTickers, strippedList=strippedList, watchlistData=watchlistResponseData, allTickers=allTickers) #""" , response=response, watchlistData=watchlistData) """
#============================================================
#=============================================================
@app.route('/symbol', methods=["GET", "POST"])
def symbol():
    ticker = request.form["symbol"]

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
    querystring = {"region":"US","symbols": {ticker}}

    newsUrl = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/list"
    querystringNews = {"category":{ticker},"region":"US"}

    #chartUrl = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-charts"
    #chartQuerystring = {"symbol":"amd","interval":"5m","range":"1d","region":"US"}

    headers = {
        'x-rapidapi-key': "3b0e1aa5d4msh7224630a28298fep1b78e7jsn66fc99cfd3c6",
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
    headersNews = {
        'x-rapidapi-key': "3b0e1aa5d4msh7224630a28298fep1b78e7jsn66fc99cfd3c6",
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    responseNews = requests.request("GET", newsUrl, headers=headersNews, params=querystringNews)

    def testData(data):
        if bool(data) == False:
            data = " - "
            return data
        else:
            return data

    tickerData = response.json()
    newsData = responseNews.json()
    #------------------
    #here we will do some testing
    # define time frame
    start = dt.datetime(2021,1,1)
    end = dt.datetime.now()

    # load data 
    stockData = web.DataReader(ticker, 'yahoo', start, end)
    #restructure data
    stockData = stockData[['Open', 'High', 'Low', 'Close']]
    stockData.reset_index(inplace=True)
    stockData['Date'] = stockData['Date'].map(mdates.date2num)

    # Generate the figure **without using pyplot**.
    fig = Figure()

    #sizing 
    fig.set_size_inches(12,7)

    axx = fig.subplots()
    #axx = plt.subplot()
    axx.grid(True)
    axx.set_axisbelow(True)
    axx.set_title(ticker.upper(), color='#505050')
    axx.set_facecolor('#f8f8ff')
    axx.figure.set_facecolor('white')
    axx.tick_params(axis='both', which='both', colors='#606060')
    axx.xaxis_date()
    
    # here we are destructiring the candlesticks to set the outline color of the candles to be black 
    # becauese without this, the outline was simply the same color as the candlestick color
    lines, patches = candlestick_ohlc(axx, stockData.values, width=.9, colorup='#00ff00', colordown='#ff3838', alpha=0.9)
    for line, patch in zip(lines, patches):
        patch.set_edgecolor("k")
        patch.set_linewidth(0.4)
        patch.set_antialiased(False)
        line.set_color("k")
        line.set_zorder(0) # make lines appear behind the patches
        line.set_visible(True) # make them invisible

    #ax.plot(chartFig)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    datax = base64.b64encode(buf.getbuffer()).decode("ascii")
    imgSrc = f"data:image/png;base64,{datax}"

    return render_template(
        "symbol.html", data=tickerData, ticker=ticker, imageSource=imgSrc, testData=testData, newsData=newsData)

