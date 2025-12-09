import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, Form, HTTPException # pyright: ignore[reportMissingImports]

##async def Tsys(
##    file: UploadFile = File(...),          
##    file2: UploadFile = File(...),        
##    username: str = Form(...),
##    password: str = Form(...),
##):

    # Verificación básica de archivos
    ##if not file.filename or not file2.filename:
    ##    raise HTTPException(status_code=400, detail="Debe proporcionar ambos archivos")

   ## try:


    ##except UnicodeDecodeError:
    ##    raise HTTPException(status_code=400, detail="Error de codificación. Intente guardar los archivos como UTF-8 BOM")
    ##except pd.errors.ParserError:
    ##    raise HTTPException(status_code=400, detail="Error al analizar el CSV. Verifique el delimitador (usar coma o punto y coma)")
    ##except Exception as e:
    ##    raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")