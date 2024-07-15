from fetch_data import fetch_data
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
import numpy as np

def analyse_data(data: pd.DataFrame):
    # print(data)

    grouped = data.groupby('honeypot_name')
    honeypots = {name: group for name, group in grouped}

    # -------------Command Frequency---------------
    for honeypot in honeypots:
        print(honeypot)

        cmd_counts = honeypots[honeypot]['input_cmd'].value_counts()

        plt.figure(figsize=(12, 6))
        bars = cmd_counts.plot(kind='bar')
        plt.title('Frequency of Commands for Honeypot: ' + honeypot)
        plt.xlabel('Command input')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right', fontsize=8)

        plt.yscale('log')

        for bar in bars.patches:
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f'{int(bar.get_height())}', 
                    ha='center', va='bottom', fontsize=6)

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.55)

    # --------------Commands Uniquness--------------

    uniqueness_groups = grouped.agg(
    unique_strings=pd.NamedAgg(column='input_cmd', aggfunc=lambda x: x.nunique()),
    total_strings=pd.NamedAgg(column='input_cmd', aggfunc='size'))   

    uniqueness_groups['unique_to_total_ratio'] = ((uniqueness_groups['unique_strings'] / uniqueness_groups['total_strings']) * 100)

    grouped_sorted = uniqueness_groups.sort_values(by='unique_to_total_ratio')

    plt.figure(figsize=(12, 6))
    bars = plt.barh(grouped_sorted.index, grouped_sorted['unique_to_total_ratio'])
    plt.title('Percentage of Unique Commands to Total Commands by Honeypot Name')
    plt.ylabel('Honeypot Name')
    plt.xlabel('Percentage of Unique/Total Commands')
    plt.xticks(rotation=45, ha='right', fontsize=8)

    for bar in bars:
        plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.2f}%', 
                ha='left', va='center', fontsize=6)

    plt.tight_layout()

    # -------------Average Interaction Time & Count---------------
    for honeypot in honeypots:
        honeypots[honeypot]['time_stamp'] = pd.to_datetime(honeypots[honeypot]['time_stamp'])

        session_times = honeypots[honeypot].groupby('session_id').agg(
            session_start=pd.NamedAgg(column='time_stamp', aggfunc='min'),
            session_end=pd.NamedAgg(column='time_stamp', aggfunc='max'),
            cmd_count=pd.NamedAgg(column='input_cmd', aggfunc='size')
        )

        session_times['session_duration'] = (session_times['session_end'] - session_times['session_start']).dt.total_seconds()

        # Step 4: Calculate the average session duration
        average_session_duration = session_times['session_duration'].mean() # TODO: remove?

         # -------------Average Interaction Time---------------
        counts, bin_edges = np.histogram(session_times['session_duration'], bins=50)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        plt.figure(figsize=(10, 6))  # Set the figure size
        bars = plt.bar(bin_centers, counts, width=(bin_edges[1] - bin_edges[0]), edgecolor='black')

        # Add text on top of each bar
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{count}', 
                    ha='center', va='bottom', fontsize=6)

        plt.title('Histogram of Session Durations for Honeypot: ' + honeypot)  # Set title
        plt.xlabel('Session Duration (seconds)')  # Set x-axis label
        plt.ylabel('Frequency')  # Set y-axis label
        # if max(counts) - min(counts) > 600:
        plt.yscale('log')


         # -------------Average Command Count---------------
        sorted_session_times = session_times.sort_values(by='cmd_count')
        plt.figure(figsize=(12, 6)) 

        unique_counts = sorted_session_times['cmd_count'].value_counts().sort_index()

        plt.bar(unique_counts.index, unique_counts.values)

        # Adding labels for each bar
        for index, value in unique_counts.items():
            plt.text(index, value, str(value), ha='center', va='bottom', fontsize=6)

        plt.title('Counts of Commands per Session for Honeypot: ' + honeypot)  # Set title
        plt.xlabel('Command Count')  # Set x-axis label
        plt.ylabel('Number of Sessions')  # Set y-axis label
        # plt.xticks(rotation=90)  # Rotate x-axis labels for readability (optional)
        plt.tight_layout()  # Adjust layout
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        if max(counts) - min(counts) > 1000:
            plt.yscale('log')
        
        # -------------Sessions per Time---------------
        
        session_times['session_date'] = pd.to_datetime(session_times['session_start']).dt.date

        session_dates = session_times.groupby('session_date').size()

        date_range = pd.date_range(start=session_dates.index.min(), end=session_dates.index.max())


        # Reindex your data with the date range, filling missing values with 0
        session_dates = session_dates.reindex(date_range, fill_value=0)
        session_dates.index = pd.to_datetime(session_dates.index)
        print(session_dates)

        plt.figure(figsize=(10, 6))  # Set the figure size (optional)
        session_dates.plot(kind='bar')  # Plotting the sessions per day as a bar chart
        plt.title('Sessions per Day for Honeypot: ' + honeypot)  # Title of the plot
        plt.xlabel('Date')  # X-axis label
        plt.ylabel('Number of Sessions')  # Y-axis label
        plt.tight_layout()  # Adjust layout to not cut off labels
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        for index, value in enumerate(session_dates):
            plt.text(index, value, str(value), ha='center', va='bottom', fontsize=6)
        if max(counts) - min(counts) > 1000:
            plt.yscale('log')


    for honeypot in honeypots:
        sessions_per_ip = honeypots[honeypot].groupby('src_ip')['session_id'].nunique()

        total_sessions = sessions_per_ip.sum()

        threshold = 0.01 * total_sessions

        # Filter out IPs contributing to less than 3% of the sessions
        significant_sessions_per_ip = sessions_per_ip[sessions_per_ip >= threshold]

        # Calculate the "Other" category by summing sessions from IPs contributing to less than 3%
        other_sessions_count = total_sessions - significant_sessions_per_ip.sum()

        # Append the "Other" category to the significant_sessions_per_ip
        if other_sessions_count > 0:
            significant_sessions_per_ip['Other'] = other_sessions_count

        top_ips = sessions_per_ip.sort_values(ascending=False).head(10)

        # Step 3: Plot the pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(significant_sessions_per_ip, labels=significant_sessions_per_ip.index, autopct=lambda p: '{:.1f}%\n({:.0f})'.format(p, p * total_sessions / 100), startangle=140)
        plt.title('Sessions per IP Address for Honeypot: ' + honeypot)
        # plt.show()
        cell_text = []
        for ip, count in top_ips.items():
            cell_text.append([ip, count])
        table = plt.table(cellText=cell_text, colLabels=['IP Address', 'Session Count'], loc='bottom', cellLoc='center', bbox=[0.0, -0.3, 1.0, 0.3])
        plt.subplots_adjust(left=0.2, bottom=0.25)

    plt.show()


def main():
    # df = fetch_data()
    df = pd.read_csv("data/logs.csv")
    analyse_data(df)


if __name__ == "__main__":
    main()