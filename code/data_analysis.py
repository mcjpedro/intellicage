import pandas
import numpy
from bokeh.palettes import gray
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Span, Whisker
from datetime import timedelta

class data_analysis():
    def __init__(self, data):
        self.data = data
        self.start_date = self.data.start
        self.end_date = self.data.end
        self.animals = self.data.animals
        self.animals_dictionary = self.data.animals_dictionary
    
    def visits_eventplot(self, grouped_by='animal'):                
        if grouped_by == 'animal':
            p = figure(width = 600, height = 600, title = "EVENTPLOT OF VISITS", x_axis_label='Protocol Date', y_axis_label='Animals', x_axis_type="datetime")
            p.rect(source=ColumnDataSource(self.data.visits_df), x="visit_start", y="animal_number", width="duration_date", height=0.5, fill_color="#353535", line_color="#353535")
            p.yaxis.ticker = list(self.animals_dictionary.values())
            p.yaxis.major_label_overrides = dict((index, animal) for animal, index in self.animals_dictionary.items())
        elif grouped_by == 'corner':
            p = figure(width = 600, height = 600, title = "EVENTPLOT OF VISITS", x_axis_label='Protocol Date', y_axis_label='Corner', x_axis_type="datetime")
            p.rect(source=ColumnDataSource(self.data.visits_df), x="visit_start", y="corner", width="duration_date", height=0.5, fill_color="#353535", line_color="#353535")
            p.yaxis.ticker = [1,2,3,4]
        
        days_range = pandas.date_range(self.start_date, self.end_date, freq='d', normalize=True, inclusive="right").to_list()
        for date in days_range:
            p.add_layout(Span(location=date, dimension='height', line_color='#A21F27', line_dash='dashed', line_width=2, name='Day limit'))
        show(p)
        
        #self.data.visits_df.to_excel("output.xlsx")

    def visits_eventplot_1(self):
        pass

    def visit_duration_per_animal(self, plot=True, save_excel=False, show_all_points=False):
        pivot_data_frame = pandas.pivot_table(self.data.visits_df, index=['animal_number'], values=['duration_seconds'], aggfunc=[numpy.mean, numpy.std])

        if save_excel:
            pivot_data_frame.to_excel("visit_duration_per_animal.xlsx")

        if plot:
            p = figure(width = 600, height = 300, title = "DISTRIBUTION OF THE DURATION OF VISITS", x_axis_label='Animals', y_axis_label='Visit Duration (s)')

            lower = list(pivot_data_frame[('mean', 'duration_seconds')])
            upper = list(pivot_data_frame[('mean', 'duration_seconds')] + pivot_data_frame[('std', 'duration_seconds')])
            mean = list(pivot_data_frame[('mean', 'duration_seconds')])
            base = list(pivot_data_frame.index)

            p.vbar(x=base, top=mean, width=0.9, color='#A21F27', alpha=0.8, line_color="#353535", line_width=2)

            source_error = ColumnDataSource(data=dict(base=base, lower=lower, upper=upper))
            p.add_layout(Whisker(source=source_error, base="base", upper="upper", lower="lower", line_color="#353535", line_width=2, line_alpha=0.8))
            
            if show_all_points:
                for animal_number in list(self.data.visits_df['animal_number'].unique()):
                    points = self.data.visits_df[self.data.visits_df['animal_number'] == animal_number]['duration_seconds']
                    p.circle(x=animal_number, y=points, width=0.05, color='#353535', alpha=0.6, line_color="#353535")

            p.xaxis.ticker = list(self.animals_dictionary.values())
            p.xaxis.major_label_overrides = dict((value, key) for key, value in self.animals_dictionary.items())
            p.xaxis.major_label_orientation = 45

            show(p)

    def visit_duration_per_corner(self, plot=True, save_excel=False, show_all_points=False):
        pivot_data_frame = pandas.pivot_table(self.data.visits_df, index=['corner'], values=['duration_seconds'], aggfunc=[numpy.mean, numpy.std])

        if save_excel:
            pivot_data_frame.to_excel("visit_duration_per_corner.xlsx")

        if plot:
            p = figure(width = 600, height = 300, title = "DISTRIBUTION OF THE DURATION OF VISITS", x_axis_label='Corners', y_axis_label='Visit Duration (s)')

            lower = list(pivot_data_frame[('mean', 'duration_seconds')])
            upper = list(pivot_data_frame[('mean', 'duration_seconds')] + pivot_data_frame[('std', 'duration_seconds')])
            mean = list(pivot_data_frame[('mean', 'duration_seconds')])
            base = list(pivot_data_frame.index)

            p.vbar(x=base, top=mean, width=0.9, color='#A21F27', alpha=0.8, line_color="#353535", line_width=2)

            source_error = ColumnDataSource(data=dict(base=base, lower=lower, upper=upper))
            p.add_layout(Whisker(source=source_error, base="base", upper="upper", lower="lower", line_color="#353535", line_width=2, line_alpha=0.8))
            
            if show_all_points:
                for corner in list(self.data.visits_df['corner'].unique()):
                    points = self.data.visits_df[self.data.visits_df['corner'] == corner]['duration_seconds']
                    p.circle(x=corner, y=points, width=0.05, color='#353535', alpha=0.6, line_color="#353535")
                
            p.xaxis.ticker = [1,2,3,4]

            show(p)