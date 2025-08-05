from fastapi import APIRouter, UploadFile, File, Form # pyright: ignore[reportMissingImports]
from scripts.Adyen import Adyen
from scripts.Canada import Canada
from scripts.Shopify import Shopify
from scripts.Ferrule import Ferrule

router = APIRouter()

@router.post("/uploadadyen/")
async def procesar(
    file: UploadFile = File(...),
    file2: UploadFile = File(...),
    deposit: str = Form(...),
    account: str = Form(...),
    depositdate: str = Form(...),
    period: str = Form(...),
    paymentmethod: str = Form(...)
):
    return await Adyen(file, file2, deposit, account, depositdate, period, paymentmethod)

@router.post("/uploadcanada")
async def procesar(
    file: UploadFile = File(...),
):
    return await Canada(file)

@router.post("/uploadshopify")
async def procesar(
    file: UploadFile = File(...),
    file2: UploadFile = File(...),
    deposit: str = Form(...),
    account: str = Form(...),
    depositdate: str = Form(...),
    period: str = Form(...),
    paymentmethod: str = Form(...)
):
    return await Shopify(file, file2, deposit, account, depositdate, period, paymentmethod)

@router.post("/uploadferrule")
async def procesar(
    file: UploadFile = File(...),
):
    return await Ferrule(file)

