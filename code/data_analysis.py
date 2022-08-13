import pymice
import pandas
import numpy
import matplotlib.pyplot as plot
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
            self.visits = self.data.getVisits()
            self.animals = self.data.getAnimal()
            self.start = self.data.getStart()
            self.end = self.data.getEnd()
        except Exception as exception:
            print(exception)
    
    def make_table_animals(self):
        animal_number = 0
        animals_data_frame = pandas.DataFrame(columns=['name', 'sex', 'tag'])
        for animal_name in self.animals:
            animal = self.data.getAnimal(animal_name)
            animals_data_frame.loc[str(animal_number)] = [animal.Name, animal.Sex, animal.Tag]
            animal_number += 1
        
        return animals_data_frame

    def make_table_visits(self):
        visit_number = 0
        visits_data_frame = pandas.DataFrame(columns=['visit', 'tag', 'animal', 'sex', 'cage', 'corner', 'duration', 'visit_start', 'visit_end'])
        for visit in self.visits:
            visits_data_frame.loc[str(visit_number)] = [visit_number, visit.Animal.Tag, visit.Animal.Name, visit.Animal.Sex, visit.Cage, visit.Corner, visit.Duration.total_seconds(), visit.Start, visit.End]
            visit_number += 1
        
        return visits_data_frame

    def make_table_nosepokes(self):
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
        #nosepoke_data_frame.to_excel("output.xlsx")

    def save_table(self, animals=True, visits=True, nosepokes=True):
        if animals:
            self.make_table_animals().to_excel("animals.xlsx")
        if visits:
            self.make_table_visits().to_excel("visits.xlsx")
        if nosepokes:
            self.make_table_nosepokes().to_excel("nosepokes.xlsx")

class data_analysis():
    def __init__(self, animals_data_frame = None, visits_data_frame = None, nosepoke_data_frame = None):
        self.animals_data_frame = animals_data_frame
        self.visits_data_frame = visits_data_frame
        self.nosepoke_data_frame = nosepoke_data_frame
    
    def visits_eventplot(self, protocol_start, protocol_end):
        total_time_ms = int((protocol_end - protocol_start).total_seconds()*1000)
        vector_time_ms = numpy.arange(0, total_time_ms, 1)
        
        self.visits_data_frame['time_from_init_0'] = self.visits_data_frame.apply(lambda row: int((row.visit_start - protocol_start).total_seconds()*1000), axis=1)
        self.visits_data_frame['time_from_init_1'] = self.visits_data_frame.apply(lambda row: int((row.visit_end - protocol_start).total_seconds()*1000), axis=1)
        
        eventplot_dict = {}
        for animal in self.animals_data_frame['name']:
            eventplot_dict[animal] = []
            data_per_animal = self.visits_data_frame.loc[self.visits_data_frame['animal'] == animal]
            for _, visit in data_per_animal.iterrows():
                eventplot_dict[animal] += list(range(visit['time_from_init_0'], visit['time_from_init_1'], 1))
        
        plot.eventplot(eventplot_dict.values(), orientation = 'horizontal', linelengths = 0.2, color = [(0.5,0.5,0.8)])
        plot.show()

        self.visits_data_frame.to_excel("output.xlsx")

    # Fazer um ectograma para cada animal

files = get_files()
data = set_data(files.folder)
animals_data_frame = data.make_table_animals()
visits_data_frame = data.make_table_visits()

print(animals_data_frame)
print(visits_data_frame)

analysis = data_analysis(animals_data_frame, visits_data_frame)
analysis.visits_eventplot(data.start, data.end)
