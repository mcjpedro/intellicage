import pymice
import pandas
import matplotlib.pyplot as plot
import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from datetime import timedelta
from tkinter import filedialog
from tkinter import *
from time import strptime

class intellicage_data():    
    def __init__(self, file, nosepokes=False):
        self.file = file 
        self.data = pymice.Loader(self.file, getNp=True, getLog=True, getEnv=True, getHw=True, verbose=False)
        self.visits = self.data.getVisits(order='Start')
        
        self.animals = sorted(list(self.data.getAnimal()))
        self.animals_dict = {animal:{'number':index} for index, animal in enumerate(self.animals)}
        
        self.start = self.data.getStart()
        self.end = self.data.getEnd()
        
        self.animals_df = self._animals_data_frame()
        self.visits_df = self._visits_data_frame()
        if nosepokes:
            self.nosepokes_df = self._nosepokes_data_frame()
        
        print("Data loaded")

    def _animals_data_frame(self):
        _animals_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex'])
        for _count, _animal_name in enumerate(self.animals):
            animal = self.data.getAnimal(_animal_name)
            _animals_df.loc[_count] = [animal.Tag, animal.Name, _count, animal.Sex]
           
        return _animals_df

    def _visits_data_frame(self):
        _visits_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex', 'visit_number', 
                                               'cage', 'corner', 'duration_seconds', 'duration_date', 
                                               'visit_start', 'visit_end'])
        for _count, _visit in enumerate(self.visits):              
            _visits_df.loc[_count] = [str(list(_visit.Animal.Tag)[0]), str(_visit.Animal.Name), 
                                           self.animals_dict[_visit.Animal.Name]['number'], 
                                           str(_visit.Animal.Sex), _count, int(_visit.Cage), 
                                           int(_visit.Corner), _visit.Duration.total_seconds(), 
                                           _visit.Duration, _visit.Start, _visit.End]
        for _animal in self.animals:
            self.animals_dict[_animal]['visits'] = _visits_df[_visits_df['animal'] == _animal]

        return _visits_df

    def _nosepokes_data_frame(self):
        _nosepokes_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex', 'visit_number', 
                                                  'cage', 'corner', 'duration_seconds', 'duration_date', 
                                                  'visit_start', 'visit_end', 'side', 'door', 'duration', 
                                                  'start', 'end', 'lick_number', 'lick_duration'])
        for _count_visit, visit in enumerate(self.visits):
            for _count_nosepoke, nosepoke in enumerate(visit.Nosepokes):
                _nosepokes_df.loc[_count_nosepoke] = [str(list(visit.Animal.Tag)[0]), str(visit.Animal.Name), 
                                                     self.animals_dict[visit.Animal.Name]['number'], str(visit.Animal.Sex),
                                                     _count_visit, int(visit.Cage), int(visit.Corner), 
                                                     visit.Duration.total_seconds(), visit.Duration, 
                                                     visit.Start, visit.End, int(nosepoke.Side), int(nosepoke.Door), 
                                                     nosepoke.Duration, nosepoke.Start, nosepoke.End, 
                                                     int(nosepoke.LickNumber), nosepoke.LickDuration]

        for _animal in self.animals:
            self.animals_dict[_animal]['nosepokes'] = _nosepokes_df[_nosepokes_df['animal'] == _animal]

        return _nosepokes_df

    def visits_by_intervals(self, interval='1H', zt_0_time=0, first_hour=0, cycle_type='DL'):
        self.zt_0_time = zt_0_time
        self.first_hour = first_hour
        _start_date = self.start.replace(hour=0, minute=0, second=0, microsecond=0)
        _end_date = self.end.replace(hour=0, minute=0, second=0, microsecond=0)
        _date_range = pandas.date_range(_start_date, _end_date, freq=interval)
        _date_range = pandas.DataFrame({'interval_start': _date_range[:-1], 'interval_end': _date_range[1:]})

        for _animal in self.animals:
            _visits_df = self.animals_dict[_animal]['visits']
            
            _duration_per_range = []
            _entries_per_range = []
            for _, _row in _date_range.iterrows():

                _entries_per_range.append(0)
                _contained_visits_df = _visits_df.loc[(_visits_df['visit_start'] >= _row['interval_start']) & (_visits_df['visit_end'] < _row['interval_end'])]['duration_date']
                _entries_per_range[-1] += len(_contained_visits_df)
                _contained_visits_df = _contained_visits_df.sum()
                _edge_visits_df_0 = (_visits_df.loc[(_visits_df['visit_start'] < _row['interval_start']) & (_visits_df['visit_end'] < _row['interval_end']) & (_visits_df['visit_end'] >= _row['interval_start'])]['visit_end'] - _row['interval_start']).sum()
                _edge_visits_df_1 = _row['interval_end'] - _visits_df.loc[(_visits_df['visit_start'] >= _row['interval_start']) & (_visits_df['visit_start'] < _row['interval_end']) & (_visits_df['visit_end'] >= _row['interval_end'])]['visit_start']
                _entries_per_range[-1] += len(_edge_visits_df_1)
                _edge_visits_df_1 = _edge_visits_df_1.sum()
                _contains_visits_df = len(_visits_df.loc[(_visits_df['visit_start'] < _row['interval_start']) & (_visits_df['visit_end'] >= _row['interval_end'])])*(_row['interval_end'] - _row['interval_start'])
                _duration_per_range.append((_contained_visits_df + _edge_visits_df_0 + _edge_visits_df_1 + _contains_visits_df).total_seconds())

            _zt_correction = numpy.timedelta64(zt_0_time , 'h')
            _date_range['interval_start'] = [date - _zt_correction for date in _date_range['interval_start']]
            _date_range['interval_end'] = [date - _zt_correction for date in _date_range['interval_end']]

            if first_hour >= 0 and first_hour < 24:
                _first_hour_correction = numpy.timedelta64(24 - first_hour, 'h')
                _date_range['interval_start'] = [date + _first_hour_correction for date in _date_range['interval_start']]
                _date_range['interval_end'] = [date + _first_hour_correction for date in _date_range['interval_end']]
            elif first_hour >= 24:
                raise ValueError("First hour must be less than 24.")

            _visits_at_interval = pandas.DataFrame({'duration' : _duration_per_range, 'activity' : _entries_per_range}, index = _date_range['interval_start'])
            self.animals_dict[_animal]['visits_at_interval'] = _visits_at_interval
            self.animals_dict[_animal]['visits_at_interval']['day'] = [str(row).split(" ")[0] for row in self.animals_dict[_animal]['visits_at_interval'].index]

        self._get_is_night(cycle_type)

    def _get_is_night(self, cycle_type='DL'):
        _first_hour = numpy.datetime64(0, 'h') + numpy.timedelta64(24 - self.first_hour, 'h')
        _last_hour = _first_hour + numpy.timedelta64(12, 'h')

        _first_hour = pandas.Timestamp(_first_hour).hour
        _last_hour = pandas.Timestamp(_last_hour).hour

        for _animal in self.animals:
            _data = self.animals_dict[_animal]['visits_at_interval']
            if cycle_type == 'DD':
                _is_night = [True]*len(_data)
            elif cycle_type == 'LL':
                _is_night = [False]*len(_data)
            elif cycle_type == 'DL':
                _is_night = []
                for date in _data.index.hour:
                    if date >= _first_hour and date < _last_hour:
                        _is_night.append(True)
                    else:
                        _is_night.append(False)
            elif cycle_type == 'LD':
                _is_night = []
                for date in _data.index.hour:
                    if date >= _first_hour and date < _last_hour:
                        _is_night.append(False)
                    else:
                        _is_night.append(True)
            else:
                raise(ValueError("Cycle must be 'DD', 'LL', 'DL' or 'LD'"))
            
            self.animals_dict[_animal]['visits_at_interval']['is_night'] = _is_night

    def actogram_activity(self, animal, save_file=None, first_day=False):
        if self.animals_dict[animal].get('visits_at_interval') is None:
            raise ValueError("To run the actogram plot you need to get the visits separated in regular time intervals first. Use the method 'visits_by_intervals'.")
        _actogram = self.animals_dict[animal]['visits_at_interval']
    
        days = list(_actogram['day'].unique())
        if first_day == False: days = days[1:]
        num_days = len(days) 
        _actogram['day_steps'] = _actogram.index.hour
        _actogram['day_steps'] = _actogram['day_steps'] + _actogram.index.minute/60
        _step_length = _actogram['day_steps'][1] - _actogram['day_steps'][0]

        max_y = numpy.nanmax(_actogram['activity'])
        
        subplot_height = 5
        total_height = subplot_height*(2*num_days)
        total_height = total_height*1.2
        total_width = 650
        fig, subplots = plt.subplots(num_days, 2, squeeze=False, sharex=True, sharey=True,
                                     figsize=(total_width/100, total_height/100), dpi=100,
                                     gridspec_kw={'hspace': 0, 'wspace': 0, 'top': 0.95, 'bottom': 0.12})
        
        hours_per_tick = 2
        tick_pos = list(range(0, 24, hours_per_tick))
        
        tick_labels = tick_pos[int(self.first_hour/hours_per_tick):] + tick_pos[:int(self.first_hour/hours_per_tick)]
        tick_labels = [str(hour) for hour in tick_labels]

        for count, day in enumerate(days):
            axes = []
            if count > 0:
                axes.append(subplots[count][0])
                axes.append(subplots[count-1][1])
            else:
                axes.append(subplots[count][0])
            
            _time_to_plot = _actogram[_actogram['day'] == day]['day_steps']
            _activity_to_plot = _actogram[_actogram['day'] == day]['activity']
            _is_night_to_plot = _actogram[_actogram['day'] == day]['is_night']

            for count_ax, ax in enumerate(axes):            
                for step, time in zip(_is_night_to_plot, _time_to_plot):
                    if step == True:
                        ax.axvspan(time, time + _step_length, facecolor='#A1A1A1', alpha=0.8, edgecolor='none')
                    else:
                        ax.axvspan(time, time + _step_length, facecolor='white', alpha=1, edgecolor='none')

                ax.bar(_time_to_plot, _activity_to_plot, width=_step_length, align='edge', color='#790F0C')

                if count_ax != 0 and count%2 != 0:
                    ax.yaxis.set_label_position("right")
                    ax.yaxis.tick_right()
                    ax.set_yticks([])
                    ax.set_ylabel("Day " + str(count), rotation=0, fontsize=8, labelpad=20, va='center')
                elif count_ax == 0 and count%2 == 0:
                    ax.yaxis.set_label_position("left")
                    ax.yaxis.tick_left()
                    ax.set_yticks([])
                    ax.set_ylabel("Day " + str(count), rotation=0, fontsize=8, labelpad=20, va='center')
            
                ax.set_xlim([0, 24])
                ax.set_ylim([0, max_y])
        subplots[-1][0].set_xticks(tick_pos, tick_labels, fontsize=8)
        subplots[-1][1].set_xticks(tick_pos, tick_labels, fontsize=8)

        fig.text(0.5, 0.98, f"Activity Actogram", ha='center', fontsize=14, wrap=False)
        fig.text(0.5, 0.07, 'Time (ZT)', ha='center')
        if save_file == None:
            plt.show()
        else:
            plt.savefig(save_file + '.png', dpi=100)
            plt.close()

file = "F:/github/intellicage/data_examples_intellicage/2022-04-01 17.17.35.zip"
example = intellicage_data(file, nosepokes=False)
example.visits_by_intervals(interval = '1H', zt_0_time=20, first_hour=18, cycle_type='DL')
example.actogram_activity('Animal 1', first_day=True)

pass