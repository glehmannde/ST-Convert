import streamlit as st
import pandas as pd
from collections import defaultdict

# Title of the app
st.title("CSV File Conversion from 'OS Paris' to 'CanoeTrainer'")

# File uploader - allow only one file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv", accept_multiple_files=False)


def convert_time_format(time_str):
    """ Convert time from Minutes:Seconds,Hundredths to Seconds,Hundredths. """
    try:
        minutes, rest = time_str.split(':')
        seconds, hundredths = rest.split('.')
        total_seconds = int(minutes) * 60 + int(seconds)
        return f"{total_seconds},{hundredths}"
    except ValueError:
        return time_str


def convert_df_to_csv(df_conv):
    """ Convert a DataFrame to a CSV string with semicolon as separator and decimal comma. """
    csv_str = df_conv.to_csv(index=False, sep=';')
    return csv_str.replace('.', ',').encode('utf-8')

# Check if a file has been uploaded
if uploaded_file is not None:
    # Read the CSV file into a DataFrame with semicolon as the separator
    df = pd.read_csv(uploaded_file, sep=';')

    # Initialize a list to hold the tab names
    tab_names = ["Original DataFrame"]
    # Initialize a list to hold the DataFrame names
    dfs = [("Original DataFrame", df)]
    # Dictionary to keep count of tab names
    name_count = defaultdict(int)

    # Loop through pairs from 'Speed1', 'Time1' and 'Stroke1' to 'Speed10', 'Time10' and 'Stroke10'
    for i in range(1, 11):
        speed_col = f'Speed{i}'
        stroke_col = f'Stroke{i}'
        time_col = f'Time{i}'
        shortname_col = f'ShortName{i}'

        # Check if both columns exist
        if speed_col in df.columns and stroke_col in df.columns and time_col in df.columns and shortname_col in df.columns:
            # Extract the shortname value for the tab name
            shortname = df[shortname_col].iloc[0] if not df[shortname_col].empty else f"Lane {i}"

            # Count the occurrence of the shortname
            name_count[shortname] += 1
            if name_count[shortname] > 1:
                shortname = f"{shortname}_{name_count[shortname]}"

            # Extract the specified columns to create a new DataFrame
            df_lane = df[['Distance', speed_col, stroke_col, time_col]]
            # Rename the columns
            df_lane.columns = ['Distance', 'Speed', 'Frequency', 'TimeFromStart']
            # Add the new columns with '0' filled
            additional_columns = ['Schlagvortrieb', 'Acceleration', 'Pace', 'HR']
            for col in additional_columns:
                df_lane[col] = '0'

            # Filter out rows where 'Distance' > 1000
            df_lane = df_lane[df_lane['Distance'] <= 1000]

            # Convert the 'TimeFromStart' column format
            df_lane['TimeFromStart'] = df_lane['TimeFromStart'].apply(convert_time_format)

            # Reorder the columns
            ordered_columns = ['Distance', 'Speed', 'Frequency', 'Schlagvortrieb', 'Acceleration', 'Pace', 'HR',
                               'TimeFromStart']
            df_lane = df_lane[ordered_columns]

            # Append the DataFrame to the list
            dfs.append((shortname, df_lane))
            # Append the tab name to the list
            tab_names.append(shortname)

    # Create tabs for each DataFrame
    if dfs:
        tabs = st.tabs(tab_names)
        for tab, (name, df_lane) in zip(tabs, dfs):
            with tab:
                st.write(f"DataFrame: {name}")
                st.dataframe(df_lane)
                if name != "Original DataFrame":
                    csv = convert_df_to_csv(df_lane)
                    st.download_button(
                        label=f"Download {name} as CSV",
                        data=csv,
                        file_name=f"Boat x_600x_data_{name}_OS_2024_Paris.csv",
                        mime='text/csv',
                    )
    else:
        st.write("No lanes with the required columns were found.")
else:
    st.write("Please upload a CSV file.")
