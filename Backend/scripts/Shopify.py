import pandas as pd
import io
from io import BytesIO
from fastapi.responses import StreamingResponse
from openpyxl.styles import NamedStyle
from fastapi import UploadFile, File, Form, HTTPException

async def Shopify(
    file: UploadFile = File(...),          # ACMA (Excel)
    file2: UploadFile = File(...),         # Adyen (CSV)
    deposit: str = Form(...),
    account: str = Form(...),
    depositdate: str = Form(...),
    period: str = Form(...),
    paymentmethod: str = Form(...)
):
    maxrows = 160
    # Verificación básica de archivos
    if not file.filename or not file2.filename:
        raise HTTPException(status_code=400, detail="Debe proporcionar ambos archivos")

    try:
        #Values
        AcmaFile = await file.read()
        ShopifyFile = await file2.read()

        #Files
        dfShopify=pd.read_csv(io.BytesIO(ShopifyFile), encoding='utf-8-sig')
        dfAcma=pd.read_excel(io.BytesIO(AcmaFile), engine='openpyxl')


        dfShopify = dfShopify[['Type','Order','Amount']]
        dfShopify.rename(columns={
            'Order':'Description'
        }, inplace=True)

        #Acma
        dfAcma = dfAcma[['Type','Description','Reference Nbr.','Payment Ref.']]

        #Refunds
        dfrefunds = dfShopify.loc[dfShopify['Type'] =='refund'].copy()
        dfrefundsAcma = dfAcma.loc[dfAcma['Type'] == 'Refund'].copy()

        dfrefunds.rename(columns={
            'Description':'Reference_clean'
        }, inplace=True)

        print(dfrefunds)
        # Quitar sufijos como ".2", ".3", etc., del final de la columna 'Description'
        dfrefundsAcma['Reference_clean'] = dfrefundsAcma['Payment Ref.'].str.replace(r'\.\d+$', '', regex=True)
        print(dfrefundsAcma)
        dfmergerefunds = pd.merge(dfrefunds,dfrefundsAcma,  how='left', left_on='Reference_clean', right_on='Reference_clean', suffixes=('dfShopy','dfAcma'))
        #print(dfmergerefunds)
        dfmergerefunds = dfmergerefunds[['Description','Payment Ref.','Reference Nbr.','Amount']]
        #dfmergerefunds = dfmergerefunds.drop_duplicates(subset=['Reference Nbr.'])
        

        #Payments
        dfpaymentsShopify = dfShopify.loc[dfShopify['Type']=='charge']
        dfmergepayments = pd.merge(dfpaymentsShopify,dfAcma,  how='left', on='Description', suffixes=('dfShopy','dfAcma'))
        dfmergepayments = dfmergepayments.loc[dfmergepayments['TypedfAcma']=='Payment']
        dfmergepayments =dfmergepayments[['Payment Ref.','Reference Nbr.']]
        #print(dfmergepayments)

        #Enter Manually
        dfpaymentsNAManually = pd.merge(dfpaymentsShopify,dfAcma,  how='left', on='Description', suffixes=('dfShopy','dfAcma'))
        dfpaymentsNAManually = dfpaymentsNAManually.loc[dfpaymentsNAManually ['TypedfAcma'].isna()]
        dfpaymentsNAManually =dfpaymentsNAManually[['TypedfShopy','Description','Amount']]
        dfpaymentsNAManually.rename(columns={
            'TypedfShopy' : 'Type',
            'Description':'Order',
        }, inplace=True)
        print(dfpaymentsNAManually)

        #Allpayments
        
        dfmergepayments['Deposit Reference Nbr.'] = deposit

        dfmergepayments['Cash Account'] = account
        dfmergepayments['Deposit Date'] = depositdate
        dfmergepayments['Fin. Period'] = period
        dfmergepayments['Payment Method'] = paymentmethod

        dfmergepayments = dfmergepayments[[
            'Deposit Reference Nbr.', 
            'Cash Account', 
            'Deposit Date', 
            'Fin. Period', 
            'Payment Method', 
            'Payment Ref.', 
            'Reference Nbr.'
        ]]

        dfmergepayments['Deposit Date'] = pd.to_datetime(dfmergepayments['Deposit Date'])
        dfmergepayments['Deposit Date'] = dfmergepayments['Deposit Date'].dt.strftime('%m/%d/%Y')
        
        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Dividir dfmergeallpayments en fragmentos de maxrows filas
            total_rows = len(dfmergepayments)
            num_sheets = (total_rows // maxrows) + (1 if total_rows % maxrows != 0 else 0)
            
            for i in range(num_sheets):
                start_row = i * maxrows
                end_row = start_row + maxrows
                sheet_name = f"Sheet1_{i + 1}"
                dfmergepayments.iloc[start_row:end_row].to_excel(writer, sheet_name=sheet_name, index=False)
            
            dfmergerefunds.to_excel(writer, sheet_name='Refunds', index=False)
            dfpaymentsNAManually.to_excel(writer, sheet_name='Missing', index=False)
            

        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': 'attachment; filename="Bank_Deposit_Upload_Shopify.xlsx"'
            }
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error de codificación. Intente guardar los archivos como UTF-8 BOM")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el CSV. Verifique el delimitador (usar coma o punto y coma)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
