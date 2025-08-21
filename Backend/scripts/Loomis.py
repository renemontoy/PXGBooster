import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, Form, HTTPException # pyright: ignore[reportMissingImports]

async def Loomis(
        file: UploadFile = File(...),
        depositdate: str = Form(...),
        ):
    
    if not file.filename:
        raise HTTPException(status_code=400, detail= "Archivo no seleccionado")

    try:
        ChaseFile = await file.read()
    
        #Files
        dfChase = pd.read_excel(io.BytesIO(ChaseFile), sheet_name='10280', skiprows=13, header=0)
        
        #Sacar data de fecha determinada
        dfChasetoday = dfChase[dfChase['Posting Date'] == depositdate].copy()
        dfChasetoday['Document Ref.'] = dfChasetoday['Check or Slip #'].astype(int)
        dfChasetoday.loc[dfChasetoday['Notes'] == 'Loomis S7', ['Notes']] = ['Loomis S07']
        dfChasetoday = dfChasetoday.sort_values('Notes')
        dfChasetoday['Fecha'] = dfChasetoday['Description'].str.extract(r' Depdate= (\d{2}/\d{2}/\d{4})')
        dfChasetoday['Deposit Date'] = depositdate
        dfChasetoday['Deposit Date'] = pd.to_datetime(dfChasetoday['Deposit Date'])
        dfChasetoday['Deposit Date'] = dfChasetoday['Deposit Date'].dt.strftime('%m/%d/%Y')
        dfChasetoday['Cash Account'] = '10280'
        dfChasetoday['Fin. Period'] = '08-2025'
        dfChasetoday['Cash Drop Account'] = '101' + dfChasetoday['Notes'].str[-2:]
        dfChasetoday['Concat'] = dfChasetoday['Fecha'] + ' ' + dfChasetoday['Notes']
        dfChasetoday['Concat'] = dfChasetoday['Concat'].str.replace('/','.')
        dfChasetoday['Line'] = range(1, len(dfChasetoday) + 1)
        dfChasetoday = dfChasetoday[['Cash Account','Deposit Date', 'Fin. Period', 'Document Ref.', 'Cash Drop Account','Concat','Amount','Line',]]
        dfChasetoday.rename(columns={
            'Concat':'Description',
            'Amount' : 'Control Total'
        }, inplace=True)
        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dfChasetoday.to_excel(writer, sheet_name='DRAFT', index=False)
            

        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': 'attachment; filename="Bank_deposits_GP.xlsx"'
            }
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error de codificación.")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el US Chase.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")