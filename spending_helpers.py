# -*- coding: utf-8 -*-
"""
2022-12-12

Helper functions for parsing personal financial data.
"""
import pandas as pd
import pdfplumber as pdf
import re

def date_parser(date: str) -> pd.datetime:
    """Transforms a date in MMMDD str format to pd.datetime. Year 2022 assumed.
    
    date: String date in MMMDD format.
    return: Datetime value
    
    >>> date_parser("JAN6")
    Timestamp('2022-01-06 00:00:00')
    >>> col_conv("Dec 25")
    Timestamp('2022-12-25 00:00:00')
    """
    current_year = "2022"
    months = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, 
              "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    

    day = date[3:]
    str_month = date[0:3].upper()
    month = str(months[str_month])
    
    return pd.to_datetime("-".join([current_year, month, day]))

def td_dc_parser(bill: str) -> pd.DataFrame:
    """Transforms a TD checquing account history export into a dataframe.
    
    bill: CSV of a TD chequing account history export.
    return: DataFrame of transation date, description, and amount.
    
    Test cases vary by data.
    """
    # Convert CSV to Dataframe, label headers, and fill NaNs.
    headings = ["Date","Desc","With.","Dep.", "Total"]
    raw = pd.read_csv(bill, header = None, names = headings).fillna(0)
    
    # Drop total col., simplify transaction history, convert dates
    clean = raw.drop("Total", 1)
    clean["Amt"] = clean["With."] - clean["Dep."]
    clean = clean.drop(["With.", "Dep."], 1)
    clean["Date"] = clean["Date"].apply(pd.to_datetime)
    
    return clean

def td_cc_parser(bill: str) -> pd.DataFrame:
    """Transforms a TD credit card statement in PDF form into a dataframe.
    
    bill: PDF of a TD credit card statement.
    return: DataFrame of transaction date, description, and amount.
    
    Test cases vary by data.
    """
    # Convert PDF to string, split into list of rows, strip whitespace.
    raw = pdf.open(bill)
    full_text = []
    for page in raw.pages:
        full_text += page.extract_text(layout = True).split("\n")
    stripped = [i.strip() for i in full_text]
    
    # Regex identify which rows include meaningful data.
    spends = []
    for j in stripped:
        if bool(re.match("[A-Z]{3}\d[^,]{2}", j)):
            spends.append(j)
    
    # Split rows into usable columns, convert to usable datatypes.
    clean = pd.DataFrame(
        [k.split()[:4] for k in spends]
        ).drop(1, 1)\
        .rename(columns = {0: "Date", 2: "Desc", 3:"Amt"})
    clean["Date"] = clean["Date"].apply(date_parser)
    clean["Amt"] = clean["Amt"].apply(lambda a: a.replace(",", ""))
    clean["Amt"] = clean["Amt"].apply(lambda b: float(b.replace("$", "")))
    
    return clean

def neo_cc_parser(bill: str) -> pd.DataFrame:
    """Transforms a Neo credit card statement in PDF form into a dataframe.
    NOTE: Basic Neo PDF statement encoding is screwed up right now. Need to 
    run the raw statement through an OCR converter first (e.g., convert to 
    .docx then back to .pdf).
    
    bill: PDF of a Neo credit card statement.
    return: DataFrame of transaction date, description, and amount.
    
    Test cases vary by data.
    """
    # Convert PDF to string, split into list of rows, strip whitespace.
    raw = pdf.open(bill)
    full_text = []
    for page in raw.pages:
        full_text += page.extract_text(layout = True).split("\n")
    stripped = [i.strip() for i in full_text]
    
    # Regex identify which rows include meaningful data.
    spends = []
    for j in stripped:
        if bool(re.match("[A-Z][a-z]{2} \d[^,]{2}", j)):
            spends.append(j)
    
    # Split rows into usabe columns.
    clean = []
    for m in [k.split() for k in spends]:
        holder = []
        holder.append(''.join((m[0].upper(), m[1])))
        holder.append(''.join(m[4:-1]))
        holder.append(m[-1])
        clean.append(holder)
    
    # Convert to usable datatypes.
    clean = pd.DataFrame(clean).rename(columns = {0: "Date", 1: "Desc", 2:"Amt"})
    clean["Date"] = clean["Date"].apply(date_parser)
    clean["Amt"] = clean["Amt"].apply(lambda a: a.replace("O", "0"))
    clean["Amt"] = clean["Amt"].apply(lambda b: b.replace(",", ""))
    clean["Amt"] = clean["Amt"].apply(lambda c: -float(c.replace("$", "")))
    
    return clean