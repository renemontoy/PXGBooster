import pandas as pd
import io
from io import BytesIO
from fastapi.responses import StreamingResponse
from openpyxl.styles import NamedStyle
from fastapi import UploadFile, File, Form, HTTPException

async def Adyen(
    file: UploadFile = File(...),          # ACMA (Excel)
    file2: UploadFile = File(...),         # Adyen (CSV)
    deposit: str = Form(...),
    account: str = Form(...),
    depositdate: str = Form(...),
    period: str = Form(...),
    paymentmethod: str = Form(...)
):
    maxrows = 160
    text_style = NamedStyle(name="text_style", number_format="@")

    # Verificación básica de archivos
    if not file.filename or not file2.filename:
        raise HTTPException(status_code=400, detail="Debe proporcionar ambos archivos")

    try:
        # Leer contenido de los archivos
        acma_content = await file.read()
        adyen_content = await file2.read()

        # Procesar Adyen (CSV) - Versión robusta
        dfAdyen = pd.read_csv(io.BytesIO(adyen_content), encoding='utf-8-sig',delimiter=',')
        dfAcma = pd.read_excel(io.BytesIO(acma_content),engine='openpyxl')
        #Adyen
        dfAdyen = dfAdyen[['Type','Merchant Reference','Psp Reference','Modification Reference','Gross Credit (GC)','Modification Merchant Reference']]
        dfAdyen.rename(columns={
            'Psp Reference':'Payment Ref.'
        }, inplace=True)
        dfAdyen = dfAdyen[dfAdyen['Payment Ref.'].notna()]


        #Acma
        dfAcma = dfAcma[['Type','Reference Nbr.','Payment Ref.']]


        #Refunds                
        dfrefunds = dfAdyen.loc[dfAdyen['Type'] =='Refunded']
        dfrefunds = dfrefunds.drop(columns=['Payment Ref.'])
        dfrefunds = dfrefunds.loc[
            (dfrefunds['Merchant Reference'].str.len() != 37) | 
            (dfrefunds['Merchant Reference'].isna())
        ]
        dfrefunds.rename(columns={
            'Modification Reference':'Payment Ref.'
        }, inplace=True)


        dfshopifyrefunds = dfAdyen.loc[dfAdyen['Merchant Reference'].str.len() == 37].copy()
        dfshopifyrefunds =  dfshopifyrefunds.loc[dfAdyen['Type'] =='Refunded']
        dfshopifyrefunds = dfshopifyrefunds.drop(columns=['Payment Ref.'])
        dfshopifyrefunds.rename(columns={
            'Modification Merchant Reference':'Payment Ref.'
        }, inplace=True)
        dfshopifyrefunds['Payment Ref.'] = dfshopifyrefunds['Payment Ref.'].str[12:]


        dfmergeallrefunds = pd.concat([dfrefunds,dfshopifyrefunds], ignore_index=True)
        #print(dfmergeallrefunds)
        dfmergerefunds = pd.merge(dfmergeallrefunds,dfAcma,  how='left', on='Payment Ref.', suffixes=('dfAdyen','dfAcma'))
        dfmergerefunds =dfmergerefunds[['Merchant Reference','Payment Ref.','Reference Nbr.']]
        #print(dfmergerefunds)

        #WebEcom
        dfpaymentshopiffy = dfAdyen.loc[dfAdyen['Merchant Reference'].str.len() == 37].copy()
        dfpaymentshopiffy['Merchant Reference'] = dfpaymentshopiffy['Merchant Reference'].str[12:]
        dfpaymentshopiffy.drop('Payment Ref.', axis=1, inplace=True)
        dfpaymentshopiffy.rename(columns={
            'Merchant Reference': 'Payment Ref.'
        }, inplace=True)
        #print(dfpaymentshopiffy)

        #Payments
        dfpaymetnsADYEN = dfAdyen.loc[dfAdyen['Type']=='Settled']
        dfpaymetnsADYEN = dfpaymetnsADYEN.loc[
            (dfpaymetnsADYEN['Merchant Reference'].str.len() != 37) | 
            (dfpaymetnsADYEN['Merchant Reference'].isna())
        ]
        dfpayments = pd.concat([dfpaymentshopiffy, dfpaymetnsADYEN], ignore_index=True)
        dfmergepayments = pd.merge(dfpayments,dfAcma,  how='left', on='Payment Ref.', suffixes=('dfAdyen','dfAcma'))
        dfmergepayments = dfmergepayments.loc[dfmergepayments['TypedfAcma']=='Payment']
        dfmergepayments =dfmergepayments[['Payment Ref.','Reference Nbr.']]
        #print(dfmergepayments)

        #PaymentsNA
        dfmergepaymentsNA = pd.merge(dfpaymetnsADYEN,dfAcma,  how='left', on='Payment Ref.', suffixes=('dfAdyen','dfAcma'))
        dfmergepaymentsNA = dfmergepaymentsNA.loc[dfmergepaymentsNA['TypedfAcma'].isna()]
        #dfpaymentsNA = dfmergepaymentsNA.drop(columns=['Payment Ref.'])
        dfmergepaymentsNA.rename(columns={
            'Payment Ref.':'Modification Reference',
            'Modification Reference':'Payment Ref.'
        }, inplace=True)
        dfpaymentsNA = pd.merge(dfmergepaymentsNA,dfAcma,  how='left', on='Payment Ref.', suffixes=('dfAdyen','dfAcma'))
        dfpaymentsNAModif = dfpaymentsNA.loc[dfpaymentsNA['Type']=='Payment']

        #Enter Manually
        dfpaymentsNAManually = dfpaymentsNA.loc[dfpaymentsNA['Type'].isna()]
        dfpaymentsNAManually =dfpaymentsNAManually[['TypedfAdyen','Merchant Reference','Modification Reference','Payment Ref.','Gross Credit (GC)']]
        dfpaymentsNAManually.rename(columns={
            'TypedfAdyen' : 'Type',
            'Payment Ref.':'Modification Reference',
            'Modification Reference':'Payment Ref.'
        }, inplace=True)
        #print(dfpaymentsNAManually)

        #Allpayments

        dfpaymentsNAModif =dfpaymentsNAModif[['Payment Ref.','Reference Nbr.dfAcma']]
        dfpaymentsNAModif.rename(columns={
            'Reference Nbr.dfAcma':'Reference Nbr.'
        }, inplace=True)
        dfmergeallpayments = pd.concat([dfmergepayments,dfpaymentsNAModif])
        
        dfmergeallpayments['Deposit Reference Nbr.'] = deposit

        dfmergeallpayments['Cash Account'] = account
        dfmergeallpayments['Deposit Date'] = depositdate
        dfmergeallpayments['Fin. Period'] = period
        dfmergeallpayments['Payment Method'] = paymentmethod

        dfmergeallpayments = dfmergeallpayments[[
            'Deposit Reference Nbr.', 
            'Cash Account', 
            'Deposit Date', 
            'Fin. Period', 
            'Payment Method', 
            'Payment Ref.', 
            'Reference Nbr.'
        ]]

        dfmergeallpayments['Deposit Date'] = pd.to_datetime(dfmergeallpayments['Deposit Date'])
        dfmergeallpayments['Deposit Date'] = dfmergeallpayments['Deposit Date'].dt.strftime('%m/%d/%Y')
        
        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Dividir dfmergeallpayments en fragmentos de maxrows filas
            total_rows = len(dfmergeallpayments)
            num_sheets = (total_rows // maxrows) + (1 if total_rows % maxrows != 0 else 0)
            
            for i in range(num_sheets):
                start_row = i * maxrows
                end_row = start_row + maxrows
                sheet_name = f"Sheet1_{i + 1}"
                dfmergeallpayments.iloc[start_row:end_row].to_excel(writer, sheet_name=sheet_name, index=False)
            
            dfmergerefunds.to_excel(writer, sheet_name='Refunds', index=False)
            dfpaymentsNAManually.to_excel(writer, sheet_name='Missing', index=False)
            

        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': 'attachment; filename="Bank_Deposit_Upload_Adyen.xlsx"'
            }
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error de codificación. Intente guardar los archivos como UTF-8 BOM")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el CSV. Verifique el delimitador (usar coma o punto y coma)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")