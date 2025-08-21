from fastapi import APIRouter, UploadFile, File, Form # pyright: ignore[reportMissingImports]
from scripts.Adyen import Adyen
from scripts.Canada import Canada
from scripts.Shopify import Shopify
from scripts.Ferrule import Ferrule
from scripts.GlobalP import GlobalPayments
from scripts.Spec import Spec
from scripts.Defect import Defect
from scripts.Loomis import Loomis

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

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

@router.post("/uploadglobalpayments")
async def procesar(
    file: UploadFile = File(...),
    account: str = Form(...),
    depositdate: str = Form(...),
    period: str = Form(...)
):
    return await GlobalPayments(file, account, depositdate, period)

@router.post("/uploadspec")
async def procesar(
    file: UploadFile = File(...),
    weekfront: str = Form(...)
):
    return await Spec(file, weekfront)

@router.post("/uploaddefect")
async def procesar(
    file: UploadFile = File(...),
    file2: UploadFile = File(...),
    weekfront: str = Form(...)
):
    return await Defect(file, file2, weekfront)

@router.post("/uploadloomis")
async def procesar(
    file: UploadFile = File(...),
    depositdate: str = Form(...),
):
    return await Loomis(file, depositdate)