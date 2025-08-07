import pandas as pd
import io
from fastapi.responses import StreamingResponse # pyright: ignore[reportMissingImports]
from fastapi import UploadFile, File, Form, HTTPException # pyright: ignore[reportMissingImports]
import traceback 
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Indenter, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import Color
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np

async def Spec(
        file: UploadFile = File(...),
        weekfront: str = Form(...)
        ):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo no seleccionado")
    # Función para dibujar el fondo
    def draw_cover(canvas, doc):
        week_formatted = weekfront.replace("Week ", "W")
        width, height = doc.pagesize
        canvas.setFillColor(colors.lightgrey)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)

        # Título centrado
        canvas.setFont("Helvetica", 50)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(width / 2, height / 2 + 20, f"W{week_formatted} Spec Check")
        canvas.drawCentredString(width / 2, height / 2 - 35, "Analysis")

    SpecFile = await file.read()
    try:
        #Values
        semana_seleccionada = weekfront
        dfSpec = pd.read_excel(io.BytesIO(SpecFile), engine='openpyxl')
        #Conceptos
        dfSpec.fillna(0, inplace=True)
        totalgc = dfSpec['Qty of GC in order (Cantidad de palos en la orden)'].sum()
        errorsgc = dfSpec['GC with errors  / ¿Cuantos palos con errores se encontraron?'].sum()
        dfSpec['Audit Date (Fecha de inspección)'] = pd.to_datetime(dfSpec['Audit Date (Fecha de inspección)'])
        fechainicio = pd.to_datetime("2025-06-17")
        dfSpec['semana_relativa'] = ((dfSpec['Audit Date (Fecha de inspección)'] - fechainicio).dt.days // 7) + 243
        dfSpec['Week'] = 'Week ' + dfSpec['semana_relativa'].astype(str)
        dfSpec.columns = dfSpec.columns.str.replace('Error type per GC / Tipo de errores por palos de Golf.','')
        dfSpec.rename(columns={
                    'Club   Length': 'Club Length',
                    'Grip   Alignment':'Grip Alignment',
                    'Grip   Length':'Grip Length',
                    'Hosel   Setting':'Hosel Setting',
                    'Shaft   Alignment':'Shaft Alignment',
                    'Shaft   Stepping':'Shaft Stepping',
                    'Swing   Weight':'Swing Weight',
                    'Wood/Putter   Weights':'Wood/Putter Weights'
                    },inplace=True)

        dfSpecWeek = dfSpec[dfSpec['Week'] == f'Week {semana_seleccionada}']

        inspection_columns = ['Components', 'Tipping', 'Hosel Setting', 'Shaft Stepping', 'Wood/Putter Weights',
            'Club Length', 'Shaft Alignment', 'Ferrules', 'Loft', 'Lie',
            'Grip Alignment', 'Grip Length', 'Wraps', 'Swing Weight', 'Cleanliness', 'Boxing']

        # Crear PDF
        output = io.BytesIO()
        doc = SimpleDocTemplate(output)
        styles = getSampleStyleSheet()
        story = []

        story.append(PageBreak())

        # Título
        custom_title_style = ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontName='Helvetica',
            fontSize=22,
            leading=30,
            textColor=colors.black,
            alignment=TA_LEFT,  
        )

        story.append(Paragraph("Report by Golf Clubs", custom_title_style))
        story.append(Spacer(1,6))
        story.append(Paragraph(f"W{semana_seleccionada} by Location: Tequila",  custom_title_style))
        story.append(Spacer(1,12))

        #Tabla de palos
        golfclubs_fail = int(dfSpecWeek['GC with errors  / ¿Cuantos palos con errores se encontraron?'].sum())
        total_golfclubs = int(dfSpecWeek['Qty of GC in order (Cantidad de palos en la orden)'].sum())
        golfclubs_pass = total_golfclubs - golfclubs_fail
        golfclubs_pass_pct = round(golfclubs_pass / total_golfclubs * 100,2)
        golfclubs_fail_pct =  round(golfclubs_fail / total_golfclubs * 100, 2)
        ordenes = [['Orders Audit', 'Quantity', '%'], ['Total', f'{total_golfclubs}', '100%'], ['Pass',f'{golfclubs_pass}',f'{golfclubs_pass_pct}%'], ['Fail', f'{golfclubs_fail}', f'{golfclubs_fail_pct}%']]

        ordenes = Table(ordenes, hAlign='LEFT',colWidths=[80, 75, 75])
        ordenes.setStyle(TableStyle([
            #('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('ALIGN',(0,0),(0,1),'LEFT'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('BOX',(0,0),(-1,-1),1,colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1),0.5,colors.black),
        ]))
        story.append(Indenter(left=10))
        story.append(ordenes)
        story.append(Spacer(1,24))
        story.append(Indenter(left=-10))

        golfclubs_data = []
        for col in inspection_columns:
            golf_clubs_errors = pd.to_numeric(dfSpecWeek[col], errors='coerce').fillna(0).sum()
            golf_clubs_errors = int(round(golf_clubs_errors))
            pct_of_fail = (golf_clubs_errors / golfclubs_fail * 100) if golfclubs_fail > 0 else "NA"
            pct_of_audit = (golf_clubs_errors / total_golfclubs * 100) if total_golfclubs > 0 else "NA"
            golfclubs_data.append([col, golf_clubs_errors, pct_of_fail, pct_of_audit])

        golfclubs_table_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.darkgrey),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('ALIGN',(1,1),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ]
        golfclubs_table_data = [['Spec Type', 'Golf clubs', '%Of Fail', '% Of Audit']]
        for row in golfclubs_data:
            formatted_row = row[:2] + [
                f"{row[2]:.1f}%" if isinstance(row[2], (int, float)) else "NA",
                f"{row[3]:.1f}%" if isinstance(row[3], (int, float)) else "NA"
            ]
            golfclubs_table_data.append(formatted_row)
        # Recorremos las filas para aplicar color condicional
        for i, row in enumerate(golfclubs_data, start=1):  
            value = row[3]
            if value == 'NA':
                bg_color = colors.white
            elif isinstance(value, (int, float)) and 8.0 <= value < 10.0:
                bg_color = Color(0.8, 0.3, 0.3)  
            elif isinstance(value, (int, float)) and 5.0 <= value <= 5.9:
                bg_color = Color(0.8984, 0.4101, 0.4375)
            elif isinstance(value, (int, float)) and 0 <= value <= 4.9:
                bg_color = Color(0.3, 0.7, 0.3) 
            else:
                bg_color = colors.white
            golfclubs_table_style.append(('BACKGROUND', (3, i), (3, i), bg_color))
        
        # Tabla principal
        tbl_golfclubs = Table(golfclubs_table_data, colWidths=[180, 60, 60, 60], repeatRows=1)
        tbl_golfclubs.setStyle(TableStyle(golfclubs_table_style))
        story.append(tbl_golfclubs)

        story.append(PageBreak())

        story.append(Paragraph("Report by Orders", custom_title_style))
        story.append(Spacer(1,6))
        story.append(Paragraph(f"W{semana_seleccionada} by Location: Tequila",  custom_title_style))
        story.append(Spacer(1,12))

        #Tabla pequeña
        #header_table = [['Week', f'W{semana_seleccionada}'], ['Facility', 'Tequila']]

        #tbl_header = Table(header_table, hAlign='LEFT',colWidths=[80, 150])
        #tbl_header.setStyle(TableStyle([
        #    ('BACKGROUND', (0,0), (0,1), colors.grey),
        #    ('ALIGN',(0,0),(0,1),'LEFT'),
        #    ('BACKGROUND', (1,0), (1,1), colors.lightgrey),
        #    ('BOX',(0,0),(-1,-1),1,colors.black),
        #    ('ALIGN',(0,0),(-1,-1),'CENTER'),
        #    ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        #    ('GRID', (0,0), (-1,-1),0.5,colors.black),
        #]))
        #story.append(Indenter(left=10))
        #story.append(tbl_header)
        #story.append(Spacer(1,24))
        #story.append(Indenter(left=-10))

        #Tabla de ordenes
        general_pass = len(dfSpecWeek[dfSpecWeek['Errors found / ¿Se encontraron errores?'] == 'No'])
        general_fail = len(dfSpecWeek[dfSpecWeek['Errors found / ¿Se encontraron errores?'] == 'Si'])
        total_ordenes = general_pass + general_fail
        general_pass_pct = round(general_pass / total_ordenes * 100,2)
        general_fail_pct =  round(general_fail / total_ordenes * 100, 2)
        ordenes = [['Orders Audit', 'Quantity', '%'], ['Total', f'{total_ordenes}', '100%'], ['Pass',f'{general_pass}',f'{general_pass_pct}%'], ['Fail', f'{general_fail}', f'{general_fail_pct}%']]

        ordenes = Table(ordenes, hAlign='LEFT',colWidths=[80, 75, 75])
        ordenes.setStyle(TableStyle([
            #('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('ALIGN',(0,0),(0,1),'LEFT'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('BOX',(0,0),(-1,-1),1,colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1),0.5,colors.black),
        ]))
        story.append(Indenter(left=10))
        story.append(ordenes)
        story.append(Spacer(1,24))
        story.append(Indenter(left=-10))
        #Resumen semanal
        summary_data = []
        for col in inspection_columns:
            dfSpecWeek.loc[:, col] = np.where(dfSpecWeek[col] != 0, 1, 0)
            counts = dfSpecWeek[col].value_counts()
            passed =  counts.get(0,0)
            failed = counts.get(1, 0)
            total = passed + failed
            pct_pass = (passed / total * 100) if total > 0 else "NA"
            pct_fail = (failed / total * 100) if total > 0 else "NA"
            summary_data.append([col, passed, failed, pct_pass, pct_fail])

        table_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.darkgrey),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('ALIGN',(1,1),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ]
        table_data = [['Spec Type', 'PASS', 'FAIL', '% PASS', '% FAIL']]
        for row in summary_data:
            formatted_row = row[:3] + [
                f"{row[3]:.1f}%" if isinstance(row[3], (int, float)) else "NA",
                f"{row[4]:.1f}%" if isinstance(row[4], (int, float)) else "NA"
            ]
            table_data.append(formatted_row)
        # Recorremos las filas para aplicar color condicional
        for i, row in enumerate(summary_data, start=1):  
            value = row[3]
            if value == 'NA':
                bg_color = colors.white
            elif isinstance(value, (int, float)) and 0 <= value < 85:
                bg_color = Color(0.8, 0.3, 0.3)  
            elif isinstance(value, (int, float)) and 86 <= value <= 94:
                bg_color = Color(0.8984, 0.4101, 0.4375)
            elif isinstance(value, (int, float)) and 95 <= value <= 100:
                bg_color = Color(0.3, 0.7, 0.3) 
            else:
                bg_color = colors.white
            table_style.append(('BACKGROUND', (3, i), (3, i), bg_color))
            table_style.append(('BACKGROUND', (4, i), (4, i), bg_color))

        # Tabla principal
        tbl = Table(table_data, colWidths=[180, 60, 60, 60, 60], repeatRows=1)
        tbl.setStyle(TableStyle(table_style))
        story.append(tbl)

        story.append(PageBreak())
        semana_seleccionada = int(semana_seleccionada)
        semanas_interes = [f'Week {w}' for w in range(243, semana_seleccionada + 1)]  
      

        rows_passfail = [
            'Boxing', 'Cleanliness', 'Club Length', 'Ferrules', 'Grip Alignment', 'Grip Length', 'Hosel Setting', 'Lie', 'Loft',
            'Shaft Alignment', 'Shaft Stepping', 'Swing Weight', 'Tipping', 'Wood/Putter Weights', 'Wraps'
        ]
        historical_summary = {}
        for week in semanas_interes:
            df_week = dfSpec[dfSpec['Week'] == week]
            summary_data = []
            for col in rows_passfail:
                df_week.loc[:,col] = np.where(df_week[col] != 0, 1, 0)
                counts = df_week[col].value_counts()
                passed =  counts.get(0,0)
                failed = counts.get(1, 0)
                total = passed + failed
                pct_pass = (passed / total * 100) if total > 0 else None
                pct_fail = (failed / total * 100) if total > 0 else None
                summary_data.append({
                    'inspection': col,
                    'passed': passed,
                    'failed': failed,
                    'pct_pass': pct_pass,
                    'pct_fail': pct_fail
                })
            historical_summary[week] = summary_data

            
        # Crear dataframe vacío con inspecciones como índice
        df_hist = pd.DataFrame(index=rows_passfail)

        passfail_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.darkgrey),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('ALIGN',(1,1),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ]

        def get_gradient_color(pct):
            if pct is None:
                return Color(1, 1, 1)  # blanco
            if pct <= 80:
                return Color(0.8, 0.3, 0.3)  # rojo apagado
            elif pct >= 100:
                return Color(0.3, 0.7, 0.3)  # verde apagado

            # Gradiente manual (entre rojo apagado y verde apagado)
            normalized = (pct - 80) / 20
            r = 0.8 * (1 - normalized) + 0.3 * normalized
            g = 0.3 * (1 - normalized) + 0.7 * normalized
            b = 0.3 * (1 - normalized) + 0.3 * normalized  # constante

            return Color(r, g, b)

        for week in semanas_interes:
            pct_pass_list = []
            for entry in historical_summary[week]:
                pct_pass_list.append(entry['pct_pass'])
            # Agregar columna con porcentaje PASS para esa semana
            df_hist[week] = pct_pass_list

        overtimedata = [['Description'] + list(df_hist.columns)]  # Encabezados

        # Llenar datos + aplicar color
        for row_idx, (inspection, row) in enumerate(df_hist.iterrows(), start=1):
            data_row = [inspection]
            for col_idx, val in enumerate(row, start=1):
                if pd.notnull(val):
                    data_row.append(f"{val:.1f}%")
                    bg_color = get_gradient_color(val)
                    text_color = colors.white if val < 60 else colors.black
                else:
                    data_row.append("")
                    bg_color = colors.white
                    text_color = colors.black
                # Aplicar estilo a celda específica
                passfail_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), bg_color))
                passfail_style.append(('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), text_color))
            overtimedata.append(data_row)

                
        story.append(Paragraph("Pass/Fail over Time by Location: Tequila", custom_title_style))
        story.append(Spacer(1,12))   
        overtimetable = Table(overtimedata, repeatRows= 1)
        overtimetable.setStyle(TableStyle(passfail_style))
        story.append(overtimetable)

        story.append(PageBreak())


        story.append(Paragraph("Loft over time in Tequila", custom_title_style))
        # Extraer solo los valores de 'pct_pass' para Loft
        loft_pass_data = {
            week: next((item['pct_pass'] for item in summary if item['inspection'] == 'Loft'), None)
            for week, summary in historical_summary.items()
        }

        # Crear el dataframe de loft over time
        df_loft_pass = pd.DataFrame({
            'Week': list(loft_pass_data.keys()),
            'Loft_Pass_%': list(loft_pass_data.values())
        }).sort_values('Week')  # Opcional: ordena por semana

        weeks = df_loft_pass['Week'].tolist()
        percentages = df_loft_pass['Loft_Pass_%'].tolist()

        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 6))
        # Dibujar segmentos coloreados
        for i in range(len(weeks) - 1):
            x = [weeks[i], weeks[i + 1]]
            y = [percentages[i], percentages[i + 1]]

            # Color según promedio entre dos puntos
            avg = sum(y) / 2
            if avg >= 90:
                color = 'green'
            elif avg >= 84:
                color = 'orange'
            else:
                color = 'red'

            ax.plot(x, y, color=color, linewidth=2)

        # Agregar puntos y etiquetas
        for week, pct in zip(weeks, percentages):
            ax.scatter(week, pct, color='black')
            ax.text(week, pct + 1.5, f"{pct:.1f}%", ha='center', fontsize=8)

        # Ajustes del gráfico
        ax.set_ylim(0, 105)
        plt.yticks(range(0, 105, 10)) 
        ax.set_ylabel("Pass % →")
        ax.set_title("Spec Check by Loft (Tequila)", loc='left', fontsize=12)
        ax.grid(True, axis='y', linestyle='--', alpha=0.4)

        # Guardar en buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300)
        plt.close()
        img_buffer.seek(0)

        # Insertar la imagen (gráfica)
        story.append(Image(img_buffer, width=500, height=300)) 
        story.append(PageBreak()) 

        #Lie Over time
        story.append(Paragraph("Lie over time in Tequila", custom_title_style))

        # Extraer solo los valores de 'pct_pass' para Lie
        lie_pass_data = {
            week: next((item['pct_pass'] for item in summary if item['inspection'] == 'Lie'), None)
            for week, summary in historical_summary.items()
        }

        #Crear el dataframe de lie over time
        df_lie_pass = pd.DataFrame({
            'Week' : list(lie_pass_data.keys()),
            'Lie_Pass_%' : list(lie_pass_data.values())
        }).sort_values('Week')

        weekslie = df_lie_pass['Week'].tolist()
        percentageslie = df_lie_pass['Lie_Pass_%'].tolist()

        #Crear Figura
        figlie, axlie = plt.subplots(figsize=(12,6))
        for i in range(len(weekslie) - 1):
            x = [weekslie[i], weekslie[i + 1]]
            y = [percentageslie[i], percentageslie[i + 1]]

            # Color según promedio entre dos puntos
            avg = sum(y) / 2
            if avg >= 90:
                color = 'green'
            elif avg >= 84:
                color = 'orange'
            else:
                color = 'red'

            axlie.plot(x, y, color=color, linewidth=2)

        # Agregar puntos y etiquetas
        for weeklie, pctlie in zip(weekslie, percentageslie):
            axlie.scatter(weeklie, pctlie, color='black')
            axlie.text(weeklie, pctlie + 1.5, f"{pctlie:.1f}%", ha='center', fontsize=8)

        # Ajustes del gráfico
        axlie.set_ylim(0, 105)
        plt.yticks(range(0, 105, 10)) 
        axlie.set_ylabel("Pass % →")
        axlie.set_title("Spec Check by Lie (Tequila)", loc='left', fontsize=12)
        axlie.grid(True, axis='y', linestyle='--', alpha=0.4)

        # Crear un buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300)
        plt.close()
        img_buffer.seek(0)

        # Insertar la imagen (gráfica)
        story.append(Image(img_buffer, width=500, height=300)) 
        story.append(PageBreak()) 

        
        # Guardar
        doc.build(story, onFirstPage=draw_cover)
        
            
        # Mover el puntero del buffer al inicio
        output.seek(0)

        return StreamingResponse(
            output,
            media_type='application/pdf',
            headers={
                'content-disposition': f'attachment; filename="Spec_Check_Analysis_W{semana_seleccionada}.pdf"'
            }
        )
        
    except Exception as e:
        tb = traceback.format_exc()
        print("Error inesperado:", str(e))
        print("Traceback completo:")
        print(tb)
        return HTTPException(f"Error procesando el archivo: {str(e)}\n\n{tb}", status=400)