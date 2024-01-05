import pandas as pd
from fastapi import FastAPI
from supabase import create_client, Client

import ai_model
import price_pred

supabase: Client = create_client(
    "https://eobauqgsolxvyamddpjl.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVvYmF1cWdzb2x4dnlhbWRkcGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDQzNzc4OTcsImV4cCI6MjAxOTk1Mzg5N30.hJx5GMmCS6PWnRio9hOJB04ZkoO5Cf-WD_O1zjc7yRI",
)
app = FastAPI()


@app.get("/")
async def read_root():
    return None


@app.get("/check_stock")
async def generate(open: float, esg: float, pe: float, roe: float, days: int = 1, stock: str = None):
    if stock:
        response = supabase.table("STOCKS").select(
            "*").eq("stock_name", stock).execute()

    if not stock or not response[1][0]["investment_check"]:
        response = bool(ai_model.generate_data(
            pd.DataFrame(
                [[
                    days, open, esg, pe, roe
                ]],
                columns=[
                    'horizon (days)', 'price_BUY', 'ESG_ranking', 'PE_ratio', 'roe_ratio'
                ]
            )
        )[0] == 1)
        if stock:
            supabase.table("STOCKS").update({"investment_check": response}).eq(
                "stock_name", stock).execute()
    return response


@app.get("/future")
async def generate(open: float, high: float, low: float, volume: int, days=7):
    return price_pred.generate(open, high, low, volume, days)