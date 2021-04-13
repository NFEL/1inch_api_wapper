import json
import requests
import typing


from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI,Depends,Response, responses
from pydantic import BaseModel
from web3 import Web3


from sqlalchemy.orm import Session

class Item(BaseModel):
    walletAddress: typing.Optional[str]
    fromToken: str
    toToken: str
    amount: typing.Optional[float]
    slippage : typing.Optional[int]

from db import models, schemas
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    
    title ="Swap",
    description="A Simple Api for finding good paths between two token swaps (/path) and create a non singed transaction which can then be signed via a wallet singer (meamask , web3 <- private key , ...) ",
    version="1.1",
    docs_url=None,
    redoc_url="/doc",
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

_DB = Depends(get_db)


# @app.post("/log/")
def create_log(log:schemas.LogSchema , db:Session = _DB):
    log_obj = models.Log(data = log.data)
    db.add(log_obj)
    db.commit()
    db.refresh(log_obj)
    return log_obj

@app.get("/log/")
def get_log(db:Session = _DB):
    return db.query(models.Log).all()

tokens = {}




BINANCE_MAINNET = "https://bsc-dataseed1.binance.org:443"
BINANCE_TESTNET = "https://data-seed-prebsc-1-s1.binance.org:8545"
ONE_INCH_BASE_URL = "https://api.1inch.exchange"
SERVER_HEALTH = "/v3.0/56/healthcheck"
ONE_INCH_PATH_FINDER = "​/v3.0​/56​/quote"
ONE_INCH_TOKENS = "​https://api.1inch.exchange/v3.0/56/tokens"
TOKEN_RETRIVAL_FAILED = False
# client = Web3(Web3.HTTPProvider(BINANCE_TESTNET))


USE_OUR_ALGORITHM = False


def check_address():
    pass


def check_allowance():
    pass


def pathfinder():
    pass


"""
on server start up populates memory with tokens availabe
"""
@app.on_event('startup')
async def sync_tokens():
    try:
        res = requests.get("https://api.1inch.exchange/v3.0/56/tokens")
        # print(len(res.json()['tokens']))
        if res.status_code == 200:
            global tokens
            tokens = res.json().get('tokens',None)
            
        else:
            global TOKEN_RETRIVAL_FAILED
            TOKEN_RETRIVAL_FAILED = True
    except Exception:
        TOKEN_RETRIVAL_FAILED = True
        
        
        
@app.post("/swap")
async def swap(item: Item):
    """
    Swap method :
        Inorder to create a transaction data while calling path method to find best path and distributions between two tokens ! :)
        This function creates transaction to 1inch router !
        Last Step would be another application signing this transation with a (from address ) wallet.
          
    """
    if not Web3.isAddress(item.fromToken):
        return {"message": "From token address is wrong "}
    if not Web3.isAddress(item.toToken):
        return {"message": "Destination token address is wrong "}
    if isinstance(item.amount, float) and not TOKEN_RETRIVAL_FAILED and item.amount < 100:
        item.amount =int (item.amount *  (10 ** int(tokens.get(item.fromToken,None).get("decimals",None))))
    
    if USE_OUR_ALGORITHM:
        return pathfinder(item)
    else:
        try : 
            res = requests.get("https://api.1inch.exchange/v3.0/56/swap", params={
                "fromTokenAddress": item.fromToken,
                "fromAddress" : item.walletAddress,
                "toTokenAddress": item.toToken,
                "slippage" : item.slippage,
                "amount": item.amount,
            })
            if res.status_code == 200:
                return responses.JSONResponse(res.json())
            if res.status_code == 500:
                return responses.JSONResponse({"error":res.json()['message']})
        except Exception : 
            pass
        res = responses.JSONResponse(jsonable_encoder({
            "error" : "something bad Happend X_X"
        }))
        res.status_code = 422
        return res
    
    
@app.post("/path")
async def path(item: Item):
    """
    path method :
        finds good path and destributions from token to token :)
    """
    if not Web3.isAddress(item.fromToken):
        return {"message": "From token address is wrong "}
    if not Web3.isAddress(item.toToken):
        return {"message": "Destination token address is wrong "}
    if isinstance(item.amount, float) and not TOKEN_RETRIVAL_FAILED and item.amount < 100:
        item.amount =int(item.amount *  (10 ** int(tokens.get(item.fromToken,None).get("decimals",None))))

    if USE_OUR_ALGORITHM:
        return pathfinder(item)
    else:
        try : 
            res = requests.get("https://api.1inch.exchange/v3.0/56/quote", params={
                "fromTokenAddress": item.fromToken,
                "toTokenAddress": item.toToken,
                "amount": item.amount,
            })
            if res.status_code == 200:
                return responses.JSONResponse(res.json())
            if res.status_code == 500:
                return responses.JSONResponse({"error":res.json()['message']})
        except Exception : 
            pass
        res = responses.JSONResponse(jsonable_encoder({
            "error" : "something bad Happend X_X"
        }))
        res.status_code = 422
        return res
                                     

@app.get("/toturial-metamask")
async def sign_with_metamsak():
    """
    Visit <a href="http://localhost:8000/toturial-metamask">Here</a>
    """
    with open("Singing with meta mask.html" , "r") as f:
        return responses.HTMLResponse(f.read())
    
@app.get("/toturial-nodejs")
async def sign_with_metamsak():
    """
    Visit <a href="http://localhost:8000/toturial-nodejs">Here</a>
    """
    with open("Singing with nodejs.html" , "r") as f:
        return responses.HTMLResponse(f.read())
    