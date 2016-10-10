class Histo:
    def __init__(self, name, xmin, xmax, nbins, signal_region):
        self.name = name
        self.xmin = xmin
        self.xmax = xmax
        self.nbins = nbins
        self.signal_region = signal_region
        histo_properties = ['"{}"'.format(self.name), 
                            str(self.xmin),
                            str(self.xmax),
                            '"{}"'.format(str(self.signal_region))]
        self.histo_properties_string = ",".join(histo_properties)
