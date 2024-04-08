from pathlib import Path

import pandas as pd
import seaborn as sns

from shiny import reactive, App, Inputs, Outputs, Session
from shiny.express import input, render, ui

sns.set_theme(style="white")

# Load dataset
food_df = pd.read_csv(Path(__file__).parent / "final_data.csv", na_values="NA")
person_df = pd.read_csv(Path(__file__).parent / "egperson.csv", na_values="NA")
df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
species = ["Adelie", "Gentoo", "Chinstrap"]

#ui.page_opts(fillable=True)


def count_species(df, species):
    return df[df["Species"] == species].shape[0]


with ui.sidebar():
    ui.input_slider("mass", "Mass", 2000, 6000, 3400)
    ui.input_checkbox_group("species", "Filter by species", species, selected=species)


@reactive.calc
def filtered_df() -> pd.DataFrame:
    filt_df = df[df["Species"].isin(input.species())]
    filt_df = filt_df.loc[filt_df["Body Mass (g)"] > input.mass()]
    return filt_df

with ui.layout_columns():
    with ui.value_box(theme="primary"):
        "About"

        @render.text
        def adelie_count():
            return "This is our AI and Society final project dashboard."

    with ui.value_box(theme="primary"):
        "Value"

        @render.text
        def gentoo_count():
            return "Below: an interactive data grid based on an ingredient data set, an interactive plot to depict a user's nutrients over time, and a filler example graph that changes based on the sidebar"

    with ui.value_box(theme="primary"):
        "Us"

        @render.text
        def chinstrap_count():
            return "Brigid, Anna, Andrew, Brian"


with ui.layout_columns():
    with ui.card():
        ui.card_header("Summary statistics")

        @render.data_frame
        def summary_statistics():
            display_df = food_df[
                [
                    "Categories", 
                    "Description", 
                    "Potassium",
                ]
            ]
            '''
            display_df = filtered_df()[
                [
                    "Species",
                    "Island",
                    "Bill Length (mm)",
                    "Bill Depth (mm)",
                    "Body Mass (g)",
                ]
            ]
            '''
            return render.DataGrid(display_df, filters=True)

    #allow user to select a nutrient and display a graph of people's nutrient intake over time
    with ui.card():
        ui.card_header("Person statistics")
        
        #radio button to select nutrient
        nutrient_unique_list = pd.Series(person_df["nutrient"]).drop_duplicates().tolist()
        ui.input_radio_buttons("nutrient", "Nutrient", nutrient_unique_list)

        @render.plot
        def person_statistics():
            display_person_df = person_df[
                [
                    "name", 
                    "date", 
                    "nutrient",
                    "grams",
                ]
            ]

            #graph specific to chosen nutrient
            nutrient = input.nutrient()
            display_person_df = display_person_df[display_person_df['nutrient'] == nutrient]
            person_wide = display_person_df.pivot(index="date", columns="name", values="grams")

            # Plot using Seaborn
            axs = sns.lineplot(data=person_wide)
            axs.set(xlabel='Date', ylabel='Grams of ' + nutrient, title=nutrient + ' Intake Over Time')
            return axs

    with ui.card():
        ui.card_header("Penguin bills")

        @render.plot
        def length_depth():
            return sns.scatterplot(
                data=filtered_df(),
                x="Bill Length (mm)",
                y="Bill Depth (mm)",
                hue="Species",
            )