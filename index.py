import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# Дані
data = {
    "year": [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027],
    "nom_gdp_uah_total_byexp": [5937.143, 5924.972, 7740.73, 7960.907, 9865.014, 11754.332, 13741.219, 16520.025, 19913.083],
    "priv_cons_uah_mln": [2958119, 3094144, 3767172, 3382196, 4191487, 5102641, 6123169, 7347803, 8890842],
    "publ_cons": [746939, 814644, 967099, 2087072, 2725227, 3289418, 3552571, 3765726, 4029327],
    "inv": [700617, 564315, 719771, 621856, 1104704, 1096886, 1369668, 2117607, 2980470],
    "exports_gs": [1639866, 1639060, 2217860, 1857010, 1868904, 2265387, 2695811, 3288889, 4012444],
    "invent": [-108398, -187191, 68828, 12773, -25308, -364215.766, -430601.499, -143625.4334, 130853.4676]
}
df = pd.DataFrame(data)

components = ["priv_cons_uah_mln", "publ_cons", "inv", "exports_gs", "invent"]
years = df["year"].tolist()
n_years = len(years)

# Функція для обчислення CAGR
def calc_cagr(series):
    return (series[-1] / series[0]) ** (1 / (n_years - 1)) - 1

# Центруємо головний графік у вузькому блоці
left, center, right = st.columns([1, 2, 1])
with center:
    st.title("Моделювання ВВП за витратним підходом")
    main_chart_placeholder = st.container()

# Секція слайдерів
st.subheader("Компоненти ВВП (керування темпом зростання)")

cols = st.columns(5)
adjusted_components = {}

for idx, component in enumerate(components):
    col = cols[idx % 5]
    with col:
        st.markdown(f"**{component}**")
        original = df[component].tolist()
        base_rate = calc_cagr(original)
        adj = st.slider(f"{component} (%)", -50.0, 50.0, 0.0, step=1.0, key=component)

        # Моделювання: масштабування кривої + розсіювання
        scaled = []
        lower_bound = []
        upper_bound = []

        for t in range(n_years):
            # base_val = original[t]
            # scaled_val = base_val * (1 + adj / 100)  # вплив повзунка
            # noise = abs(base_val) * 0.03 * t if t > 0 else 0

            if t == 0:
                scaled_val = original[0]
            else:
                # Вираховуємо відхилення від базової точки
                growth_factor = (1 + adj / 100)
                scaled_val = original[0] + (original[t] - original[0]) * growth_factor

            noise = abs(original[t]) * 0.03 * t if t > 0 else 0
            
            scaled.append(scaled_val)
            lower_bound.append(scaled_val - noise)
            upper_bound.append(scaled_val + noise)

        adjusted_components[component] = scaled

        # Малий графік компонента
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        ax.plot(years, scaled, label='Модель', marker='o')
        ax.plot(years, original, label='Факт', linestyle='--', marker='x')
        ax.fill_between(years, lower_bound, upper_bound, color='blue', alpha=0.05,edgecolor='none', label='Невизначеність')
        ax.set_xticks(years[::2])
        ax.set_title(component)

        # 🎨 Стилізація
        ax.set_facecolor('#eee')  # фон фігури
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(axis='x', labelrotation=45, colors='gray')
        ax.tick_params(axis='y', colors='gray')
        ax.title.set_color('black')
        ax.ticklabel_format(style='plain', axis='y')  # без 1e6
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x/1e3):,}'))  # '100 000' замість '100000'

        ax.set_xticks(years[::2])
        legend = ax.legend(fontsize='x-small')
        legend.get_frame().set_facecolor('#f0f0f0') 
        legend.get_frame().set_edgecolor('none')

        st.pyplot(fig)
        

# Перерахунок змодельованого ВВП
recalculated_gdp = [
    sum(adjusted_components[comp][i] for comp in components) / 1000
    for i in range(n_years)
]
true_gdp = df["nom_gdp_uah_total_byexp"].tolist()

# Побудова головного графіка
fig_main, ax_main = plt.subplots(figsize=(8, 3))
ax_main.plot(years, true_gdp, linestyle='--', color='orange', marker='o', label='Факт ВВП')
ax_main.bar(years, recalculated_gdp, label='Модельований ВВП', alpha=0.6, color='#4a90e2')
ax_main.set_ylabel("млрд грн")
ax_main.set_title("Валовий внутрішній продукт (сума змодельованих компонентів)")
ax_main.legend()
main_chart_placeholder.pyplot(fig_main)
