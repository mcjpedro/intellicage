import numpy
from datetime import datetime
from chronobiology import CycleAnalyzer, generate_data

class experiment():
    def __init__(self):
        self.file_name = "G:\\Outros computadores\\Desktop\\GitHub\\intellicage\\data_examples_paula\\controlDD part1 ale animal01.asc"

        file = open(self.file_name, 'r')
        lines = file.readlines()
        lines = [line.strip() for line in lines]	
        file.close()
        self.logfile = lines[0].split("Experiment Logfile:", 1)[1].strip()
        self.description = lines[1].split("Experiment Description:", 1)[1].strip()
        self.start_date = datetime.strptime(lines[3].split("Start Date/Time ", 1)[1].strip(), "%m/%d/%y %H:%M:%S")
        self.end_date = datetime.strptime(lines[4].split("End Date/Time ", 1)[1].strip(), "%m/%d/%y %H:%M:%S")
        self.animal_id = int(lines[6].split("Animal ID:", 1)[1].strip())
        self.group_id = lines[7].split("Group ID:", 1)[1].strip()
        self.units_measured = lines[8].split("Units Measured:", 1)[1].strip()
        self.sampling_interval = lines[9].split("Sampling Interval:", 1)[1].strip()
        self.low_clipping = lines[10].split("Low Clipping Limit:", 1)[1].strip()
        self.high_clipping = lines[11].split("High Clipping Limit:", 1)[1].strip()
        
        self._data_string = lines[15:]
        self._raw_data = [sample.replace(',', ' ', 1).split(",", 1) for sample in self._data_string]
        self.time = [datetime.strptime(sample[0], "%m/%d/%y %H:%M:%S") for sample in self._raw_data]
        self.parameter = [float(sample[1].replace(',', '.', 1)) for sample in self._raw_data]
        self.is_nigth = [True]*len(self.time)

        self.time = [numpy.datetime64(date) for date in self.time]
        self.sampling_interval = (self.time[1] - self.time[0])

        self.zt_0_time = numpy.datetime64(zt_0_time)
        _zt_correction = self.time[0] - self.zt_0_time
        self.time = [date - _zt_correction for date in self.time]

    def resample(self, new_sampling_interval):
        _sampling_interval_int = self.sampling_interval.astype(int)
        _sampling_interval_int = _sampling_interval_int*1e-6
        
        if new_sampling_interval % _sampling_interval_int != 0:
            raise ValueError("New sampling interval must be a multiple of the old one")
        else:
            _resample_factor = int(new_sampling_interval / _sampling_interval_int)
            
            _new_time = []
            _new_parameter = []
            _new_is_nigth = []

            samples = list(range(0, len(self.time), _resample_factor))
            for sample in samples[1:]:   
                _new_time.append(self.time[sample - _resample_factor])
                _new_parameter.append(sum(self.parameter[sample - _resample_factor:sample]))
                _new_is_nigth.append(self.is_nigth[sample])

            self.time = _new_time
            self.parameter = _new_parameter
            self.is_nigth = _new_is_nigth
            self.sampling_interval = (self.time[1] - self.time[0])

    def array_list(self):
        if type(self.time) == list:
            self.time = numpy.array(self.time)
            self.parameter = numpy.array(self.parameter)
            self.is_nigth = numpy.array(self.is_nigth)
        elif type(self.time) == numpy.ndarray:
            self.time = self.time.tolist()
            self.parameter = self.parameter.tolist()
            self.is_nigth = self.is_nigth.tolist()

zt_0_time = '2022-06-15T00:00:00.000000'
example = experiment(zt_0_time)
example.resample(3600)
example.array_list()
example.parameter = numpy.nan_to_num(example.parameter)

data = {'time': example.time, 'value': example.parameter, 'is_night': example.is_nigth}

ca = CycleAnalyzer(example.time, example.parameter, example.is_nigth)

ca.plot_actogram(step=example.sampling_interval)

print("DEBUG")