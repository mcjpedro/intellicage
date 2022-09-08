import pymice
import pandas
import matplotlib.pyplot as plot
from bokeh.palettes import gray
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Span, Whisker
from datetime import timedelta
from tkinter import filedialog
from tkinter import *
from time import strptime

class intellicage_data():    
    def __init__(self):
        self.folder = self._get_file() 
        try:
            self.data = pymice.Loader(self.folder, getNp=True, getLog=True, getEnv=True, getHw=True, verbose=False)
            self.visits = self.data.getVisits(order='Start')
            self.animals = sorted(list(self.data.getAnimal()))
            self.animals_dictionary = {animal:index for index, animal in enumerate(self.animals)}
            self.start = self.data.getStart()
            self.end = self.data.getEnd()
            
            self.animals_df = None
            self.visits_df = None
            self.nosepokes_df = None
            
            print("Data loaded")
        except Exception as exception:
            print(exception)

    def _get_file(self, number_of_marge_data=1):
        # root = Tk()
        # root.withdraw()
        # folder_tuple = filedialog.askopenfilenames(title='Open a file', filetypes=[('zip files', '*.zip')])
        # self.folder = folder_tuple[0]
        self.folder = "G:/Outros computadores/Desktop/GitHub/intellicage/data_examples/2022-03-30 11.11.54.zip"

    def animals_data_frame(self, to_excel=True):
        animals_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex'])
        for animal_number, animal_name in enumerate(self.animals):
            animal = self.data.getAnimal(animal_name)
            animals_df.loc[animal_number] = [animal.Tag, animal.Name, animal_number, animal.Sex]
           
        if to_excel:
            self.animals_df().to_excel("animals_df.xlsx")

        self.animals_df = animals_df
        return self.animals_df

    def visits_data_frame(self, to_excel=True):
        visits_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex', 'visit_number', 
                                              'cage', 'corner', 'duration_seconds', 'duration_date', 
                                              'visit_start', 'visit_end'])
        for visit_number, visit in enumerate(self.visits):              
            visits_df.loc[visit_number] = [str(list(visit.Animal.Tag)[0]), str(visit.Animal.Name), 
                                           self.animals_dictionary[visit.Animal.Name], str(visit.Animal.Sex), 
                                           visit_number, int(visit.Cage), int(visit.Corner), 
                                           visit.Duration.total_seconds(), visit.Duration, 
                                           visit.Start, visit.End]

        if to_excel:
            self.visits_df().to_excel("visits_df.xlsx")

        self. visits_df = visits_df
        return self.visits_df

    def nosepokes_data_frame(self, to_excel=True):
        nosepokes_df = pandas.DataFrame(columns=['tag', 'animal', 'animal_number', 'sex', 'visit_number', 
                                                 'cage', 'corner', 'duration_seconds', 'duration_date', 
                                                 'visit_start', 'visit_end', 'side', 'door', 'duration', 
                                                 'start', 'end', 'lick_number', 'lick_duration'])
        for visit_number, visit in enumerate(self.visits):
            for nosepoke_number, nosepoke in enumerate(visit.Nosepokes):
                nosepokes_df.loc[nosepoke_number] = [str(list(visit.Animal.Tag)[0]), str(visit.Animal.Name), 
                                                     self.animals_dictionary[visit.Animal.Name], str(visit.Animal.Sex),
                                                     visit_number, int(visit.Cage), int(visit.Corner), 
                                                     visit.Duration.total_seconds(), visit.Duration, 
                                                     visit.Start, visit.End, int(nosepoke.Side), int(nosepoke.Door), 
                                                     nosepoke.Duration, nosepoke.Start, nosepoke.End, 
                                                     int(nosepoke.LickNumber), nosepoke.LickDuration]
            
        if to_excel:
            self.nosepokes_df().to_excel("nosepokes_df.xlsx")

        self.nosepokes_df = nosepokes_df
        return self.nosepokes_df

class paula_data():
    def __init__(self):
        self.file_name = "F:/GitHub/intellicage/data_examples_paula/controlDD part1 ale animal01.asc"

        file = open(self.file_name, 'r')  # We need to re-open the file
        lines = file.readlines()
        lines = [line.strip() for line in lines]	
        file.close()
        self.logfile = lines[0].split("Experiment Logfile:", 1)[1].strip()
        self.description = lines[1].split("Experiment Description:", 1)[1].strip()
        self.start_date = lines[3].split("Start Date/Time ", 1)[1].strip()
        self.end_date = strptime(lines[4].split("End Date/Time ", 1)[1].strip(), "%m/%d/%y %H:%M:%S")
        self.animal_id = int(lines[6].split("Animal ID:", 1)[1].strip())
        self.group_id = lines[7].split("Group ID:", 1)[1].strip()
        self.units_measured = lines[8].split("Units Measured:", 1)[1].strip()
        self.sampling_interval = lines[9].split("Sampling Interval:", 1)[1].strip()
        self.low_clipping = lines[10].split("Low Clipping Limit:", 1)[1].strip()
        self.high_clipping = lines[11].split("High Clipping Limit:", 1)[1].strip()
        self.data_string = lines[15:]
        self.data = [self.data_string[sample].split(",", 2) for sample in range(0, len(self.data_string))]
