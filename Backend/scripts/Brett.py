import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, HTTPException # pyright: ignore[reportMissingImports]

async def Brett(
        file: UploadFile = File(...)
        ):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Debe proporcionar ambos archivos")
    
    try:
        archivo_excel = await file.read()
        def unir_hojas_excel(archivo_excel, hojas_a_ignorar=None, columnas_a_unir=['A', 'B']):
            """
            Une todas las hojas de un archivo Excel en un solo DataFrame,
            ignorando hojas específicas.
            
            Parámetros:
            -----------
            archivo_excel : str
                Ruta del archivo Excel a procesar
            hojas_a_ignorar : list, opcional
                Lista de nombres de hojas a ignorar
            columnas_a_unir : list, opcional
                Lista de columnas a incluir (por defecto ['A', 'B'])
            
            Retorna:
            --------
            DataFrame
                DataFrame con todas las hojas unidas
            """
            
            # Leer el archivo Excel
            xls = pd.ExcelFile(archivo_excel)
            
            # Si no se especifican hojas a ignorar, usar lista vacía
            if hojas_a_ignorar is None:
                hojas_a_ignorar = []
            
            # Lista para almacenar todos los DataFrames
            dataframes = []
            
            # Procesar cada hoja
            for nombre_hoja in xls.sheet_names:
                if nombre_hoja in hojas_a_ignorar:
                    print(f"✓ Ignorando hoja: '{nombre_hoja}'")
                    continue
                
                print(f"✓ Procesando hoja: '{nombre_hoja}'")
                
                # Leer la hoja completa
                try:
                    # Leer todas las columnas primero
                    df_temp = pd.read_excel(xls, sheet_name=nombre_hoja)
                    
                    # Verificar si el DataFrame tiene datos
                    if df_temp.empty:
                        print(f"  - Advertencia: Hoja '{nombre_hoja}' está vacía")
                        continue
                    
                    # Convertir nombres de columnas a letras si son numéricas
                    # Esto es útil cuando las columnas no tienen nombre de cabecera
                    mapeo_columnas = {}
                    for i, col in enumerate(df_temp.columns):
                        if isinstance(col, int) or (isinstance(col, str) and col.isdigit()):
                            # Convertir índice numérico a letra de Excel (A=0, B=1, etc.)
                            letra_col = chr(65 + int(col))
                            mapeo_columnas[col] = letra_col
                        else:
                            mapeo_columnas[col] = str(col)
                    
                    # Renombrar columnas si es necesario
                    df_temp = df_temp.rename(columns=mapeo_columnas)
                    
                    # Filtrar solo las columnas especificadas
                    columnas_disponibles = [col for col in columnas_a_unir if col in df_temp.columns]
                    
                    if not columnas_disponibles:
                        print(f"  - Advertencia: No se encontraron las columnas {columnas_a_unir} en la hoja '{nombre_hoja}'")
                        # Tomar las primeras 2 columnas disponibles
                        columnas_disponibles = df_temp.columns[:2].tolist()
                        print(f"  - Usando columnas: {columnas_disponibles}")
                    
                    # Crear un nuevo DataFrame con las columnas seleccionadas
                    df_filtrado = df_temp[columnas_disponibles].copy()
                    
                    # Añadir columna con el nombre de la hoja
                    df_filtrado['Sheet name'] = nombre_hoja
                    
                    # Añadir a la lista
                    dataframes.append(df_filtrado)
                    
                    # Mostrar información de la hoja procesada
                    print(f"  - Filas: {len(df_filtrado)}, Columnas: {len(df_filtrado.columns)}")
                    
                except Exception as e:
                    print(f"  - Error procesando hoja '{nombre_hoja}': {e}")
            
            # Unir todos los DataFrames
            if dataframes:
                df_final = pd.concat(dataframes, ignore_index=True)
                return df_final
            else:
                print("\nNo se procesaron datos. Verifica las hojas y columnas.")
                return pd.DataFrame()

        hojas_a_ignorar = ['Stock', 'MASTER']  # Hojas a omitir
        columnas = ['A', 'B']  # Columnas a unir

        # 3. Ejecutar la función
        df_unificado = unir_hojas_excel(
            archivo_excel=archivo_excel,
            hojas_a_ignorar=hojas_a_ignorar,
            columnas_a_unir=columnas
        )

        # Create an Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_unificado.to_excel(writer, sheet_name='Master', index=False)
            

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