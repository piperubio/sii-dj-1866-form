import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(
    page_title="Generador DJ 1866 - SII Chile",
    page_icon="⛽",
    layout="wide"
)

def extract_period_from_filename(filename):
    """Extrae año y mes del nombre del archivo formato: *_YYYYMM.xlsx"""
    # Patrón que busca 6 dígitos seguidos antes de .xlsx o .xls al final del nombre
    pattern = r'_(\d{6})(?:\.(xlsx|xls))$'
    match = re.search(pattern, filename)
    if match:
        period = match.group(1)
        year = period[:4]
        month = period[4:6]
        return year, month
    return None, None

def format_rut(rut_str):
    """Formatea RUT y extrae sus componentes (dígitos y dígito verificador)"""
    if pd.isna(rut_str) or str(rut_str).strip() == '':
        return '', ''
    
    # Separar el RUT en componentes: número y dígito verificador
    rut_parts = str(rut_str).split('-')
    if len(rut_parts) == 2:
        # Si hay un guión, tomar la parte antes y después como componentes
        rut_num = re.sub(r'[^0-9]', '', rut_parts[0])
        rut_dv = rut_parts[1].strip().upper()  # Dígito verificador, podría ser un número o K
    else:
        # Si no hay guión, intentar extraer el último dígito como DV
        rut_clean = re.sub(r'[^0-9K]', '', str(rut_str).upper())
        if len(rut_clean) > 1:
            rut_num = rut_clean[:-1]
            rut_dv = rut_clean[-1]
        else:
            rut_num = rut_clean
            rut_dv = ''
    
    # Limitar a 8 dígitos para el RUT y 1 para el DV
    return rut_num[:8], rut_dv[:1]

def format_date_ddmmyyyy(date_obj):
    """Convierte fecha a formato ddmmaaaa"""
    if pd.isna(date_obj):
        return ''
    if isinstance(date_obj, str):
        try:
            date_obj = pd.to_datetime(date_obj)
        except:
            return ''
    return date_obj.strftime('%d%m%Y')

def format_decimal(value, integer_digits=12, decimal_digits=2):
    """Formatea número decimal con punto como separador"""
    if pd.isna(value) or value == '':
        return '0.00'
    try:
        num = float(value)
        return f"{num:.{decimal_digits}f}"
    except:
        return '0.00'

def format_numeric(value, max_digits):
    """Formatea número entero"""
    if pd.isna(value) or value == '':
        return '0'
    try:
        num = int(float(value))
        return str(num)[:max_digits]
    except:
        return '0'

st.title('⛽ Generador CSV para Declaración Jurada 1866 - SII Chile')
st.markdown("**Detalle de las compras de petróleo y sus derivados**")
st.markdown("---")

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📁 Carga de Archivos", "📊 Vista Previa", "💾 Generar CSV"])

