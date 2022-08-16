import pymice
import pandas
import numpy
import matplotlib.pyplot as plot
from bokeh.palettes import gray
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Span, Whisker
from datetime import timedelta
from tkinter import filedialog
from tkinter import *

class get_files():
    def __init__(self, number_of_marge_data=1):
        root = Tk()
        root.withdraw()
        folder_tuple = filedialog.askopenfilenames(title='Open a file', filetypes=[('zip files', '*.zip')])
        self.folder = folder_tuple[0]

class set_data():    
    def __init__(self, folder):
        self.folder = folder 
        try:
            self.data = pymice.Loader(self.folder, getNp=True, getLog=True, getEnv=True, getHw=True, verbose=False)
            self.visits = self.data.getVisits(order='Start')
            self.animals = sorted(list(self.data.getAnimal()))
            self.start = self.data.getStart()
            self.end = self.data.getEnd()
            self.days_range = self.get_days_range()
            print("Data loaded")
        except Exception as exception:
           print(exception)
    
    def get_days_range(self):
        days_range = pandas.date_range(self.start, self.end, freq='d', normalize=True, inclusive="right").to_list()

        return days_range

    def make_animals_table(self):
        animal_number = 0
        animals_data_frame = pandas.DataFrame(columns=['name', 'number', 'sex', 'tag'])
        for animal_name in self.animals:
            animal = self.data.getAnimal(animal_name)
            animals_data_frame.loc[str(animal_number)] = [animal.Name, animal_number, animal.Sex, animal.Tag]
            animal_number += 1
        
        return animals_data_frame

    def make_visits_table(self):
        visit_number = 0
        visits_data_frame = pandas.DataFrame(columns=['visit', 'tag', 'animal', 'sex', 'cage', 'corner', 'duration', 'visit_start', 'visit_end'])
        for visit in self.visits:
            visits_data_frame.loc[str(visit_number)] = [visit_number, str(list(visit.Animal.Tag)[0]), str(visit.Animal.Name), str(visit.Animal.Sex), 
                                                        int(visit.Cage), int(visit.Corner), visit.Duration.total_seconds(), visit.Start, visit.End]
            visit_number += 1
        
        self.animals_dictionary = {animal:index for index, animal in enumerate(self.animals)}
        visits_data_frame['animal_number'] = visits_data_frame['animal'].map(self.animals_dictionary)

        return visits_data_frame

    def make_nosepokes_table(self):
        visit_number = 0
        nosepoke_number = 0
        nosepoke_data_frame = pandas.DataFrame(columns=['visit', 'tag', 'animal', 'sex', 'cage', 'corner', 'duration', 'visit_start', 'visit_end', 'side', 'door', 'duration', 'start', 'end', 'lick_number', 'lick_duration'])
        for visit in self.visits:
            for nosepoke in visit.Nosepokes:
                nosepoke_data_frame.loc[str(nosepoke_number)] = [visit_number, visit.Animal.Tag, visit.Animal.Name, visit.Animal.Sex, visit.Cage, visit.Corner,
                                                                visit.Duration.total_seconds(), visit.Start, visit.End, nosepoke.Side, nosepoke.Door, 
                                                                nosepoke.Duration, nosepoke.Start, nosepoke.End, nosepoke.LickNumber, nosepoke.LickDuration]
                nosepoke_number += 1
            visit_number += 1
        
        return nosepoke_data_frame

    def make_all_tables(self, animals=True, visits=True, nosepokes=True):
        if animals:
            animals_table = self.make_animals_table()
        else:
            animals_table = pandas.DataFrame()
        if visits:
            visits_table = self.make_visits_table()
        else:
            visits_table = pandas.DataFrame()
        if nosepokes:
            nosespoke_table = self.make_nosepokes_table()
        else:
            nosespoke_table = pandas.DataFrame()

        return (animals_table, visits_table, nosespoke_table)

    def save_table(self, animals=True, visits=True, nosepokes=True):
        if animals:
            self.make_animals_table().to_excel("animals.xlsx")
        if visits:
            self.make_visits_table().to_excel("visits.xlsx")
        if nosepokes:
            self.make_nosepokes_table().to_excel("nosepokes.xlsx")

