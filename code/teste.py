import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource

df = pd.DataFrame({'y':[1,2,3,4,4], 
                   'start':[0, 1, 1, 10, 6], 
                   'duration':[1, 2, 1, 5, 2], 
                   'color':['green', 'red', 'blue', 'red', 'green']
                  })

p = figure(
    width=350,
    height=350,
    title="Task Stream",
    toolbar_location="above",
)

p.rect(
    source=ColumnDataSource(df),
    x="start",
    width="duration",
    height=0.4,
    fill_color="color",
    line_color="color",
)
show(p)