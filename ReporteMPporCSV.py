import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de Ventas - Mercadopago")

# Subida del archivo CSV
uploaded_file = st.file_uploader("Sube un archivo CSV de reporte de ventas de Mercadopago", type="csv")

if uploaded_file is not None:
    try:
        # Leer el archivo CSV
        df = pd.read_csv(uploaded_file, encoding="utf-8")

        # Mostrar la vista previa inicial
        st.subheader("Vista previa del archivo original:")
        st.dataframe(df.head())

        # Validar que las columnas necesarias existan
        required_columns = [
            "Fecha de compra (date_created)",
            "Tipo de operación (operation_type)",
            "Monto recibido (net_received_amount)"
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Faltan las siguientes columnas requeridas: {', '.join(missing_columns)}")
            st.stop()

        # Filtrar filas donde "Tipo de operación" sea "regular_payment"
        filtered_df = df[df["Tipo de operación (operation_type)"] == "regular_payment"]

        # Convertir las columnas a tipos apropiados
        filtered_df["Monto recibido (net_received_amount)"] = pd.to_numeric(
            filtered_df["Monto recibido (net_received_amount)"], errors="coerce"
        )
        filtered_df["Fecha de compra (date_created)"] = pd.to_datetime(
            filtered_df["Fecha de compra (date_created)"], errors="coerce"
        )

        # Filtrar filas válidas después de la conversión
        filtered_df = filtered_df.dropna(subset=["Fecha de compra (date_created)", "Monto recibido (net_received_amount)"])

        # Agrupar por fecha y sumar los montos recibidos
        grouped_data = (
            filtered_df.groupby(filtered_df["Fecha de compra (date_created)"].dt.date)["Monto recibido (net_received_amount)"]
            .sum()
            .reset_index()
        )
        grouped_data.columns = ["Fecha", "Suma de Monto Recibido"]

        # Mostrar los datos agrupados
        st.subheader("Datos agrupados por fecha:")
        if grouped_data.empty:
            st.warning("No se encontraron datos válidos después del procesamiento.")
        else:
            st.dataframe(grouped_data)

            # Descargar los datos agrupados
            grouped_csv = grouped_data.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Descargar CSV Agrupado por Fecha",
                data=grouped_csv,
                file_name="suma_por_fecha.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
