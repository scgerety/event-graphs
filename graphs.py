#!python3
"""graphs.py
Makes stacked bar graphs of likert-scale data. This is custom made for Leadership Development Institute program reports.
"""

import pandas as pd
import plot_likert
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib as mpl
import textwrap

pathname = f"{os.path.abspath(os.path.dirname(__file__))}\\"
filename = "SurveyExport.csv"
corrections = "Corrections.csv"
# In this iteration, we're using the filename_dict to loop over three events.
filename_dict = {
    "2025UndergraduateSummit.csv": "UndergradCorrections.csv",
    "FallSeminar2025.csv": "FallCorrections.csv",
    "ISeval2025.csv": "ISCorrections.csv"
}

def main(df, pathname, filename, corrections):
    correction_df = setup_correction_df(pathname, corrections)
    event_name = filename.replace(".csv", "")
    df = correct_session_names(df, correction_df)
    df = clean_columns(df)
    df = df.loc[:,"Speaker":]
    df = df.fillna("na")
    session_list = [i for i in df["session"] if i is not None]
    session_list = set(session_list)
    setup_folder(pathname, event_name)
    for session in session_list:
        session_plot(session, df, event_name)
        print(session)
    summary = session_scores(df, session_list, event_name)
    plot_scores(summary, pathname, event_name)

def setup_folder(pathname, event_name):
    os.makedirs(f"{pathname}{event_name}Graphs", exist_ok=True)

def setup_correction_df(pathname, corrections):
    session_corrections = pd.read_csv(
        f"{pathname}{corrections}",
        header=0
        )
    return session_corrections

def load_files(pathname, filename):
    df = pd.read_csv(
        f"{pathname}{filename}",
        header=1,
        skiprows=[2]
    )
    return df

def clean_columns(session_data):
    session_data = session_data.rename(columns={
        "Please rate [Field-speaker]'s presentation.": "Speaker",
        "I found [Field-session] engaging.": "Engaging",
        "The information presented in the session was relevant to my future work.": "Relevant",
        "I enjoyed attending [Field-session].": "Enjoyable",
        "I found the session informative.": "Informative",
        "I can implement what I learned in practice.": "Implementable",
        "I plan to use what I have learned in [Field-session] in my current or future projects.": "Useful"
        })
    return session_data

def correct_session_names(df, session_corrections):
    for ind in session_corrections.index:
        df = df.replace(f"{session_corrections['Session List'][ind]}", f"{session_corrections['Session Name'][ind]}")
        return df

# Create a function that cycles through session names and creates likert scale
# graphs for all questions.
def session_plot(session_name, session_data, event_name):
    # Set up scale
    agree_scale = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
    # Rename columns with session_name
    session_data = session_data.query("session == @session_name")
    # Select those columns
    session_data = session_data[[
        "Engaging",
        "Relevant",
        "Enjoyable",
        "Informative",
        "Implementable",
        "Useful"
    ]]

    #session_data = plot_likert.likert_counts(session_data, agree_scale)    

    #Plot graph
    session_data_fig = plot_likert.plot_likert(
        session_data.round(0),
        agree_scale,
        bar_labels=False,
        plot_percentage=True,
        title=session_name,
        colors=plot_likert.colors.default_with_darker_neutral
    )
    # Attach bar labels with 1 decimal
    for bars in session_data_fig.containers[1:]:
        labels = session_data_fig.bar_label(
            bars,
            label_type="center",
            fmt='%.1f%%',
            color='snow',
            family='sans',
            weight='bold'
        )

        # Remove labels that don't fit because the bars are too small
        # (Sampled from plot-likert library)
        for label in labels:
            label_text = label.get_text()
            number = round(float(label_text.rstrip("%")), 0)
            if number == 0:
                label.set_text("")

    # Remove ugly axes
    session_data_fig.get_xaxis(
        ).set_visible(False)
    for key, spine in session_data_fig.spines.items():
        spine.set_visible(False)
    # Save
    session_data_fig.get_figure().savefig(f"{pathname}{event_name}Graphs\\{session_name} session ratings.png",
                                          bbox_inches="tight")
def session_scores(df, session_list):
    agreement_values = {
        "Strongly Agree": 2,
        "Agree": 1,
        "Neutral": 0,
        "Disagree": -1,
        "Strongly Disagree": -2
    }
    rating_values = {
        "Very Good": 2,
        "Good": 1,
        "Average": 0,
        "Poor": -1,
        "Very Poor": -2
    }
    for keys, values in agreement_values.items():
        df = df.replace(keys, values)
    for keys, values in rating_values.items():
        df = df.replace(keys, values)
    df = df.drop(columns=["Please provide any additional comments you would like to add here.","speaker"])
    df = df.groupby(by="session")
    averages = df.mean()
    return averages

def plot_scores(summary, pathname, event_name):
    for col in summary.columns:
        summary = summary.sort_values(col)
        x = np.array(["\n".join(textwrap.wrap(label, 20)) for label in summary.index])
        y = summary[f"{col}"]
        fig, ax = plt.subplots()
        ax.barh(x, y)
        mpl.rcParams["font.size"] = 5
        plt.tight_layout()
        fig.savefig(f"{pathname}{event_name}Graphs\\{col}.png", format="png")

if __name__ == "__main__":
    for survey_filename, correction_filename in filename_dict.items():
        correction_df = setup_correction_df(pathname, correction_filename)
        df = load_files(pathname, survey_filename)
        main(df, pathname, survey_filename, correction_df)