with tab1:
    st.header("Carga de Archivos RCV")
    
    # Información sobre el formato esperado
    with st.expander("ℹ️ Información sobre los archivos de entrada"):
        st.markdown("""
        ## 📁 Archivo de entrada
        
        **Nombre del archivo:**
        - Formato: `RCV_COMPRA_REGISTRO_XXXXXXX-X_YYYYMM.xlsx`
        - Donde YYYYMM es el año y mes del registro (ej: 202401 = Enero 2024)
        - Ejemplo: `RCV_COMPRA_REGISTRO_15661465-3_202401.xlsx`
        
        ## 📊 Columnas esperadas
        
        | Columna | Descripción | Formato/Validación |
        |---------|-------------|-------------------|
        | **RUT Proveedor** | RUT con dígito verificador | Formato: 12345678-9 |
        | **Código Otro Impuesto** | Código del documento | ⚠️ Solo registros con valor **28** |
        | **Litros** | Cantidad de Litros adquiridos | Valores numéricos válidos |
        | **Valor Otro Impuesto** | Valor del impuesto específico al petróleo diesel | Monto del IEPD |
        | **Folio** | Número del documento | Identificador único |
        | **Fecha Docto** | Fecha del documento | Formato: dd/mm/aaaa |
        
        ## ⚠️ Consideraciones importantes
        
        - **Filtro automático**: Solo se procesarán registros con `Código Otro Impuesto = 28` (petróleo)
        - **Fecha de registro**: Se extrae del nombre del archivo (YYYYMM al final)
        - **RUT**: Debe incluir dígito verificador con guión
        - **Fecha documento**: Formato día/mes/año con barras
        - **Litros**: Solo registros con valores válidos (no nulos)
        
        ## 📝 Ejemplo de registro válido
        ```
        RUT Proveedor: 15661465-3
        Código Otro Impuesto: 28
        Litros: 1500.50
        Valor Otro Impuesto: 45678
        Folio: 123456
        Fecha Docto: 15/01/2024
        ```
        """)
    
    # Carga múltiple de archivos
    uploaded_files = st.file_uploader(
        "Selecciona los archivos RCV (múltiples archivos permitidos)",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="Puedes seleccionar múltiples archivos RCV de diferentes períodos"
    )
    
    if uploaded_files:
        all_data = []
        file_info = []
        
        st.subheader("📄 Archivos procesados:")
        
        for uploaded_file in uploaded_files:
            try:
                # Extraer período del nombre del archivo
                year, month = extract_period_from_filename(uploaded_file.name)
                
                if not year or not month:
                    st.warning(f"⚠️ No se pudo extraer el período del archivo: {uploaded_file.name}")
                    continue
                
                # Leer archivo Excel
                df = pd.read_excel(uploaded_file)
                
                # Filtrar solo registros con Código Otro Impuesto = 28 (petróleo)
                df_filtered = df[df['Codigo Otro Impuesto'] == 28].copy()
                
                if len(df_filtered) == 0:
                    st.warning(f"⚠️ No se encontraron registros de petróleo en: {uploaded_file.name}")
                    continue
                
                # Filtrar registros con Litros válidos (no nulos)
                df_filtered = df_filtered[df_filtered['Litros'].notna()]
                
                if len(df_filtered) == 0:
                    st.warning(f"⚠️ No se encontraron registros con Litros válidos en: {uploaded_file.name}")
                    continue
                
                # Mapear las columnas al formato requerido para DJ 1866
                df_mapped = pd.DataFrame({
                    'RUT_VENDEDOR': df_filtered['RUT Proveedor'],
                    'PETROLEO_Litros': df_filtered['Litros'],
                    'IEPD': df_filtered['Valor Otro Impuesto'],
                    'TIPO_DOCUMENTO': 2,  # Siempre Factura Electrónica según README
                    'NUMERO_DOCUMENTO': df_filtered['Folio'],
                    'FECHA_DOCUMENTO': df_filtered['Fecha Docto'],
                    'MES_REGISTRO': int(month),
                    'AÑO_REGISTRO': int(year),
                    'ARCHIVO_ORIGEN': uploaded_file.name
                })
                
                all_data.append(df_mapped)
                
                # Mostrar información del archivo procesado
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📁 Archivo", uploaded_file.name[-30:])
                with col2:
                    st.metric("📅 Período", f"{month}/{year}")
                with col3:
                    st.metric("📊 Registros", len(df_mapped))
                with col4:
                    st.metric("⛽ Total Litros", f"{df_mapped['PETROLEO_Litros'].sum():,.0f}")
                
                file_info.append({
                    'archivo': uploaded_file.name,
                    'período': f"{month}/{year}",
                    'registros': len(df_mapped),
                    'Litros': df_mapped['PETROLEO_Litros'].sum()
                })
                
            except Exception as e:
                st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")
        
        if all_data:
            # Combinar todos los datos
            df_combined = pd.concat(all_data, ignore_index=True)
            st.session_state['df_data'] = df_combined
            
            st.success(f"✅ Procesados {len(uploaded_files)} archivos con {len(df_combined)} registros totales")
            
            # Resumen por período
            if len(file_info) > 1:
                st.subheader("📈 Resumen por período:")
                summary_df = pd.DataFrame(file_info)
                st.dataframe(summary_df, use_container_width=True)
        else:
            st.error("❌ No se pudieron procesar los archivos. Verifica el formato y contenido.")

