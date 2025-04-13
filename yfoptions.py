import pandas as pd
import yfinance as yf


# calculating columns how many days to expiration dates
def daysleft(inputdate):
    import datetime

    previous_date = datetime.datetime.strptime(inputdate, "%Y-%m-%d")
    today = datetime.datetime.today()
    ndays = (previous_date - today).days + 1
    return ndays


# get All Option Chain for a ticker, calculate additional columns and retun as a dataframe from Yahoo finance
def get_DF_optionchain(ticker):
    import requests

    session = requests.Session()
    tkobj = yf.Ticker(ticker, session=session)
    exps = tkobj.options

    if not exps:
        print(f"No expiration dates found for the ticker {ticker}")
        raise ValueError(f"No expiration dates found for the ticker {ticker}.")
        return None

    # Current Price in Market Session
    lastprice = tkobj.info["currentPrice"]

    # base price for additional column
    # bias_price = 'mark'
    bias_price = "lastPrice"
    print(ticker)
    optionslst = []
    for e in exps:
        try:
            print(e)
            opt = tkobj.option_chain(e)
            # opt_calls = pd.DataFrame().append(opt.calls)
            opt_calls = opt.calls
            opt_calls["Type"] = "CALL"
            # opt_puts = pd.DataFrame().append(opt.puts)
            opt_puts = opt.puts
            opt_puts["Type"] = "PUT"
            combined = pd.concat([opt_calls, opt_puts], ignore_index=True)

            combined["expirationDate"] = e
            combined["daysleft"] = daysleft(e)

            combined[["bid", "ask", "strike"]] = combined[
                ["bid", "ask", "strike"]
            ].apply(pd.to_numeric)
            combined["mark"] = (combined["bid"] + combined["ask"]) / 2

            combined["pricepercent"] = 100 * combined[bias_price] / lastprice
            combined["pricepercentstrike"] = (
                100 * combined[bias_price] / combined["strike"]
            )
            combined["interinsicvalue"] = combined.apply(
                lambda row: abs(lastprice - row["strike"]) if row["inTheMoney"] else 0,
                axis=1,
            )
            combined["interinsicvalue%"] = (
                100 * combined["interinsicvalue"] / combined[bias_price]
            )
            combined["timevalue"] = combined.apply(
                lambda row: row[bias_price] - row["interinsicvalue"], axis=1
            )
            combined["timevalue%"] = 100 * combined["timevalue"] / combined[bias_price]
            combined["breakevenprice"] = combined.apply(
                lambda row: row[bias_price] + row["strike"]
                if row["Type"] == "CALL"
                else row["strike"] - row[bias_price],
                axis=1,
            )

            optionslst.append(combined)

        except:
            pass

        optionschain = pd.concat(optionslst, ignore_index=True)
    return optionschain
