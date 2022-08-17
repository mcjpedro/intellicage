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
            self.animals_dictionary = {animal:index for index, animal in enumerate(self.animals)}
            self.start = self.data.getStart()
            self.end = self.data.getEnd()
            print("Data loaded")
        except Exception as exception:
            print(exception)

    def make_data_frames(self, animals=True, visits=True, nosepokes=True, to_excel=True):
        data_frames = []
        if animals:
            animals_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex'])
            for animal_number, animal_name in enumerate(self.animals):
                animal = self.data.getAnimal(animal_name)
                animals_df.loc[animal_number] = [animal.Tag, animal.Name, animal_number, animal.Sex]
            
            if to_excel:
                self.animals_df().to_excel("animals_df.xlsx")

            data_frames.append(animals_df)

        if visits:
            visits_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex', 'visit_number', 'cage', 'corner', 'duration_seconds', 'duration_date', 'visit_start', 'visit_end'])
            for visit_number, visit in enumerate(self.visits):              
                visits_df.loc[visit_number] = [str(list(visit.Animal.Tag)[0]), str(visit.Animal.Name), self.animals_dictionary[visit.Animal.Name], str(visit.Animal.Sex), visit_number, int(visit.Cage), int(visit.Corner), visit.Duration.total_seconds(), visit.Duration, visit.Start, visit.End]

            if to_excel:
                self.visits_df().to_excel("visits_df.xlsx")

            data_frames.append(visits_df)

        if nosepokes:
            nosepokes_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex', 'visit_number', 'cage', 'corner', 'duration_seconds', 'duration_date', 'visit_start', 'visit_end', 'side', 'door', 'duration', 'start', 'end', 'lick_number', 'lick_duration'])
            for visit_number, visit in enumerate(self.visits):
                for nosepoke_number, nosepoke in enumerate(visit.Nosepokes):
                    nosepokes_df.loc[nosepoke_number] = [str(list(visit.Animal.Tag)[0]), str(visit.Animal.Name), self.animals_dictionary[visit.Animal.Name], str(visit.Animal.Sex), visit_number, int(visit.Cage), int(visit.Corner), visit.Duration.total_seconds(), visit.Duration, visit.Start, visit.End,
                                                        int(nosepoke.Side), int(nosepoke.Door), nosepoke.Duration, nosepoke.Start, nosepoke.End, int(nosepoke.LickNumber), nosepoke.LickDuration]
            
            if to_excel:
                self.nosepokes_df().to_excel("nosepokes_df.xlsx")

            data_frames.append(nosepokes_df)
        
        self.data_frames = data_frames
        return data_frames
