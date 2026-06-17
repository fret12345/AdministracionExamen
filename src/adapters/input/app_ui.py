import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.use_cases.get_financial_data import ObtenerDatosSiboifUseCase

@st.cache_data(show_spinner="Cargando datos de Siboif...")
def load_data_from_use_case(_use_case: ObtenerDatosSiboifUseCase):
    records, es_fallback = _use_case.ejecutar()
    if not records:
        return pd.DataFrame(), es_fallback
    
    # Convertir entidades de dominio (Pydantic models) a DataFrame
    data_list = [r.model_dump() for r in records]
    df = pd.DataFrame(data_list)
    
    # Asegurar el tipado correcto requerido para los filtros y cálculos de app.py original
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['valor1'] = pd.to_numeric(df['valor1'], errors='coerce').fillna(0)
    return df, es_fallback

def render_ui(use_case: ObtenerDatosSiboifUseCase):
    # Configuración inicial de la página
    st.set_page_config(
        page_title="Dashboard SIBOIF Analytics",
        page_icon=":material/account_balance:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Estilos CSS modernos con animaciones y hovers premium
    st.markdown("""
        <style>
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            h1, h2, h3 {
                color: #4A90E2 !important;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
            }
            .metric-card {
                background: linear-gradient(145deg, #1E2530, #13171F);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 4px 4px 10px #090B0E, -4px -4px 10px #232D3C;
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 6px 6px 15px #090B0E, -6px -6px 15px #232D3C;
            }
            .metric-title {
                font-size: 1.1rem;
                color: #8C98A8;
                margin-bottom: 10px;
            }
            .metric-value {
                font-size: 2rem;
                color: #4CAF50;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    # Invocar al caso de uso con caché de Streamlit
    df, es_fallback = load_data_from_use_case(use_case)

    if not df.empty:
        st.title(":material/account_balance: SIBOIF Analytics: Inteligencia Financiera")
        
        # Aviso sutil e interactivo indicando que el fallback está activo (Modo Offline)
        if es_fallback:
            st.warning("Modo Offline: Datos locales de Siboif.db", icon=":material/wifi_off:")
            
        st.markdown("Explora de forma **interactiva** y dinámica los indicadores del 2018.")
        
        # --- BARRA LATERAL ---
        with st.sidebar:
            st.header(":material/tune: Controles Interactivos")
            
            meses_disponibles = sorted(df['Mes'].dropna().unique())
            opciones_mes = ["Todos"] + list(meses_disponibles)
            mes_seleccionado = st.select_slider(":material/calendar_month: Desliza el Mes:", options=opciones_mes)
            
            tipos_institucion_disponibles = df['tipo_institucion'].dropna().unique()
            tipo_seleccionado = st.multiselect(":material/domain: Filtrar Tipo Institución:", 
                                               options=list(tipos_institucion_disponibles), 
                                               default=list(tipos_institucion_disponibles)[:3] if len(tipos_institucion_disponibles)>0 else None)
            
            # Filtro extra por monto
            st.markdown("### :material/payments: Filtro Avanzado")
            min_valor = st.number_input("Valor mínimo a considerar:", min_value=0.0, value=0.0, step=1000000.0)

        # Filtrar datos localmente usando pandas en memoria
        df_filtrado = df.copy()
        if mes_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Mes'] == mes_seleccionado]
        if tipo_seleccionado:
            df_filtrado = df_filtrado[df_filtrado['tipo_institucion'].isin(tipo_seleccionado)]
        if min_valor > 0:
            df_filtrado = df_filtrado[df_filtrado['valor1'] >= min_valor]

        variables_destacadas = ['Activos', 'Pasivos', 'Cartera de Créditos, Neta', 'Depósitos del Público', 'Patrimonio']
        top_variables = df[df['variable1'].isin(variables_destacadas)]['variable1'].unique()

        # Helpers
        def format_currency(num):
            return f"$ {num:,.2f}"

        # Tabs de visualizaciones dinámicas
        tab1, tab2, tab3, tab4 = st.tabs([":material/bar_chart: Resumen Global", ":material/compare_arrows: Comparador Bancario", ":material/trending_up: Tendencias Interactivas", ":material/download: Exportar Datos"])
        
        with tab1:
            st.markdown("### Indicadores Principales")
            col1, col2, col3, col4 = st.columns(4)
            
            # Realizar las sumas dinámicas basadas en los registros filtrados
            val_activos = df_filtrado[df_filtrado['variable1'] == 'Activos']['valor1'].sum()
            val_pasivos = df_filtrado[df_filtrado['variable1'] == 'Pasivos']['valor1'].sum()
            val_patrimonio = df_filtrado[df_filtrado['variable1'] == 'Patrimonio']['valor1'].sum()
            
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>Activos Totales</div><div class='metric-value'>{format_currency(val_activos)}</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>Pasivos Totales</div><div class='metric-value' style='color:#FF5252;'>{format_currency(val_pasivos)}</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>Patrimonio Estimado</div><div class='metric-value' style='color:#FFC107;'>{format_currency(val_patrimonio)}</div></div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>Registros Totales</div><div class='metric-value' style='color:#03A9F4;'>{len(df_filtrado):,}</div></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                df_activos = df_filtrado[df_filtrado['variable1'] == 'Activos'].groupby('institucion', as_index=False)['valor1'].sum()
                if not df_activos.empty:
                    df_activos = df_activos.sort_values(by='valor1', ascending=False).head(10)
                    fig1 = px.pie(df_activos, values='valor1', names='institucion', hole=0.4, 
                                  color_discrete_sequence=px.colors.sequential.Electric, title="Activos por Institución (Top 10)")
                    fig1.update_traces(hoverinfo='label+percent+value', textfont_size=12,
                                       marker=dict(line=dict(color='#0E1117', width=2)))
                    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.warning("Sin datos de activos.")
                    
            with c2:
                if len(top_variables) > 0:
                    df_vars = df_filtrado[df_filtrado['variable1'].isin(top_variables)].groupby('variable1', as_index=False)['valor1'].sum()
                    fig2 = px.bar(df_vars, x='valor1', y='variable1', orientation='h', 
                                  color='valor1', color_continuous_scale='Sunset', title="Distribución de Variables Clave")
                    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            st.markdown("### :material/sports_martial_arts: Comparador uno a uno")
            st.write("Selecciona dos instituciones para comparar sus métricas frente a frente.")
            instituciones_disp = df_filtrado['institucion'].unique()
            if len(instituciones_disp) >= 2:
                cc1, cc2 = st.columns(2)
                with cc1:
                    inst_1 = st.selectbox("Institución A", options=instituciones_disp, index=0)
                with cc2:
                    inst_2 = st.selectbox("Institución B", options=instituciones_disp, index=1 if len(instituciones_disp)>1 else 0)
                    
                df_comp = df_filtrado[df_filtrado['institucion'].isin([inst_1, inst_2])]
                df_comp = df_comp[df_comp['variable1'].isin(top_variables)]
                df_comp_grp = df_comp.groupby(['institucion', 'variable1'], as_index=False)['valor1'].sum()
                
                fig_comp = px.bar(df_comp_grp, x='variable1', y='valor1', color='institucion', barmode='group',
                                  title=f"Comparativa: {inst_1} vs {inst_2}", color_discrete_sequence=['#4CAF50', '#FF5252'])
                fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.info("Necesitas al menos 2 instituciones en la muestra actual para realizar una comparación.")

        with tab3:
            st.markdown("### :material/timeline: Evolución Histórica (Animable y Exploratoria)")
            st.write("Analiza la tendencia de los Activos. Para mayor interactividad, puedes seleccionar con el ratón zonas específicas de la gráfica para hacer zoom.")
            df_tendencia = df[df['tipo_institucion'].isin(tipo_seleccionado)] if tipo_seleccionado else df
            df_tendencia = df_tendencia[df_tendencia['variable1'] == 'Activos'].groupby(['Mes', 'institucion'], as_index=False)['valor1'].sum()
            
            if not df_tendencia.empty:
                top_inst = df_tendencia.groupby('institucion')['valor1'].sum().nlargest(5).index
                df_tendencia_top = df_tendencia[df_tendencia['institucion'].isin(top_inst)]
                
                fig3 = px.line(df_tendencia_top, x='Mes', y='valor1', color='institucion', 
                               markers=True, title='Crecimiento de Activos Mensual (Top 5 en la muestra)')
                fig3.update_traces(line=dict(width=3), marker=dict(size=8, symbol='circle', line=dict(width=2, color='white')))
                fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', hovermode='x unified')
                st.plotly_chart(fig3, use_container_width=True)

        with tab4:
            st.markdown("### :material/table_view: Datos Crudos y Exportación")
            st.write("Explora la tabla interactiva, puedes ordenar según las columnas y luego descargar los datos filtrados en formato CSV para tu propio análisis estadístico.")
            st.dataframe(df_filtrado.head(500), use_container_width=True)
            
            # Botón de descarga
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=":material/file_download: Descargar Datos Filtrados (CSV)",
                data=csv,
                file_name='datos_siboif_filtrados.csv',
                mime='text/csv',
            )

        st.markdown("---")
        st.caption(":material/rocket_launch: Plataforma Interactiva de Análisis | Desarrollada en Streamlit")
    else:
        st.error("No se pudieron cargar los datos de Siboif.")
