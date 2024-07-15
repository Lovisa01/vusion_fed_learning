from BlueLLMTeam.database.db_interaction import fetch_all_session_logs
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
import numpy as np


def plot_cmd_frequency(cmd_counts, honeypot):
    plt.figure(figsize=(12, 6))
    bars = cmd_counts.plot(kind='bar')
    plt.title('Frequency of Commands for Honeypot: ' + honeypot)
    plt.xlabel('Command input')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right', fontsize=8)

    if max(cmd_counts) - min(cmd_counts) > 1000:
        plt.yscale('log')

    for bar in bars.patches:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f'{int(bar.get_height())}', 
                ha='center', va='bottom', fontsize=6)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.55)


def plot_cmd_uniqueness(uniqueness_groups):
    grouped_sorted = uniqueness_groups.sort_values(by='unique_to_total_ratio')

    print("###################")
    print(grouped_sorted)
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

def get_sessions_data(honeypots):
    all_hp_sessions = {}
    for honeypot in honeypots:
        honeypots[honeypot]['time_stamp'] = pd.to_datetime(honeypots[honeypot]['time_stamp'])
        session_times = honeypots[honeypot].groupby('session_id').agg(
            session_start=pd.NamedAgg(column='time_stamp', aggfunc='min'),
            session_end=pd.NamedAgg(column='time_stamp', aggfunc='max'),
            cmd_count=pd.NamedAgg(column='input_cmd', aggfunc='size')
        )
        session_times['session_duration'] = (session_times['session_end'] - session_times['session_start']).dt.total_seconds()
        session_times['session_date'] = pd.to_datetime(session_times['session_start']).dt.date

        all_hp_sessions[honeypot] = session_times
    
    return all_hp_sessions


def plot_sessions_per_day(honeypot_sessions):
    all_dates = pd.date_range(start=min(min(s['session_date']) for s in honeypot_sessions.values()), end=max(max(s['session_date']) for s in honeypot_sessions.values()))
    
    honeypot_sessions_dates = {}
    for honeypot in honeypot_sessions:
        honeypot_sessions_dates[honeypot] = honeypot_sessions[honeypot].groupby('session_date').size()
        honeypot_sessions_dates[honeypot] = honeypot_sessions_dates[honeypot].reindex(all_dates, fill_value=0)

    honeypot_sessions_dates = pd.DataFrame(honeypot_sessions_dates)
    bars = honeypot_sessions_dates.plot(kind='bar', figsize=(10, 6))
    plt.title('Sessions per Day for All Honeypots')
    plt.xlabel('Date')
    plt.ylabel('Number of Sessions')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.xticks([i for i in range(0, len(all_dates))], [all_dates[i].strftime('%m-%d') for i in range(0, len(all_dates))])
    
    if honeypot_sessions_dates.max().max() - honeypot_sessions_dates.min().min() > 1000:
        plt.yscale('log') 
    
    for bar in bars.patches:
        if bar.get_height() > 0:
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f'{int(bar.get_height())}', 
                    ha='center', va='bottom', fontsize=6)


def plot_top_commands(honeypots, top_n=15):
    top_commands = []
    for honeypot, data in honeypots.items():
        top = data['input_cmd'].value_counts().head(top_n).reset_index()
        top.columns = ['Command', 'Frequency']
        top['Honeypot'] = honeypot
        top_commands.append(top)

    df = pd.concat(top_commands, ignore_index=True)

    plt.figure(figsize=(10, 6))
    for honeypot in df['Honeypot'].unique():
        subset = df[df['Honeypot'] == honeypot].reset_index(drop=True)
        subset['Frequency'] = subset['Frequency'] / honeypots[honeypot]['input_cmd'].size
        plt.plot(subset.index+1, subset['Frequency'], marker='o', label=honeypot)
    
    plt.xticks(rotation=0, ha="right")
    plt.ylabel('Frequency')
    plt.xlabel('Command')
    plt.title('Top Commands by Frequency for Each Honeypot')
    plt.legend()
    plt.tight_layout()