with tab2:
    st.header("Vista Previa de Datos")
    
    if 'df_data' in st.session_state and not st.session_state['df_data'].empty:
        df = st.session_state['df_data']
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Registros", len(df))
        with col2:
            if 'PETROLEO_Litros' in df.columns:
                total_Litros = df['PETROLEO_Litros'].sum()
                st.metric("⛽ Total Litros", f"{total_Litros:,.2f}")
            else:
                st.metric("⛽ Total Litros", "N/A")
        with col3:
            if 'IEPD' in df.columns:
                total_iepd = df['IEPD'].sum()
                st.metric("💰 Total IEPD", f"${total_iepd:,.0f}")
            else:
                st.metric("💰 Total IEPD", "N/A")
        with col4:
            # Mostrar períodos únicos
            if 'AÑO_REGISTRO' in df.columns and 'MES_REGISTRO' in df.columns:
                periodos = df[['MES_REGISTRO', 'AÑO_REGISTRO']].drop_duplicates()
                periodos_str = ", ".join([f"{row['MES_REGISTRO']:02d}/{row['AÑO_REGISTRO']}" for _, row in periodos.iterrows()])
                st.metric("📅 Períodos", periodos_str[:20] + "..." if len(periodos_str) > 20 else periodos_str)
        
        st.markdown("---")
        
        # Tabla de datos con campos relevantes
        st.subheader("📋 Datos Procesados")
        display_cols = ['RUT_VENDEDOR', 'PETROLEO_Litros', 'IEPD', 'NUMERO_DOCUMENTO', 
                       'FECHA_DOCUMENTO', 'MES_REGISTRO', 'AÑO_REGISTRO', 'ARCHIVO_ORIGEN']
        
        if all(col in df.columns for col in display_cols):
            display_df = df[display_cols].copy()
            
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "PETROLEO_Litros": st.column_config.NumberColumn(
                        "Petróleo (Litros)",
                        format="%.2f",
                        min_value=0.0
                    ),
                    "IEPD": st.column_config.NumberColumn(
                        "IEPD",
                        format="%d",
                        min_value=0
                    ),
                    "FECHA_DOCUMENTO": st.column_config.DateColumn(
                        "Fecha Documento",
                        format="YYYY-MM-DD"
                    ),
                    "ARCHIVO_ORIGEN": st.column_config.TextColumn(
                        "Archivo",
                        width="medium"
                    )
                }
            )
            
            # Actualizar session_state con los cambios
            for col in display_cols:
                if col in edited_df.columns:
                    st.session_state['df_data'][col] = edited_df[col]
        else:
            st.dataframe(df, use_container_width=True)
        
        # Botón para limpiar datos
        if st.button("🗑️ Limpiar todos los datos", type="secondary"):
            if 'df_data' in st.session_state:
                del st.session_state['df_data']
            st.rerun()
    
    else:
        st.info("ℹ️ No hay datos cargados. Ve a la pestaña 'Carga de Archivos' para cargar archivos RCV.")

