class Cut:
    def __init__(self, name, cpp_condition, signal_region):
        self.name = name
        self.cpp_condition = cpp_condition
        self.signal_region = signal_region
    def write(self, f, cut_list):
        f.write('\tif(!Manager()->ApplyCut({}, "{}")) return false;\n'.format(self.cpp_condition, self.name))
        cut_list.append(self)
