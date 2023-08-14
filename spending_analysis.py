# -*- coding: utf-8 -*-
"""
2022-12-13

Attempt at collating personal spending trends for 2022.
NEGATIVES are cash INFLOW. POSITIVES are cash OUTFLOW.
"""
import pandas as pd
import glob
import spending_helpers as sh

# Differentiating the various statements in the folder.
neo = glob.glob("6*.pdf")
td_cc = [i for i in glob.glob("*.pdf") if i not in neo]
td_dc = glob.glob("*.csv")

# Initialising empty dataframe to fill.
master = pd.DataFrame(columns = ["Date", "Desc", "Amt"])

# THE ACTUAL LOOPS
for x in neo:
    bill = sh.neo_cc_parser(x)
    master = pd.concat((master, bill))
for y in td_cc:
    bill = sh.td_cc_parser(y)
    master = pd.concat((master, bill))
for z in td_dc:
    bill = sh.td_dc_parser(z)
    master = pd.concat((master, bill))

# Formatting
master = master.sort_values("Date").reset_index().drop("index", 1)

"""
Various levels of filtering
"""

# Removing inter-account transfers
accountless = master[~(
    master["Desc"].str.contains("PAYMENT|Payment|C/C|NEO FINANCE")
    )]

# Filter government payments
canadaless = accountless[~(
    (accountless["Desc"].str.contains("CANADA ")) & 
    (accountless["Amt"] < 0)
    )]
canada = accountless[
    (accountless["Desc"].str.contains("CANADA ")) & 
    (accountless["Amt"] < 0)
    ]

# Filter cash inflow
expenses = canadaless[~(
    canadaless["Desc"].str.contains("E-TRANSFER|U of T")
    )]
etransfers = canadaless[canadaless["Desc"].str.contains("E-TRANSFER")]
pay = canadaless[canadaless["Desc"].str.contains("U of T")]

"""
Interesting key-lists and useful functions

in 23 pay 10
cost 14 tu 9 lo 2 me 1
left 7
"""
uber = ["UBER"]
amazon = ["Amazon", "AMZ"]
groceries = ["FARMBOY", "FOOD BASICS", "GALLERIA", "HMART", "H-MART", "IKEA", "LCBO", "LONGOS", "NOFRILLS", "SHOPPERS", "T&T"]
rogers = ["ROGERS"]
presto = ["PRESTO"]
nslsc = ["NSLSC"]
games = ["GOG", "HUMBLEBUNDLE", "SteamPurchase"]
minis = ["401", "MEEPLEMART"]

def searcher(descs: list) -> pd.DataFrame:
    """Searches the expenses dataframe for expenses associated with keywords.
    descs: List of keywords to search the Desc. column for.
    returns: Dataframe of expenses associated with the keywords.
    """
    return expenses[expenses["Desc"].str.contains("|".join(descs))]

def summer(descs: list) -> float:
    """Sums the expenses identified by the searcher function.
    descs: List of keywords to search the Desc. column for.
    returns: Float representation of the expense sum.
    """
    return searcher(descs)["Amt"].sum()
    
# # Export to excel.
# export = expenses.reset_index().drop("index", 1)
# export.to_excel("results.xlsx")