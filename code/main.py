#%%
import pandas
import os
import numpy
import matplotlib.pyplot as plt
from time import strptime
from data_handler import intellicage_data, paula_data

#from data_analysis import data_analysis

#%%

# data = intellicage_data()
# visits_df = data.visits_data_frames(to_excel=False)

#%%

class paula_dataa():
    def __init__(self):
        self.file_name_act = "F:/GitHub/intellicage/data_examples_paula/controlDD part1 ale animal01.asc"
        self.file_name_tmp = "F:/GitHub/intellicage/data_examples_paula/controlDD part1 temp animal01.asc"

        file = open(self.file_name_act, 'r')  # We need to re-open the file
        lines = file.readlines()
        lines = [line.strip() for line in lines]	
        file.close()
        self.logfile = lines[0].split("Experiment Logfile:", 1)[1].strip()
        self.description_act = lines[1].split("Experiment Description:", 1)[1].strip()
        self.start_date = lines[3].split("Start Date/Time ", 1)[1].strip()
        self.end_date = strptime(lines[4].split("End Date/Time ", 1)[1].strip(), "%m/%d/%y %H:%M:%S")
        self.animal_id = int(lines[6].split("Animal ID:", 1)[1].strip())
        self.group_id = lines[7].split("Group ID:", 1)[1].strip()
        self.units_measured_act = lines[8].split("Units Measured:", 1)[1].strip()
        self.sampling_interval = lines[9].split("Sampling Interval:", 1)[1].strip()
        self.low_clipping_act = lines[10].split("Low Clipping Limit:", 1)[1].strip()
        self.high_clipping_act = lines[11].split("High Clipping Limit:", 1)[1].strip()
        self.data_string_act = lines[15:]
        self.data_act = [self.data_string_act[sample].split(",", 2) for sample in range(0, len(self.data_string_act))]

        file = open(self.file_name_tmp, 'r')  # We need to re-open the file
        lines = file.readlines()
        lines = [line.strip() for line in lines]	
        file.close()
        if self.logfile != lines[0].split("Experiment Logfile:", 1)[1].strip():
            raise Exception("The temperature file does not match the activity file: LogFile is different")
        self.description_tmp = lines[1].split("Experiment Description:", 1)[1].strip()
        if self.start_date != lines[3].split("Start Date/Time ", 1)[1].strip():
            raise Exception("The temperature file does not match the activity file: Start Date/Time is different")
        if self.end_date != strptime(lines[4].split("End Date/Time ", 1)[1].strip(), "%m/%d/%y %H:%M:%S"):
            raise Exception("The temperature file does not match the activity file: End Date/Time is different")
        if self.animal_id != int(lines[6].split("Animal ID:", 1)[1].strip()):
            raise Exception("The temperature file does not match the activity file: Animal ID is different")
        if self.group_id != lines[7].split("Group ID:", 1)[1].strip():
            raise Exception("The temperature file does not match the activity file: Group ID is different")
        self.units_measured_tmp = lines[8].split("Units Measured:", 1)[1].strip()
        if self.sampling_interval != lines[9].split("Sampling Interval:", 1)[1].strip():
            raise Exception("The temperature file does not match the activity file: Sampling Interval is different")
        self.low_clipping_tmp = lines[10].split("Low Clipping Limit:", 1)[1].strip()
        self.high_clipping_tmp = lines[11].split("High Clipping Limit:", 1)[1].strip()
        
        self.data_string_tmp = lines[15:]
        self.data_tmp = [self.data_string_tmp[sample].split(",", 2) for sample in range(0, len(self.data_string_tmp))]

        self.data_act = pandas.DataFrame(self.data_act, columns=["Date", "Time", "Activity"])
        self.data_act = self.data_act.replace({"Activity": ","}, {"Activity": "."}, regex=True)
        self.data_act = self.data_act.astype({"Activity": float})
        self.data_tmp = pandas.DataFrame(self.data_tmp, columns=["Date", "Time", "Temperature"])
        self.data_tmp = self.data_tmp.replace({"Temperature": ","}, {"Temperature": "."}, regex=True)
        self.data_tmp = self.data_tmp.astype({"Temperature": float})
        self.data_tmp =self.data_tmp.interpolate(method='polynomial', order = 2).ffill().bfill()
        self.data = pandas.merge(self.data_act, self.data_tmp, on=["Date", "Time"])

        self.data["DateTime"] = self.data.apply(lambda x:"%s %s" % (x["Date"], x['Time']), axis=1)
        self.data["DateTime"] = [strptime(str(row), "%m/%d/%y %H:%M:%S") for row in self.data["DateTime"]]

data = paula_dataa()
pass

#%%

# create figure and axis objects with subplots()
fig,ax = plt.subplots()
# make a plot
ax.bar(data.data["DateTime"], data.data["Activity"], color="red")
# set x-axis label
ax.set_xlabel("Time", fontsize = 10)
ax.set_xticks(data.data["DateTime"][0:20:-1])
# set y-axis label
ax.set_ylabel("Activity", fontsize=10)

# twin object for two different y-axis on the sample plot
ax2 = ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(data.data["DateTime"], data.data["Temperature"],color="blue")
ax2.set_xticks(data.data["DateTime"][0:20:-1])
ax2.set_ylabel("Temperature", fontsize=10)
plt.show()

pass
# # %%

# date_range = pandas.date_range(data.start, data.end, freq='10S')
# date_range = pandas.DataFrame({'range_start': date_range[:-1], 'range_end': date_range[1:]})

# # %%

# #cut_visits_df = visits_df.loc[visits_df['visit_start'] >= date_range['range_start'] and visits_df['visit_end'] < date_range['range_end']]

# duration_per_range = []
# entries_per_range = []
# for index, row in date_range.iterrows():
#     entries_per_range.append(0)
#     contained_visits_df = visits_df.loc[(visits_df['visit_start'] >= row['range_start']) & (visits_df['visit_end'] < row['range_end'])]['duration_date']
#     entries_per_range[-1] += len(contained_visits_df)
#     contained_visits_df = contained_visits_df.sum()
#     edge_visits_df_0 = (visits_df.loc[(visits_df['visit_start'] < row['range_start']) & (visits_df['visit_end'] < row['range_end']) & (visits_df['visit_end'] >= row['range_start'])]['visit_end'] - row['range_start']).sum()
#     edge_visits_df_1 = row['range_end'] - visits_df.loc[(visits_df['visit_start'] >= row['range_start']) & (visits_df['visit_start'] < row['range_end']) & (visits_df['visit_end'] >= row['range_end'])]['visit_start']
#     entries_per_range[-1] += len(edge_visits_df_1)
#     edge_visits_df_1 = edge_visits_df_1.sum()
#     contains_visits_df = len(visits_df.loc[(visits_df['visit_start'] < row['range_start']) & (visits_df['visit_end'] >= row['range_end'])])*(row['range_end'] - row['range_start'])
#     duration_per_range.append((contained_visits_df + edge_visits_df_0 + edge_visits_df_1 + contains_visits_df).total_seconds())

# date_range['duration_per_range'] = duration_per_range
# date_range['entries_per_range'] = entries_per_range

# # %%
# #print(date_range)

# date_range.to_excel('date_range.xlsx')
# visits_df[['visit_start', 'visit_end', 'duration_seconds']].to_excel('visits_df.xlsx')

# # %%
# date_range.head()

# %%
