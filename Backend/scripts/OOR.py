import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, HTTPException # pyright: ignore[reportMissingImports]
import traceback

async def OOR(
    file: UploadFile = File(...),          # ACMA (Excel)
    file2: UploadFile = File(...)   
    ):
    if not file.filename or not file2.filename:
        raise HTTPException(status_code=400, detail="Debe proporcionar ambos archivos")

    try:
        
        # Leer contenido de los archivos
        OORexcelfile = await file.read()
        openordersfile = await file2.read()

        # Procesar OOR (Excel) - Versión robusta
        OORexcel = pd.read_excel(io.BytesIO(OORexcelfile), engine='openpyxl', sheet_name='Open Orders ')
        promised_date_column = OORexcel.columns[13]
        columnasOORexcel = ['PO Number', 'Line Number', 'Material Sku', 'PO Qty', 'Current Unit Price','Ship to', 'Shipping Origin','MOT']
        columnasseleccionar = columnasOORexcel + [promised_date_column]
        OORexcel = OORexcel[columnasseleccionar]
        #OORexcel = OORexcel[OORexcel['PO Number'] != 'PO Number']
        OORexcel = OORexcel.rename(columns={promised_date_column: 'Shipped Date'})
        
        OORexcel['Shipped Date'] = pd.to_datetime(OORexcel['Shipped Date'], errors='coerce').dt.date
        OORexcel['Day'] = pd.to_datetime(OORexcel['Shipped Date'], errors='coerce').dt.day_name()

        openorders = pd.read_csv(io.BytesIO(openordersfile),encoding='utf-16', sep='\t')       
        openorders = openorders.rename(columns={'Order Nbr': 'PO Number', 
                                        'Line Nbr': 'Line Number', 
                                        'Inventory CD': 'Material Sku', 
                                        'Order Qty': 'PO Qty', 
                                        'Avg. UnitCostUSD': 'Current Unit Price'})
        
        openorders = openorders[['PO Number', 'Line Number', 'Material Sku', 'PO Qty', 'Current Unit Price','Promised Date']]
        openorders['Promised Date'] = pd.to_datetime(openorders['Promised Date'], errors='coerce').dt.date
        openorders['Day'] = pd.to_datetime(openorders['Promised Date'], errors='coerce').dt.day_name()
        
        #Trabajo de fechas
                #MOT US
        usof = 40
        usaf = 14
        uspafe = 7
        usfbvn = 31
        usfbcn = 25

        #MOT UK
        ukof = 50
        ukaf = 14
        ukpafe = 7

        #MOTJP
        jpof = 14
        jpaf = 10
        jppafe = 7

        #MOT DISTRIBUTION
        dist= 0

        OORexcel['CONCAT'] = OORexcel['Shipping Origin'].astype(str) + '-' + OORexcel['Ship to'].astype(str) + '-' + OORexcel['MOT'].astype(str)

        mapeo_dias = {
            # MOT US
            'China-USA-FBLCL': usfbcn,
            'Vietnam-USA-FBLCL': usfbvn, 
            'China-USA-Ocean': usof,
            'Vietnam-USA-Ocean': usof,
            'China-USA-AF': usaf,
            'Vietnam-USA-AF': usaf,
            'China-USA-Fedex IE': uspafe,
            'Vietnam-USA-Fedex IE': uspafe,
            'China-USA-FedEx IE': uspafe,
            'Vietnam-USA-FedEx IE': uspafe,

            # MOT UK
            'China-UK-Ocean': ukof,
            'Vietnam-UK-Ocean': ukof,
            'China-UK-AF': ukaf,
            'Vietnam-UK-AF': ukaf,
            'China-UK-FedEx IE': ukpafe,
            'Vietnam-UK-FedEx IE': ukpafe, 
            'China-UK-Fedex IE': uspafe,
            'Vietnam-UK-Fedex IE': uspafe, 
    
            # MOT JP 
            'China-JP-Ocean': jpof,
            'Vietnam-JP-Ocean': jpof,
            'China-JP-AF': jpaf,
            'Vietnam-JP-AF': jpaf,
            'China-JP-FedEx IE': jppafe,
            'Vietnam-JP-FedEx IE': jppafe,
            'China-JP-Fedex IE': uspafe,
            'Vietnam-JP-Fedex IE': uspafe,

            # MOT DISTRIBUTION
            'DIST': dist
        }
        # Aplicar mapeo: los valores no encontrados usan dist (0)
        OORexcel['Dias_a_Sumar'] = OORexcel['CONCAT'].map(mapeo_dias).fillna(dist)

        # Calcular nueva fecha
        OORexcel['Shipped Date'] = pd.to_datetime(OORexcel['Shipped Date'])
        OORexcel['Nueva_Fecha'] = OORexcel['Shipped Date'] + pd.to_timedelta(OORexcel['Dias_a_Sumar'], unit='D')

        #OORexcel = OORexcel[OORexcel['PO Number'] != 'PO Number']
        OORexcel['Day'] = OORexcel['Nueva_Fecha'].dt.day_name()

        #Suma por dias
        sat= 6
        sun= 5
        mon= 4
        tue= 3
        wed= 2
        thu= 1
        fri= 0

        mapeo_dias_semana = {
            'Saturday': sat,
            'Sunday': sun,
            'Monday': mon,
            'Tuesday': tue,
            'Wednesday': wed,
            'Thursday': thu,
            'Friday': fri
        }

        OORexcel['Dias_a_Sumar_Semana'] = OORexcel['Day'].map(mapeo_dias_semana).fillna(0)
        OORexcel['Promised Date'] = OORexcel['Nueva_Fecha'] + pd.to_timedelta(OORexcel['Dias_a_Sumar_Semana'], unit='D')
        OORexcel['New_Day'] = OORexcel['Promised Date'].dt.day_name()

        openorders['Material Sku'] = (
            openorders['Material Sku']
            .fillna('')
            .astype(str)
            .str.strip()
        )

        openorders['PO Qty'] = (
            openorders['PO Qty']
            .fillna('')
            .astype(str)
            .str.replace(',', '', regex=False)
        )

        openorders['PO Qty'] = pd.to_numeric(
            openorders['PO Qty'],
            errors='coerce'
        )

        OORexcel = OORexcel[OORexcel['PO Number'] != 'PO Number']

        OORexcel.loc[OORexcel['Material Sku'] == 'T-Tip Weights 4', ['Material Sku']] = 'T-TIPWEIGHT-4G'
        OORexcel.loc[OORexcel['Material Sku'] == 'T-Tip Weights 8', ['Material Sku']] = 'T-TIPWEIGHT-8G'


        OORexcel = OORexcel.sort_values(['PO Number', 'Line Number'])
        openorders = openorders.sort_values(['PO Number', 'Line Number'])

        po_depure1 = openorders[~openorders['PO Number'].isin(OORexcel['PO Number'])]
        ordenes_cerradas = po_depure1.copy()
        lista_ordenes_cerradas = ordenes_cerradas['PO Number'].unique().tolist()
        #print(f"PO ordenes cerradas: {lista_ordenes_cerradas}")

        po_depure2 = OORexcel[~OORexcel['PO Number'].isin(openorders['PO Number'])]
        nuevas_ordenes = po_depure2.copy()
        lista_ordenes_nuevas = nuevas_ordenes['PO Number'].unique().tolist()
        #print(f"PO ordenes nuevas: {lista_ordenes_nuevas}")

        openorders = openorders[openorders['PO Number'].isin(OORexcel['PO Number'])].copy()
        OORexcel = OORexcel[OORexcel['PO Number'].isin(openorders['PO Number'])].copy()

        #print(f"PO únicos originales en openorders: {openorders['PO Number'].nunique()}")
        #print(f"PO únicos originales en OORexcel: {OORexcel['PO Number'].nunique()}")

        # 1. Obtener la frecuencia de cada PO Number en ambos dataframes
        frecuencia_openorders = openorders['PO Number'].value_counts().reset_index()
        frecuencia_openorders.columns = ['PO Number', 'frecuencia_openorders']

        frecuencia_OORexcel = OORexcel['PO Number'].value_counts().reset_index()
        frecuencia_OORexcel.columns = ['PO Number', 'frecuencia_OORexcel']

        # 2. Combinar las frecuencias
        comparacion = frecuencia_openorders.merge(frecuencia_OORexcel, on='PO Number', how='outer').fillna(0)

        # 3. Identificar los PO que NO tienen la misma frecuencia
        comparacion['misma_frecuencia'] = comparacion['frecuencia_openorders'] == comparacion['frecuencia_OORexcel']

        # 4. Separar en dos grupos
        po_con_diferencia = comparacion[~comparacion['misma_frecuencia']].copy()
        po_sin_diferencia = comparacion[comparacion['misma_frecuencia']].copy()

        # 5. Extraer los registros completos de openorders para los PO con diferencia
        df_diferencia = openorders[openorders['PO Number'].isin(po_con_diferencia['PO Number'])].copy()

        # 6. Opcional: también extraer los de OORexcel
        df_diferencia_OORexcel = OORexcel[OORexcel['PO Number'].isin(po_con_diferencia['PO Number'])].copy()

        mayor_en_openorders = po_con_diferencia[po_con_diferencia['frecuencia_openorders'] > po_con_diferencia['frecuencia_OORexcel']].copy()
        mayor_en_OORexcel = po_con_diferencia[po_con_diferencia['frecuencia_OORexcel'] > po_con_diferencia['frecuencia_openorders']].copy()

        mayor_en_openorders = mayor_en_openorders[['PO Number', 'frecuencia_openorders', 'frecuencia_OORexcel']]
        mayor_en_openorders = mayor_en_openorders.rename(columns={'frecuencia_openorders': 'Acumatica Lines', 'frecuencia_OORexcel': 'OOR Lines'})

        split_lines = mayor_en_OORexcel[['PO Number', 'frecuencia_openorders', 'frecuencia_OORexcel']]
        split_lines = split_lines.rename(columns={'frecuencia_openorders': 'Acumatica Lines', 'frecuencia_OORexcel': 'OOR Lines'})

        openorders = openorders[~openorders['PO Number'].isin(mayor_en_openorders['PO Number'])].copy() #REVISAR
        openorders = openorders[~openorders['PO Number'].isin(split_lines['PO Number'])].copy()

        OORexcel = OORexcel[~OORexcel['PO Number'].isin(mayor_en_openorders['PO Number'])].copy()
        OORexcel = OORexcel[~OORexcel['PO Number'].isin(split_lines['PO Number'])].copy()

        #COMPARACION DE DATOS
        openorders_reset = openorders.reset_index(drop=True)
        OORexcel_reset = OORexcel.reset_index(drop=True)

        #Redondear a dos decimales para igualar formatos
        openorders_reset['Current Unit Price'] = pd.to_numeric(
            openorders_reset['Current Unit Price'],
            errors='coerce'
        ).round(2)

        OORexcel_reset['Current Unit Price'] = pd.to_numeric(
            OORexcel_reset['Current Unit Price'],
            errors='coerce'
        ).round(2)

        # Crear un identificador de fila
        openorders_reset['fila_id'] = openorders_reset.index
        OORexcel_reset['fila_id'] = OORexcel_reset.index

        # Hacer merge (equivalente a juntar lado a lado)
        df_comparado = openorders_reset.merge(OORexcel_reset, 
                                            on='fila_id', 
                                        suffixes=('_openorders', '_OORexcel'))

        # Crear indicadores de igualdad columna por columna
        for col in openorders_reset.columns:
            if col != 'fila_id':  # Excluir el ID
                col_df1 = f'{col}_openorders'
                col_df2 = f'{col}_OORexcel'
                df_comparado[f'{col}_igual'] = df_comparado[col_df1] == df_comparado[col_df2]

        #excel = df_comparado.to_excel('comparacion_final.xlsx', index=False)

        # Diccionario para almacenar los dataframes de diferencias
        dfs_diferencias = {}

        # Lista de columnas que estás comparando
        columnas_comparadas = ['PO Number', 'Line Number', 'Material Sku', 'PO Qty', 'Current Unit Price', 'Promised Date']

        # Crear un dataframe por cada columna que tenga diferencias
        for col in columnas_comparadas:
            col_igual = f'{col}_igual'
            
            # Filtrar filas donde esta columna específica es FALSA (diferente)
            mask = df_comparado[col_igual] == False
            
            if mask.any():  # Si hay al menos una diferencia
                # Crear dataframe con las filas donde hay diferencia
                df_temp = df_comparado[mask].copy()
                
                # Seleccionar columnas relevantes para este análisis
                columnas_interes = ['Line Number_openorders',
                                    'PO Number_openorders',
                                    'Material Sku_openorders',
                                f'{col}_openorders', 
                                f'{col}_OORexcel', 
                                col_igual]
                
                df_temp = df_temp[columnas_interes]
                
                # Renombrar para mayor claridad
                df_temp.columns = ['Line Number', 
                                'PO Number',
                                'Material Sku',
                                f'{col}_acumatica', 
                                f'{col}_OOR', 
                                'difference']
                
                # Guardar en el diccionario
                dfs_diferencias[col] = df_temp
                
                #print(f"✅ {col}: {len(df_temp)} filas con diferencias")
            else:
                print("No hay diferencias")

        # Acceder a cada dataframe individualmente
        df_diff_po = dfs_diferencias.get('PO Number')
        df_diff_line = dfs_diferencias.get('Line Number')
        df_diff_material = dfs_diferencias.get('Material Sku')
        df_diff_qty = dfs_diferencias.get('PO Qty')
        df_diff_precio = dfs_diferencias.get('Current Unit Price')
        if isinstance(lista_ordenes_nuevas, list):
            df_ordenes_nuevas = pd.DataFrame({'PO Number': lista_ordenes_nuevas})
        else:
            df_ordenes_nuevas = lista_ordenes_nuevas

        if isinstance(lista_ordenes_cerradas, list):
            df_ordenes_cerradas = pd.DataFrame({'PO Number': lista_ordenes_cerradas})
        else:
            df_ordenes_cerradas = lista_ordenes_cerradas

        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Agregar hojas de diferencias
            for nombre_columna, df in dfs_diferencias.items():
                if df is not None and len(df) > 0:
                    nombre_hoja = nombre_columna.replace(' ', '_').replace('/', '_')
                    df.to_excel(writer, sheet_name=nombre_hoja, index=False)
                    print(f"✅ Hoja '{nombre_hoja}' agregada ({len(df)} filas)")
            
            # Agregar hoja de Órdenes Nuevas
            if df_ordenes_nuevas is not None and len(df_ordenes_nuevas) > 0:
                df_ordenes_nuevas.to_excel(writer, sheet_name='Ordenes_Cerradas', index=False)
                #print(f"✅ Hoja 'Ordenes_Nuevas' agregada ({len(df_ordenes_nuevas)} filas)")
            else:
                pd.DataFrame({'Mensaje': ['No hay órdenes nuevas']}).to_excel(writer, sheet_name='Closed_Orders', index=False)
                #print(f"ℹ️ Hoja 'Ordenes_Nuevas' creada (sin datos)")
            
            # Agregar hoja de Órdenes Cerradas
            if df_ordenes_cerradas is not None and len(df_ordenes_cerradas) > 0:
                df_ordenes_cerradas.to_excel(writer, sheet_name='Faltantes_OOR', index=False)
                #print(f"✅ Hoja 'Ordenes_Cerradas' agregada ({len(df_ordenes_cerradas)} filas)")
            else:
                pd.DataFrame({'Mensaje': ['No hay órdenes cerradas']}).to_excel(writer, sheet_name='Missing_OOR', index=False)
                #print(f"ℹ️ Hoja 'Ordenes_Cerradas' creada (sin datos)")
    
                    

        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': 'attachment; filename="OOR_Validation.xlsx"'
            }
        )
    except Exception as e:
        traceback.print_exc()

        print("========== ERROR ==========")
        print(type(e))
        print(repr(e))
        print(str(e))
        print("===========================")

        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error de codificación.")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el US Chase.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")