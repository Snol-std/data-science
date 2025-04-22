import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import os



area_mapping = {
        1: 'Вінницька облать', 2: 'Волинська область', 3: 'Дніпропетровська область', 4: 'Донецька область',
        5: 'Житомирська область', 6: 'Закарпатська область', 7: 'Запорізька область', 8: 'Івано-Франківська область',
        9: 'Київська область', 10: 'Кіровоградська область', 11: 'Луганська область', 12: 'Львівська область',
        13: 'Миколаївська область', 14: 'Одеська область', 15: 'Полтавська область', 16: 'Рівненська область',
        17: 'Сумська область', 18: 'Тернопільська область', 19: 'Харківська область', 20: 'Херсонська область',
        21: 'Хмельницька область', 22: 'Черкаська область', 23: 'Чернівецька область', 24: 'Чернігівська область',
        25: 'Крим'
    }


def merge_cleaned_data(dir):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', '-']
    files = os.listdir(dir)
    merged_dataframe = pd.DataFrame()

    for file in files:
        try:
            dataframe = pd.read_csv(os.path.join(dir, file), header=1, names=headers)

            dataframe = dataframe[dataframe["VHI"] != -1]

            dataframe["area_id"] = file.split("_")[2]

            dataframe["area_id"] = pd.to_numeric(dataframe["area_id"], errors="coerce")

            dataframe["Year"] = dataframe["Year"].astype(str).str.replace("<tt><pre>", "", regex=False)

            dataframe = dataframe[~dataframe["Year"].str.contains('</pre></tt>', na=False)]

            dataframe["Year"] = pd.to_numeric(dataframe["Year"], errors="coerce")

            dataframe.drop('-', axis=1, inplace=True, errors="ignore")

            merged_dataframe = pd.concat([merged_dataframe, dataframe], ignore_index=True).drop_duplicates()

        except Exception as e:
            print(f"[Error] in processing file {file}: {e}")

    merged_dataframe["area_id"] = merged_dataframe["area_id"].astype(int)
    merged_dataframe = merged_dataframe.sort_values(by=["area_id", "Year", "Week"]).reset_index(drop=True)

    return merged_dataframe

dataframe = merge_cleaned_data("C:/Users/User/PycharmProjects/PythonProject/Da/lab2/CSVs")

defaults = {
    "index": "VHI",
    "region": list(area_mapping.values())[3],
    "week_range": (1, 25),
    "year_range": (1991, 2014),
    "sort_asc": False,
    "sort_desc": False,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if st.button("Скинути фільтри"):
    for key, val in defaults.items():
        st.session_state[key] = val
    st.rerun()

col1, col2 = st.columns([1, 3])

with col1:
    st.session_state.index = st.selectbox("Індекс:", ["VCI", "TCI", "VHI"],
                                          index=["VCI", "TCI", "VHI"].index(st.session_state.index))
    st.session_state.region = st.selectbox("Область:", list(area_mapping.values()),
                                                index=list(area_mapping.values()).index(st.session_state.region))
    st.session_state.week_range = st.slider("Інтервал тижнів:", 1, 52, st.session_state.week_range)
    st.session_state.year_range = st.slider("Інтервал років:", int(dataframe["Year"].min()), int(dataframe["Year"].max()),
                                            st.session_state.year_range)
    st.session_state.sort_asc = st.checkbox("Сортувати за зростанням", value=st.session_state.sort_asc)
    st.session_state.sort_desc = st.checkbox("Сортувати за спаданням", value=st.session_state.sort_desc)

    if st.session_state.sort_asc and st.session_state.sort_desc:
        st.warning("Виберіть лише одне сортування.")

with col2:
    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік 1", "Графік 2"])

    for key, value in area_mapping.items():
        if value == st.session_state.region:
            region_id = key
            break

    filtered = dataframe[
        (dataframe["area_id"] == region_id) &
        (dataframe["Week"].between(*st.session_state.week_range)) &
        (dataframe["Year"].between(*st.session_state.year_range))
        ][["Year", "Week", st.session_state.index, "area_id"]]

    if st.session_state.sort_asc: # зростання
        filtered = filtered.sort_values(by=st.session_state.index, ascending=True)
    elif st.session_state.sort_desc: # спадання
        filtered = filtered.sort_values(by=st.session_state.index, ascending=False)

    with tab1:
        st.dataframe(filtered)

    with tab2:

        avg_by_week = filtered.groupby("Week")[st.session_state.index].mean().reset_index()
        plt.figure(figsize=(8, 4))
        sns.lineplot(data=avg_by_week, x="Week", y=st.session_state.index, marker="o")
        plt.title(f"Середнє значення {st.session_state.index} по тижнях у {st.session_state.region}")
        plt.xlabel("Тиждень")
        plt.ylabel(st.session_state.index)
        plt.grid(True)
        st.pyplot(plt.gcf())

    with tab3:
        filtered_2 = dataframe[
            (dataframe["Week"].between(*st.session_state.week_range)) &
            (dataframe["Year"].between(*st.session_state.year_range))
            ]
        
        plt.figure(figsize=(8, 4))
        filtered_2["region"] = filtered_2["area_id"].map(area_mapping)

        sns.boxplot(data=filtered_2, x="region", y=st.session_state.index)
        plt.xticks(rotation=90)
        plt.title(f"Графік порівняння {st.session_state.index} по всіх областях")
        plt.xlabel("Область")
        plt.ylabel(st.session_state.index)
        st.pyplot(plt.gcf())