with tab3:
    st.header("Generar Archivo CSV para DJ 1866")
    
    if 'df_data' in st.session_state and not st.session_state['df_data'].empty:
        df = st.session_state['df_data']
        
        # Configuración del archivo de salida
        st.subheader("⚙️ Configuración del Archivo")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("📋 **Formato fijo para SII:**\n- Sin encabezados\n- Separador: punto y coma (;)\n- Codificación: MS-DOS (latin1)\n- Terminaciones de línea: CRLF (\\r\\n)\n- Tipo documento: 2 (Factura Electrónica)")
        
        with col2:
            # Obtener período más común o el primero disponible
            if 'AÑO_REGISTRO' in df.columns and 'MES_REGISTRO' in df.columns:
                year_mode = df['AÑO_REGISTRO'].mode().iloc[0] if not df['AÑO_REGISTRO'].mode().empty else 2024
                month_mode = df['MES_REGISTRO'].mode().iloc[0] if not df['MES_REGISTRO'].mode().empty else 1
                default_name = f"DJ1866_{year_mode}{month_mode:02d}.csv"
            else:
                default_name = "DJ1866.csv"
                
            nombre_archivo = st.text_input(
                "Nombre del archivo",
                value=default_name
            )
        
        # Aplicar formatos específicos según especificaciones SII
        st.subheader("🔧 Procesamiento de Datos")
        
        with st.spinner("Aplicando formatos SII..."):
            # Crear DataFrame de salida con formato SII
            df_output = df.copy()
            
            # C1 y C2: RUT vendedor (parte numérica y dígito verificador)
            # Aplicamos format_rut que ahora retorna una tupla (num_rut, dv_rut)
            rut_components = df_output['RUT_VENDEDOR'].apply(format_rut)
            df_output['C1'] = rut_components.apply(lambda x: x[0])  # Parte numérica del RUT
            df_output['C2'] = rut_components.apply(lambda x: x[1])  # Dígito verificador
            
            # C3: Petróleo adquirido (12,2 decimales)
            df_output['C3'] = df_output['PETROLEO_Litros'].apply(lambda x: format_decimal(x, 12, 2))
            
            # C4: IEPD (15 dígitos numéricos)
            df_output['C4'] = df_output['IEPD'].apply(lambda x: format_numeric(x, 15))
            
            # C5: Tipo de Documento (siempre 2 = Factura Electrónica)
            df_output['C5'] = '2'
            
            # C6: Número de Documento (10 dígitos numéricos)
            df_output['C6'] = df_output['NUMERO_DOCUMENTO'].apply(lambda x: format_numeric(x, 10))
            
            # C7: Fecha del Documento (8 dígitos formato ddmmaaaa)
            df_output['C7'] = df_output['FECHA_DOCUMENTO'].apply(format_date_ddmmyyyy)
            
            # C8: Mes de Registro (2 dígitos numéricos)
            df_output['C8'] = df_output['MES_REGISTRO'].apply(lambda x: f"{int(x):02d}")
            
            # C9: Año de Registro (4 dígitos numéricos)
            df_output['C9'] = df_output['AÑO_REGISTRO'].apply(lambda x: str(int(x)))
        
        # Crear DataFrame final solo con las columnas formateadas
        df_final = df_output[['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']].copy()
        
        # Vista previa del archivo
        st.subheader("👀 Vista Previa del CSV (Formato SII)")
        
        # Mostrar los primeros registros con explicación
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(df_final.head(10), use_container_width=True)
        
        with col2:
            st.markdown("""
            ## 📋 Estructura del Archivo (Formato SII)
            
            | Campo | Descripción | Formato | Ejemplo |
            |-------|-------------|---------|---------|
            | C1 | RUT vendedor | 8 (N) | 12345678 |
            | C2 | RUT Dígito Verificador | 1 (X) | 9 o K |
            | C3 | Petróleo adquirido (litros) | 12,2 (P) | 1500.50 |
            | C4 | IEPD (Impuesto Específico) | 15 (N) | 125000 |
            | C5 | Tipo de Documento | 1 (N) | 2 |
            | C6 | Número de Documento | 10 (N) | 123456789 |
            | C7 | Fecha del Documento | 8 (F) | 15062024 |
            | C8 | Mes de Registro | 2 (N) | 06 |
            | C9 | Año de Registro | 4 (N) | 2024 |
            
            **Formatos:** N=Numérico, X=Alfanumérico, P=Decimal con punto, F=Fecha
            """)
        
        # Generar CSV sin encabezados en formato MS-DOS
        csv_buffer = io.StringIO()
        df_final.to_csv(
            csv_buffer,
            index=False,
            header=False,  # Sin encabezados según especificación SII
            sep=';',       # Separador punto y coma según especificación
            encoding='latin1',  # Codificación compatible con MS-DOS
            line_terminator='\r\n'  # Terminación de línea MS-DOS (CRLF)
        )
        csv_string = csv_buffer.getvalue()
        
        # Validaciones
        st.subheader("✅ Validaciones")
        validaciones = []
        
        # Validar que no hay campos vacíos críticos
        campos_criticos = ['C1', 'C7']  # RUT y fecha son críticos
        for campo in campos_criticos:
            vacios = df_final[campo].isna().sum() + (df_final[campo] == '').sum()
            if vacios > 0:
                validaciones.append(f"❌ {vacios} registros con {campo} vacío")
            else:
                validaciones.append(f"✅ Todos los {campo} completos")
        
        # Validar formatos de fecha
        fechas_invalidas = df_final[df_final['C7'].str.len() != 8]['C7'].count()
        if fechas_invalidas > 0:
            validaciones.append(f"❌ {fechas_invalidas} fechas con formato incorrecto")
        else:
            validaciones.append("✅ Todas las fechas con formato correcto")
        
        # Validar RUTs
        ruts_invalidos = df_final[df_final['C1'].str.len() < 7]['C1'].count()
        if ruts_invalidos > 0:
            validaciones.append(f"❌ {ruts_invalidos} RUTs con formato incorrecto")
        else:
            validaciones.append("✅ Todos los RUTs con formato correcto")
        
        for validacion in validaciones:
            if "❌" in validacion:
                st.error(validacion)
            else:
                st.success(validacion)
        
        # Mostrar ejemplo de línea generada
        if len(df_final) > 0:
            ejemplo_linea = ";".join(df_final.iloc[0].astype(str))
            st.code(f"Ejemplo de línea generada:\n{ejemplo_linea}")
        
        # Botón de descarga
        st.download_button(
            label="📥 Descargar archivo CSV para SII (Formato MS-DOS)",
            data=csv_string.encode('latin1'),  # Codificación compatible con MS-DOS
            file_name=nombre_archivo,
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        
        # Información del archivo
        periodos_info = ""
        if 'AÑO_REGISTRO' in df.columns and 'MES_REGISTRO' in df.columns:
            periodos = df[['MES_REGISTRO', 'AÑO_REGISTRO']].drop_duplicates()
            periodos_list = [f"{row['MES_REGISTRO']:02d}/{row['AÑO_REGISTRO']}" for _, row in periodos.iterrows()]
            periodos_info = ", ".join(periodos_list)
        
        st.info(f"""
        📄 **Información del archivo generado:**
        - Registros: {len(df_final)}
        - Tamaño: {len(csv_string.encode('latin1'))} bytes
        - Formato: Sin encabezados, separador ';'
        - Codificación: MS-DOS (latin1)
        - Terminaciones de línea: CRLF (\\r\\n)
        - Períodos incluidos: {periodos_info}
        - Tipo de documento: 2 (Factura Electrónica)
        """)
        
    else:
        st.warning("⚠️ No hay datos para generar el archivo. Carga archivos RCV en la pestaña 'Carga de Archivos'.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⛽ Generador de CSV para Declaración Jurada 1866 - SII Chile</p>
    <p><small>Detalle de las compras de petróleo y sus derivados</small></p>
    <p><small>Procesamiento automático de archivos RCV - Formato sin encabezados, separador ';'</small></p>
</div>
""", unsafe_allow_html=True)

# Información adicional en sidebar
st.sidebar.markdown("""
### 📖 Información DJ 1866

**Estructura del archivo CSV:**
1. RUT vendedor (8N)
2. Dígito verificador (1X)
3. Petróleo adquirido Litros (12,2P)
4. IEPD (15N)
5. Tipo de documento (1N) = 2
6. Número de documento (10N)
7. Fecha documento (8F ddmmaaaa)
8. Mes de registro (2N)
9. Año de registro (4N)

**Formatos:**
- N = Numérico
- P = Decimal con punto
- F = Fecha ddmmaaaa
- Separador: punto y coma (;)
- Codificación: MS-DOS (latin1)
- Terminaciones de línea: CRLF (\\r\\n)
- Sin encabezados

### 📥 Archivos de entrada esperados

**Formato del nombre:**
- `RCV_COMPRA_REGISTRO_XXXXXXX-X_YYYYMM.xlsx`
- YYYYMM = Año y mes de registro

**Columnas requeridas:**
- **RUT Proveedor**: Con dígito verificador (12345678-9)
- **Código Otro Impuesto**: Solo código 28 (petróleo)
- **Litros**: Cantidad de Litros adquiridos
- **Valor Otro Impuesto**: Monto del IEPD
- **Folio**: Número de documento
- **Fecha Docto**: Formato dd/mm/aaaa

⚠️ **Importante:** Este formato cumple exactamente con las especificaciones técnicas del SII para DJ 1866.
""")
