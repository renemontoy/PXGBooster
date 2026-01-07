from fastapi import APIRouter, UploadFile, File, Form, HTTPException # pyright: ignore[reportMissingImports]
from scripts.Adyen import Adyen
from scripts.Canada import Canada
from scripts.Shopify import Shopify
from scripts.Ferrule import Ferrule
from scripts.GlobalP import GlobalPayments
from scripts.Spec import Spec
from scripts.Defect import Defect
from scripts.Loomis import Loomis
from scripts.ValidationMS import ValidationMS 
from scripts.Brett import Brett
from scripts.Receipt import ValidationReceipt
from typing import List

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

@router.post("/uploadmsmanifest/")
async def procesar(
    file: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    return await ValidationMS(file, file2)

@router.post("/uploadreceipt/")
async def procesar(
    transfers_files: List[UploadFile] = File(...),          
    ies_files: List[UploadFile] = File(...),    
):
    # Verificar que hay archivos
    if not transfers_files or not ies_files:
        raise HTTPException(
            status_code=400, 
            detail="Debe proporcionar ambos tipos de archivos"
        )
    
    # Verificar límites de Render (100MB por defecto)
    total_size = 0
    for file in transfers_files + ies_files:
        # Guardar el contenido en memoria para no perderlo
        setattr(file, "_content", await file.read())
        total_size += len(file._content)
    
    if total_size > 50 * 1024 * 1024:  # 50MB límite recomendado
        raise HTTPException(
            status_code=413, 
            detail="Tamaño total de archivos excede el límite de 50MB"
        )
    
    return await ValidationReceipt(transfers_files, ies_files)


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

@router.post("/tsysdeposits")
async def procesar(
    file: UploadFile = File(...),
    file2: UploadFile = File(...),
    username: str = Form(...),
    password: str = Form(...),
):
    return await Loomis(file, file2, username, password)

@router.post("/uploadbrett")
async def procesar(
    file: UploadFile = File(...),
):
    return await Brett(file)