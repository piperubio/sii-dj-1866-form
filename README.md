# Generador CSV para Declaración Jurada 1866 - SII Chile

Una aplicación web desarrollada con Streamlit para facilitar la creación de archivos CSV de carga masiva para la **Declaración Jurada 1866** del Servicio de Impuestos Internos (SII) de Chile, específicamente para el **detalle de las compras de petróleo y sus derivados**.

## 🚀 Características

- **Interfaz intuitiva**: Aplicación web fácil de usar con pestañas organizadas
- **Formato exacto SII**: Cumple con las especificaciones técnicas oficiales (AT2020 en adelante)
- **Procesamiento automático de archivos RCV**:
  - Carga múltiple de archivos Excel RCV (.xlsx, .xls)
  - Extracción automática del período desde el nombre del archivo
  - Filtrado automático por Código Otro Impuesto = 28 (petróleo)
- **Editor de datos**: Tabla interactiva para editar y revisar la información
- **Validaciones automáticas**: Verificación de formatos y datos requeridos
- **Información detallada**: Guías completas sobre formato de archivos de entrada
- **Generación exacta**: CSV sin encabezados, separador ';' según especificaciones SII
- **Resumen por período**: Vista consolidada de múltiples archivos procesados

## 📋 Estructura del Archivo (Formato SII)

La DJ 1866 requiere los siguientes 8 campos en orden específico:

| Campo | Descripción | Formato | Ejemplo |
|-------|-------------|---------|---------|
| C1 | RUT vendedor | 8 (N) | 12345678 |
| C2 | RUT Dígito Verificador | 1 (N) | 9 |
| C3 | Petróleo adquirido (litros) | 12,2 (P) | 1500.50 |
| C4 | IEPD (Impuesto Específico) | 15 (N) | 125000 |
| C5 | Tipo de Documento | 1 (N) | 2 |
| C6 | Número de Documento | 10 (N) | 123456789 |
| C7 | Fecha del Documento | 8 (F) | 15062024 |
| C8 | Mes de Registro | 2 (N) | 06 |
| C9 | Año de Registro | 4 (N) | 2024 |

**Códigos de formato:**
- **N** = Numérico
- **P** = Numérico con decimales (punto como separador)
- **F** = Fecha (formato ddmmaaaa)

## 🛠️ Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:
   ```bash
   pip install -e .
   ```
   
   O usando uv:
   ```bash
   uv sync
   ```

## ▶️ Uso

1. Ejecuta la aplicación:
   ```bash
   streamlit run main.py
   ```

2. Abre tu navegador en `http://localhost:8502`

3. Carga los archivos RCV en la pestaña "Carga de Archivos":
   - Selecciona uno o múltiples archivos con formato `RCV_COMPRA_REGISTRO_XXXXXXX-X_YYYYMM.xlsx`
   - El período (año y mes) se extrae automáticamente del nombre del archivo
   - Solo se procesan registros con Código Otro Impuesto = 28 (petróleo)
   - La aplicación muestra métricas de cada archivo procesado
   - Resumen consolidado de múltiples períodos si se cargan varios archivos

4. Revisa los datos procesados en la pestaña "Vista Previa":
   - Editor de datos interactivo para modificar registros
   - Métricas de resumen (total registros, litros, IEPD, períodos)
   - Validación visual de datos antes de generar el archivo final

5. Genera y descarga el archivo CSV en la pestaña "Generar CSV":
   - Aplicación automática de formatos según especificaciones SII
   - Vista previa del archivo generado
   - Validaciones de integridad de datos
   - Descarga directa del archivo en formato requerido por el SII

## 📥 Archivos de Entrada Esperados

### Formato del Nombre del Archivo
- **Patrón**: `RCV_COMPRA_REGISTRO_XXXXXXX-X_YYYYMM.xlsx`
- **Donde**: 
  - `YYYYMM`: Año y mes del registro (ej: 202401 = Enero 2024)
- **Ejemplo**: `RCV_COMPRA_REGISTRO_15661465-3_202401.xlsx`

### Columnas Requeridas en el Archivo

