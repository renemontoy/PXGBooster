import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, Form, HTTPException # pyright: ignore[reportMissingImports]

async def OOR(
        file: UploadFile = File(...)
        ):
    
    if not file.filename:
        raise HTTPException(status_code=400, detail= "Archivo no seleccionado")

    try:
        OORFile = await file.read()
    
        #Files
        dfOOR = pd.read_excel(io.BytesIO(OORFile), sheet_name='Open Orders ')
        
        dfOORordenes = dfOOR.copy()

        dfOORordenes = dfOORordenes[['PO Number','Sales Remark']]

        filtro = (
            (dfOORordenes.index == 0) |  # Mantener primera fila
            ((dfOORordenes['Sales Remark'] != 'Sales Remark') &  # No sea "Sales Remark"
            (dfOORordenes['Sales Remark'].notna()) &  # No sea NaN
            (dfOORordenes['Sales Remark'] != ''))  # No sea string vacío
        )

        df_limpio = dfOORordenes[filtro]
        df_limpio = df_limpio[['PO Number']]
        dfordenes = df_limpio.drop_duplicates()


        dfOOR = dfOOR[['Shipping Origin', 'Ship to', 'Distributor', 'Project', 'PO Number',
            'Line Number', 'Material Sku', 'Description', 'PO Qty',
            'Current Unit Price', 'PO Creation Date', 'ORG Ship Date',
            'ETD Updated of 2/4 OOR ', 'ETD Updated of 2/11 OOR ', 'Shipped Qty',
            'Unshipped', 'Shipped Date', 'Factory INV #', 'MOT', 'Sales Remark']]

        lista_po = dfordenes['PO Number'].tolist()

        dfOOR_filtrado = dfOOR[dfOOR['PO Number'].isin(lista_po)]

        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dfOOR_filtrado.to_excel(writer, sheet_name='OOR', index=False)
            

        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': 'attachment; filename="OOR.xlsx"'
            }
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error de codificación.")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el US Chase.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")