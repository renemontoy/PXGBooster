import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, Form, HTTPException # pyright: ignore[reportMissingImports]

async def Canada(
        file: UploadFile = File(...)
        ):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Debe proporcionar ambos archivos")
    try:
        #Files
        CanadaFile = await file.read()
        dfcanada=pd.read_excel(io.BytesIO(CanadaFile),engine='openpyxl')
        dfcanada = dfcanada[dfcanada['Inventory Description']!='redemption']

        dfshipping = dfcanada
        dfdataoriginal = dfcanada
        dfdata = dfcanada
        dfinfo = dfcanada
        Warehousevalue = 'HQ'

        #Hoja Shipping
        dfshipping = dfshipping[dfshipping['Inventory ID'].isna()]

        #Hoja Data Original
        dfdataoriginal = dfdataoriginal[dfdataoriginal['Inventory ID'].notna()]
        dfdataoriginal = dfdataoriginal[['Status','External Reference','Inventory ID','Inventory Description','Order Qty.','Unit Cost','Extended Price']]

        #Hoja Data
        dfdata = dfdata[dfdata['Inventory ID'].notna()]
        dfdata = dfdata[['Inventory ID','Order Qty.','Unit Cost','Extended Price']]
        dfdata['Warehouse'] = Warehousevalue

        #Hoja Info
        totalquantity = dfdata['Order Qty.'].sum()
        totalbalance = dfdata['Extended Price'].sum()
        dfinfo = dfinfo[dfinfo['Inventory ID'].notna()]
        dfinfo = dfinfo.drop_duplicates(subset=['Status', 'External Reference']).copy()
        dfinfo = dfinfo[['External Reference','Status']]
        dfinfo['yes'] = None
        dfinfo['no'] = None
        dfinfo[''] = None
        dfinfo['Total Quantity'] = None
        dfinfo[totalquantity] = None
        dfinfo[''] = None
        dfinfo['Total Balance'] = None
        dfinfo[totalbalance] = None


        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dfdata.to_excel(writer, sheet_name='Data', index=False)
            dfdataoriginal.to_excel(writer, sheet_name='Data - Original', index=False)
            dfshipping.to_excel(writer, sheet_name='Shipping', index=False)
            dfinfo.to_excel(writer, sheet_name='Orders', index=False)



        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': 'attachment; filename="Canada_Orders_Consiliation.xlsx"'
            }
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error de codificación. Intente guardar los archivos como UTF-8 BOM")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el CSV. Verifique el delimitador (usar coma o punto y coma)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")