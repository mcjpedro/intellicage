#%%
import pandas
import datetime
import data_handler
#from data_analysis import data_analysis

#%%
#files = data_handler.get_files()
#print(files.folder)
data = data_handler.set_data("G:/Outros computadores/Desktop/GitHub/intellicage/data_examples/2022-03-30 11.11.54.zip")
_, visits = data.make_data_frames(animals=True, visits=True, nosepokes=False, to_excel=False)

#analysis = data_analysis(data)
#analysis.visits_eventplot(grouped_by='corner')
#analysis.visit_duration_per_corner(show_all_points=True)

# %%

date_range = pandas.date_range(data.start, data.end, freq='10S')
date_range = pandas.DataFrame({'range_start': date_range[:-1], 'range_end': date_range[1:]})

# %%

#cut_visits = visits.loc[visits['visit_start'] >= date_range['range_start'] and visits['visit_end'] < date_range['range_end']]

duration_per_range = []
entries_per_range = []
for index, row in date_range.iterrows():
    entries_per_range.append(0)
    contained_visits = visits.loc[(visits['visit_start'] >= row['range_start']) & (visits['visit_end'] < row['range_end'])]['duration_date']
    entries_per_range[-1] += len(contained_visits)
    contained_visits = contained_visits.sum()
    edge_visits_0 = (visits.loc[(visits['visit_start'] < row['range_start']) & (visits['visit_end'] < row['range_end']) & (visits['visit_end'] >= row['range_start'])]['visit_end'] - row['range_start']).sum()
    edge_visits_1 = row['range_end'] - visits.loc[(visits['visit_start'] >= row['range_start']) & (visits['visit_start'] < row['range_end']) & (visits['visit_end'] >= row['range_end'])]['visit_start']
    entries_per_range[-1] += len(edge_visits_1)
    edge_visits_1 = edge_visits_1.sum()
    contains_visits = len(visits.loc[(visits['visit_start'] < row['range_start']) & (visits['visit_end'] >= row['range_end'])])*(row['range_end'] - row['range_start'])
    duration_per_range.append((contained_visits + edge_visits_0 + edge_visits_1 + contains_visits).total_seconds())

date_range['duration_per_range'] = duration_per_range
date_range['entries_per_range'] = entries_per_range

# %%
#print(date_range)

date_range.to_excel('date_range.xlsx')
visits[['visit_start', 'visit_end', 'duration_seconds']].to_excel('visits.xlsx')

# %%
date_range.head()
# %%
