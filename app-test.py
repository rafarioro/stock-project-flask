    
    #get tickers from watchlist table
    testTickers = Watchlist.query.with_entities(Watchlist.ticker).filter(Watchlist.email_id == session['email']).all()

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