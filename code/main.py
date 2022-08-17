#%%
import pandas
import datetime
import data_handler
from data_analysis import data_analysis

#%%
#files = data_handler.get_files()
#print(files.folder)
data = data_handler.set_data("G:/Outros computadores/Desktop/GitHub/intellicage/data_examples/2022-03-30 11.11.54.zip")
_, visits = data.make_data_frames(animals=True, visits=True, nosepokes=False, to_excel=False)

#analysis = data_analysis(data)
#analysis.visits_eventplot(grouped_by='corner')
#analysis.visit_duration_per_corner(show_all_points=True)

# %%
data_range = pandas.date_range(data.start, data.end, freq='1H').to_list()
duration_per_step = []

for time in range(0, len(data_range) - 1):
    duration_per_step.append(datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0))
    for visit in zip(visits['visit_start'], visits['visit_end']):
        if visit[0] >= data_range[time] and visit[0] < data_range[time + 1] and visit[1] <= data_range[time + 1]:
            duration_per_step[-1] += (visit[1] - visit[0])
            pass
        elif visit[0] >= data_range[time] and visit[0] < data_range[time + 1] and visit[1] > data_range[time + 1]:
            duration_per_step[-1] += (data_range[time + 1] - visit[0])
            pass
    
# %%
data_frame = pandas.DataFrame({'data_range': data_range[:-1], 'duration_per_step': duration_per_step})

print(data_frame)

# %%
