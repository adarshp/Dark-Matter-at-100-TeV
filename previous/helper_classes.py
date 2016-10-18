from helper_functions import cd, razor_combinations, convert_SAF_to_XML
import pandas as pd
import untangle

class Counter:
    def __init__(self, counter_object):
        self.name = counter_object.cdata.split('\n')[1].split('\"')[1]
        self.nevents = int(counter_object.cdata.split('\n')[2].split(' ')[0])

class OriginalEvents:

    def __init__(self, process):
        self.dataset_name = process.name
        self.m_R = str(0)
        self.m_T_R = str(0)
        self.events = self.set_events()

    def set_events(self):
        filename = '/'.join(['CutAndCountAnalysis', 'Output', self.dataset_name, 
            self.m_R+'_GeV_m_R_'+self.m_T_R+'_GeV_m_T_R', 'Cutflows', 'Signal'])
        convert_SAF_to_XML(filename+'.saf')
        xml_filepath = filename+'.xml'
        SAF_objects = (untangle.parse(xml_filepath)).root
        initial_counter = SAF_objects.InitialCounter
        counter_objects = SAF_objects.Counter
        counter_objects.insert(0, initial_counter)

        counters =  [Counter(counter_object) for counter_object in counter_objects]
        df = pd.DataFrame(index = [counter.name for counter in counters])
        df[self.dataset_name] = [counter.nevents for counter in counters]

        return df
   
class SkimmedEvents(OriginalEvents):
    def __init__(self, process, razor_combo):
        self.dataset_name = process.name+'_skimmed'
        self.m_R = str(int(razor_combo[0]))
        self.m_T_R = str(int(razor_combo[1]))
        self.events = self.set_events()

class Cut:
    def __init__(self, name, cpp_condition, signal_region):
        self.name = name
        self.cpp_condition = cpp_condition
        self.signal_region = signal_region
    def write(self, f, cut_list):
        f.write('\tif(!Manager()->ApplyCut({}, "{}")) return false;\n'.format(self.cpp_condition, self.name))
        cut_list.append(self)