| Columna | Descripción | Formato/Validación |
|---------|-------------|-------------------|
| **RUT Proveedor** | RUT con dígito verificador | Formato: 12345678-9 |
| **Código Otro Impuesto** | Código del documento | ⚠️ Solo registros con valor **28** |
| **Litros** | Cantidad de litros adquiridos | Valores numéricos válidos |
| **Valor Otro Impuesto** | Valor del impuesto específico al petróleo diesel | Monto del IEPD |
| **Folio** | Número del documento | Identificador único |
| **Fecha Docto** | Fecha del documento | Formato: dd/mm/aaaa |

### Consideraciones Importantes
- **Filtro automático**: Solo se procesarán registros con `Código Otro Impuesto = 28` (petróleo)
- **Fecha de registro**: Se extrae del nombre del archivo (YYYYMM al final)
- **RUT**: Debe incluir dígito verificador con guión
- **Fecha documento**: Formato día/mes/año con barras
- **Litros**: Solo registros con valores válidos (no nulos)

### Ejemplo de Registro Válido
```
RUT Proveedor: 12345678-9
Código Otro Impuesto: 28
Litros: 1500.50
Valor Otro Impuesto: 45678
Folio: 123456
Fecha Docto: 15/01/2024
```

## 📄 Tipos de Documento

| Código | Descripción |
|--------|-------------|
| 2 | Factura Electrónica (Hay más tipos pero siempre es del tipo Factura Electrónica) |

## 📊 Ejemplo de Salida

```
12345678;9;3997.0;606631;2;3184450;31122023;01;2024
12345678;9;3612.0;467828;2;3190498;16012024;01;2024
```

**Características del archivo generado:**
- Sin encabezados (títulos de columna)
- Separador: punto y coma (;)
- Codificación: UTF-8
- Fechas en formato ddmmaaaa
- Decimales con punto (.)
- Tipo de documento: siempre 2 (Factura Electrónica)

## 📁 Archivos de Ejemplo

El proyecto incluye información detallada sobre el formato esperado de archivos RCV directamente en la interfaz de la aplicación, con ejemplos de registros válidos y guías completas de formato.

## ✅ Validaciones Incluidas

- **Verificación de RUT vendedor**: Formato correcto (8 dígitos numéricos)
- **Validación de formato de fecha**: ddmmaaaa según especificaciones SII
- **Control de campos obligatorios**: Verificación de campos críticos no vacíos
- **Formato correcto de números decimales**: Punto como separador decimal
- **Longitud máxima de campos**: Según especificaciones SII
- **Filtrado automático**: Solo registros con Código Otro Impuesto = 28
- **Validación de archivos**: Verificación de estructura y contenido de archivos RCV
- **Integridad de datos**: Control de valores nulos en campos críticos (RUT, fechas)
- **Consistencia de períodos**: Extracción y validación del período desde nombre de archivo

## ⚠️ Importante

- Este formato cumple exactamente con las especificaciones técnicas del SII para DJ 1866 (AT2020 en adelante)
- El archivo generado está listo para ser cargado directamente en el sistema del SII
- La aplicación procesa automáticamente archivos RCV con filtrado por Código Otro Impuesto = 28
- Solo se incluyen registros con datos válidos (litros no nulos, fechas correctas)
- El período de registro se extrae automáticamente del nombre del archivo
- Siempre verifica que tus datos sean correctos antes de presentar la declaración

## 🔧 Tecnologías Utilizadas

- [Streamlit](https://streamlit.io/) - Framework de aplicaciones web
- [Pandas](https://pandas.pydata.org/) - Manipulación de datos
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Lectura de archivos Excel
- [NumPy](https://numpy.org/) - Computación numérica

## 📝 Especificaciones Técnicas SII

La aplicación implementa el formato **F1866 AT2020 en adelante (Formato Simple)** según las especificaciones del SII:

- **Separador de campos**: punto y coma (;)
- **Sin encabezados** en la primera línea
- **Formatos específicos** por campo (N, P, F)
- **Longitudes máximas** definidas por el SII
- **Tipo de documento**: siempre 2 (Factura Electrónica)
- **Filtrado automático**: solo registros de petróleo (código 28)
- **Extracción de período**: automática desde nombre de archivo RCV
- **Validaciones de integridad**: según especificaciones técnicas oficiales

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes preguntas o necesitas ayuda, por favor abre un issue en este repositorio.