class data_analysis():
    def __init__(self, data, animals=True, visits=True, nosepokes=True):
        self.data = data
        self.start_date = self.data.start
        self.end_date = self.data.end
        self.animals = self.data.animals
        
        data_tables = data.make_all_tables(animals, visits, nosepokes)
        if animals: self.animals_data_frame = data_tables[0]
        if visits: self.visits_data_frame = data_tables[1]
        if nosepokes: self.nosepoke_data_frame = data_tables[2]
    
    def visits_eventplot(self, grouped_by='animal'):                
        if grouped_by == 'animal':
            p = figure(width = 600, height = 600, title = "EVENTPLOT OF VISITS", x_axis_label='Protocol Date', y_axis_label='Animals', x_axis_type="datetime")
            p.rect(source=ColumnDataSource(self.visits_data_frame), x="visit_start", y="animal_number", width="duration", height=0.5, fill_color="#353535", line_color="#353535")
            p.yaxis.ticker = list(self.data.animals_dictionary.values())
            p.yaxis.major_label_overrides = dict((value, key) for key, value in self.data.animals_dictionary.items())
        elif grouped_by == 'corner':
            p = figure(width = 600, height = 600, title = "EVENTPLOT OF VISITS", x_axis_label='Protocol Date', y_axis_label='Corner', x_axis_type="datetime")
            p.rect(source=ColumnDataSource(self.visits_data_frame), x="visit_start", y="corner", width="duration", height=0.5, fill_color="#353535", line_color="#353535")
            p.yaxis.ticker = [1,2,3,4]
        
        for date in self.data.days_range:
            p.add_layout(Span(location=date, dimension='height', line_color='#A21F27', line_dash='dashed', line_width=2, name='Day limit'))
        show(p)
        
        self.visits_data_frame.to_excel("output.xlsx")

    def visit_duration_per_animal(self, plot=True, save_excel=False, show_all_points=False):
        data_frame = pandas.pivot_table(self.visits_data_frame, index=['animal_number'], values=['duration'], aggfunc=[numpy.mean, numpy.std])
        print(data_frame)

        if save_excel:
            data_frame.to_excel("visit_duration_per_animal.xlsx")

        if plot:
            p = figure(width = 600, height = 300, title = "DISTRIBUTION OF THE DURATION OF VISITS", x_axis_label='Animals', y_axis_label='Visit Duration (s)')

            lower = list(data_frame[('mean', 'duration')] - data_frame[('std', 'duration')])
            upper = list(data_frame[('mean', 'duration')] + data_frame[('std', 'duration')])
            mean = list(data_frame[('mean', 'duration')])
            base = list(data_frame.index)

            p.vbar(x=base, top=mean, width=0.9, color='#A21F27', alpha=0.8, line_color="#353535", line_width=2)

            source_error = ColumnDataSource(data=dict(base=base, lower=lower, upper=upper))
            p.add_layout(Whisker(source=source_error, base="base", upper="upper", lower="lower", line_color="#353535", line_width=2, line_alpha=0.8))
            
            if show_all_points:
                for animal_number in list(self.visits_data_frame['animal_number'].unique()):
                    y = self.visits_data_frame[self.visits_data_frame['animal_number'] == animal_number]['duration']
                    p.circle(x=animal_number, y=y, width=0.05, color='#353535', alpha=0.6, line_color="#353535")

            p.xaxis.ticker = list(self.data.animals_dictionary.values())
            p.xaxis.major_label_overrides = dict((value, key) for key, value in self.data.animals_dictionary.items())
            p.xaxis.major_label_orientation = 45

            show(p)

    def visit_duration_per_corner(self, plot=True, save_excel=False, show_all_points=False):
        data_frame = pandas.pivot_table(self.visits_data_frame, index=['corner'], values=['duration'], aggfunc=[numpy.mean, numpy.std])

        if save_excel:
            data_frame.to_excel("visit_duration_per_corner.xlsx")

        if plot:
            p = figure(width = 600, height = 300, title = "DISTRIBUTION OF THE DURATION OF VISITS", x_axis_label='Corners', y_axis_label='Visit Duration (s)')

            lower = list(data_frame[('mean', 'duration')])
            upper = list(data_frame[('mean', 'duration')] + data_frame[('std', 'duration')])
            mean = list(data_frame[('mean', 'duration')])
            base = list(data_frame.index)

            p.vbar(x=base, top=mean, width=0.9, color='#A21F27', alpha=0.8, line_color="#353535", line_width=2)

            source_error = ColumnDataSource(data=dict(base=base, lower=lower, upper=upper))
            p.add_layout(Whisker(source=source_error, base="base", upper="upper", lower="lower", line_color="#353535", line_width=2, line_alpha=0.8))
            
            if show_all_points:
                for corner in list(self.visits_data_frame['corner'].unique()):
                    y = self.visits_data_frame[self.visits_data_frame['corner'] == corner]['duration']
                    p.circle(x=corner, y=y, width=0.05, color='#353535', alpha=0.6, line_color="#353535")
                
            p.xaxis.ticker = [1,2,3,4]

            show(p)

files = get_files()
data = set_data(files.folder)
data.save_table(False, True, False)

analysis = data_analysis(data, True, True, False)
analysis.visits_eventplot(grouped_by='animal')
analysis.visit_duration_per_corner(plot=True, save_excel=False)
