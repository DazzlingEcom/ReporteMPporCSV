import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de Reportes de Ventas - MercadoPago")

# Subida del archivo CSV
uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

if uploaded_file is not None:
    try:
        # Leer el archivo CSV con el separador y codificación adecuada
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8', on_bad_lines='skip')

        # Mostrar columnas detectadas
        st.write("Columnas detectadas en el archivo:")
        st.write(df.columns.tolist())

        # Renombrar columnas si tienen espacios adicionales
        df.columns = df.columns.str.strip()

        # Validar columnas requeridas
        required_columns = [
            "Fecha de compra (date_created)",
            "Tipo de operación (operation_type)",
            "Monto recibido (net_received_amount)"
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Faltan las siguientes columnas requeridas: {missing_columns}")
            st.stop()

        # Filtrar las filas donde el tipo de operación sea "regular_payment"
        filtered_df = df[df["Tipo de operación (operation_type)"] == "regular_payment"]

        # Convertir la columna de fecha a formato datetime
        filtered_df["Fecha de compra (date_created)"] = pd.to_datetime(
            filtered_df["Fecha de compra (date_created)"], errors="coerce", format='%d/%m/%Y %H:%M:%S'
        )

        # Convertir la columna de monto recibido a numérico
        filtered_df["Monto recibido (net_received_amount)"] = pd.to_numeric(
            filtered_df["Monto recibido (net_received_amount)"], errors="coerce"
        )

        # Agrupar por fecha y sumar los valores netos
        grouped_df = (
            filtered_df.groupby(filtered_df["Fecha de compra (date_created)"].dt.date)["Monto recibido (net_received_amount)"]
            .sum()
            .reset_index()
        )
        grouped_df.columns = ["Fecha de compra", "Suma de Monto Recibido"]

        # Mostrar los datos procesados
        st.subheader("Datos agrupados por fecha (solo regular_payment):")
        st.dataframe(grouped_df)

        # Descargar los datos agrupados
        csv = grouped_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV Agrupado",
            data=csv,
            file_name='ventas_agrupadas.csv',
            mime='text/csv'
        )
    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
