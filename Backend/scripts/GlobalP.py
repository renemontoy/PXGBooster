import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, Form, HTTPException # pyright: ignore[reportMissingImports]

async def GlobalPayments(
        file: UploadFile = File(...),
        account: str = Form(...),
        depositdate: str = Form(...),
        period: str = Form(...)
        ):
    
    if not file.filename:
        raise HTTPException(status_code=400, detail= "Archivo no seleccionado")

    try:
        ChaseFile = await file.read()
    
        #Files
        dfChase = pd.read_excel(io.BytesIO(ChaseFile), sheet_name='10250', skiprows=13, header=0)
        #Diccionario Retails
        retails  = {
            'CHARLOTTE' : 'Charlotte',
            'WESTCHESTER': 'New Rochelle',
            'BOSTON' : 'Boston',
            'CHICAGO- NORTH' : 'Chicago',
            'MINNEAPOLIS' : 'Minneapolis',
            'CHICAGO- WEST' : 'Oakbrook',
            'SAN JOSE' : 'San Jose',
            'PHILADELPHIA' : 'Philadelphia',
            'KANSAS CITY' : 'Kansas City',
            'SAN DIEGO' : 'San Diego',
            'DETROIT' : 'Detroit',
            'WESTGATE' : 'Westgate',
            'MESA' : 'Mesa',
            'HOUSTON' : 'Houston',
            'CINCINNATI': 'Cincinnati',
            'FAIRFAX' : 'Fairfax',
            'DENVER' : 'Centennial',
            'DUBLIN' : 'East Bay',
            'ORANGE COUNTY' :'Orange County',
            'ORLANDO' : 'Orlando',
            'INDIANAPOLIS' : 'Indianapolis',
            'SEATTLE' : 'Seattle',
            'DALLAS' : 'Dallas',
            'POP UP' : 'Pop Up',
            'PARAMUS' : 'Paramus',
            'ATLANTA' : 'Atlanta',
            'SCOTTSDALE' : 'Scottsdale'
        }


        #Sacar data de fecha determinada
        dfChasetoday = dfChase[dfChase['Posting Date'] == depositdate]
        dfChasetoday = dfChasetoday[['Posting Date','Description','Amount']]

        #Document Ref.
        dfChasetoday['Document Ref.'] = dfChasetoday['Description'].str[-12:]

        #Global Payments
        dfmerchant = dfChasetoday[dfChasetoday['Description'].str.contains('MERCHANT', na=False, case=False)].copy()
        dfmerchant['Fecha'] = dfmerchant['Description'].str.extract(r'DESC DATE:(\d{6})')
        def transformar_fecha(fecha):
            if len(fecha) == 6:  # Asegurarse de que la longitud sea correcta
                año = '20' + fecha[0:2]
                mes = fecha[2:4]
                dia = fecha[4:6]  # Asumimos que el año es 20XX
                return f"{mes}.{dia}.{año}"
            return "Fecha no válida"
        dfmerchant['Fecha formateada'] = dfmerchant['Fecha'].apply(transformar_fecha)
        dfmerchant['extracted'] = dfmerchant['Description'].str.extract(r'(CHARLOTTE|WESTCHESTER|BOSTON|CHICAGO- NORTH|MINNEAPOLIS|CHICAGO- WEST|SAN JOSE|PHILADELPHIA|KANSAS CITY|SAN DIEGO|DETROIT|WESTGATE|MESA|HOUSTON|CINCINNATI|FAIRFAX|DENVER|DUBLIN|ORANGE COUNTY|ORLANDO|INDIANAPOLIS|SEATTLE|DALLAS|CINCINNATI|POP UP|PARAMUS|ATLANTA|SCOTTSDALE)', expand=False)
        dfmerchant['Retails'] = dfmerchant['extracted'].map(retails)
        dfmerchant['New Description'] = dfmerchant['Fecha formateada'] + " Global Payments - " + dfmerchant['Retails']

        dfmerchant = dfmerchant[['Document Ref.','New Description','Amount']]

        dfmerchant.rename(columns={
            'New Description' : 'Description',
            'Amount' : 'Control Total'
        }, inplace=True)
        
        dfmerchant['Cash Account'] = account
        dfmerchant['Fin. Period'] = period
        dfmerchant['Deposit Date'] = depositdate
        dfmerchant['Cash Drop Account'] = ""
        dfmerchant['Line'] = range(1, len(dfmerchant) + 1) 

        dfmerchant = dfmerchant[[
            'Cash Account',
            'Deposit Date',
            'Fin. Period',
            'Document Ref.',
            'Cash Drop Account',
            'Description',
            'Control Total',
            'Line'
        ]]
        dfmerchant['Deposit Date'] = pd.to_datetime(dfmerchant['Deposit Date'])
        dfmerchant['Deposit Date'] = dfmerchant['Deposit Date'].dt.strftime('%m/%d/%Y')
        
        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dfmerchant.to_excel(writer, sheet_name='DRAFT', index=False)
            

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