def analyse_data(data: pd.DataFrame):

    # Divide the data into groups based on the honeypot name
    grouped = data.groupby('honeypot_name')
    honeypots = {name: group for name, group in grouped}

    # -------------Command Frequency---------------
    cmd_frequency = {}
    for honeypot in honeypots:
        cmd_frequency[honeypot] = honeypots[honeypot]['input_cmd'].value_counts()
        plot_cmd_frequency(cmd_frequency[honeypot], honeypot)
        
    # -----------Commands Frequency Combined---------
    plot_top_commands(honeypots)

    # --------------Commands Uniquness--------------

    uniqueness_groups = grouped.agg(
    unique_strings=pd.NamedAgg(column='input_cmd', aggfunc=lambda x: x.nunique()),
    total_strings=pd.NamedAgg(column='input_cmd', aggfunc='size'))   

    uniqueness_groups['unique_to_total_ratio'] = ((uniqueness_groups['unique_strings'] / uniqueness_groups['total_strings']) * 100)

    plot_cmd_uniqueness(uniqueness_groups)
    
    # --------------Sessions Data--------------
    session_times = get_sessions_data(honeypots)
    # -------------Average Interaction Time---------------
    for honeypot in honeypots:
        honeypots[honeypot]['time_stamp'] = pd.to_datetime(honeypots[honeypot]['time_stamp'])

        counts, bin_edges = np.histogram(session_times[honeypot]['session_duration'], bins=50)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        plt.figure(figsize=(10, 6))  
        bars = plt.bar(bin_centers, counts, width=(bin_edges[1] - bin_edges[0]), edgecolor='black')

        # Add text on top of each bar
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{count}', 
                    ha='center', va='bottom', fontsize=6)

        plt.title('Histogram of Session Durations for Honeypot: ' + honeypot)  
        plt.xlabel('Session Duration (seconds)')  
        plt.ylabel('Frequency')  
        if max(counts) - min(counts) > 1000:
            plt.yscale('log')

    
    # -------------Average Command Count---------------
    sorted_session_times = {}
    cmd_counts = {}
    for honeypot in honeypots:
        sorted_session_times[honeypot] = session_times[honeypot].sort_values(by='cmd_count')
        cmd_counts[honeypot] = sorted_session_times[honeypot]['cmd_count'].value_counts().sort_index()

    cmd_counts = pd.DataFrame(cmd_counts)
    min_cmd_count = cmd_counts.index.min()
    max_cmd_count = cmd_counts.index.max()

    complete_index = range(min_cmd_count, max_cmd_count + 1)
    
    cmd_counts = cmd_counts.reindex(complete_index, fill_value=0)

    bars = cmd_counts.plot(kind='bar', figsize=(12, 6))
    plt.title('Counts of Commands per Session for All Honeypots')  
    plt.xlabel('Command Count')  
    plt.ylabel('Number of Sessions')  
    plt.xticks(rotation=0)  
    plt.tight_layout()  
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    if cmd_counts.max().max() - cmd_counts.min().min() > 1000:
        plt.yscale('log') 

    for bar in bars.patches:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f'{int(bar.get_height())}', 
                ha='center', va='bottom', fontsize=6)

    # -------------Sessions per Time---------------
    plot_sessions_per_day(session_times)
    

    # -------------Sessions per IP---------------
    num_honeypots = len(honeypots)
    fig, axes = plt.subplots(1, num_honeypots, figsize=(8 * num_honeypots, 8))  

    for index, (honeypot, data) in enumerate(honeypots.items()):
        sessions_per_ip = data.groupby('src_ip')['session_id'].nunique()
        total_sessions = sessions_per_ip.sum()
        threshold = 0.01 * total_sessions
        significant_sessions_per_ip = sessions_per_ip[sessions_per_ip >= threshold]
        other_sessions_count = total_sessions - significant_sessions_per_ip.sum()

        if other_sessions_count > 0:
            significant_sessions_per_ip['Other'] = other_sessions_count

        top_ips = sessions_per_ip.sort_values(ascending=False).head(10)

        ax = axes[index] if num_honeypots > 1 else axes  
        ax.pie(significant_sessions_per_ip, labels=significant_sessions_per_ip.index, autopct=lambda p: '{:.1f}%\n({:.0f})'.format(p, p * total_sessions / 100), startangle=140)
        ax.set_title('Sessions per IP Address for Honeypot: ' + honeypot)
        cell_text = []
        for ip, count in top_ips.items():
            cell_text.append([ip, count])
        table = ax.table(cellText=cell_text, colLabels=['IP Address', 'Session Count'], loc='bottom', cellLoc='center', bbox=[0.0, -0.3, 1.0, 0.3])
        table.set_fontsize(8)
        plt.subplots_adjust(left=0.2, bottom=0.25)


    # -------------Session length stacked barh plot---------------
    print(session_times['cowrie-default'], session_times['cowrie-default'].size, len(session_times['cowrie-default']))
    def categorize_cmd_count(x):
        if x >= 10:
            return '10+'
        else:
            return str(x)
    
    for honeypot in session_times:
        session_times[honeypot]['cmd_count_category'] = session_times[honeypot]['cmd_count'].apply(categorize_cmd_count)
    print(session_times)
    total_sessions = {}
    category_percentages = {}
    for honeypot in session_times:
        total_sessions[honeypot] = len(session_times[honeypot])
        category_percentages[honeypot] = session_times[honeypot]['cmd_count_category'].value_counts(normalize=True).sort_index()

    categories = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10+']
    category_percentages = pd.DataFrame(category_percentages)
    print(total_sessions)
    print(category_percentages)

    category_percentages.plot(kind='bar', stacked=True, figsize=(10, 6))
    
   
    plt.show()


def main():
    # df = fetch_all_session_logs()
    df = pd.read_csv("data/logs.csv")
    analyse_data(df)


if __name__ == "__main__":
    main()