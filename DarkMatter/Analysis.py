class Analysis:

    def __init__(self):
        self.cuts = None
        self.histos = None
        self.region_names = None
        
    def write_includes(self, f):
        f.write('#include "SampleAnalyzer/User/Analyzer/Analysis.h"\n')
        f.write('using namespace MA5;\n\n')

    def write_begin_initialize(self, f):
        f.write('bool Analysis::Initialize(const MA5::Configuration& cfg, const std::map<std::string,std::string>& parameters) {\n')
        f.write("\tPHYSICS->recConfig().Reset();\n")

        for name in self.region_names:
            f.write('\tManager()->AddRegionSelection("{}");\n'.format(name))

        for cut in self.cuts:
            f.write('\tManager()->AddCut("{}", "Signal");\n'.format(cut.name))

        for histo in self.histos:
            f.write('\tManager()->AddHisto({});\n'.format(histos.histo_properties_string))

    def write_end_initialize(self, f):
        f.write("\treturn true;\n")
        f.write("}\n\n")

    def write_initialize_block(self, f):
        self.write_begin_initialize(f)
        self.write_end_initialize(f)

    def write_pre_execute(self, f):
        f.write("""\
        bool Analysis::Execute(SampleFormat& sample, const EventFormat& event) {
            double myEventWeight = 1.;
            Manager()->InitializeForNewEvent(myEventWeight);

            // Declaration of all containers
            std::vector<const RecLeptonFormat*> electrons, muons, leptons;
            std::vector<const RecJetFormat*> jets, b_jets;

            // Clear particle containers

            electrons.clear();
            muons.clear(); 
            leptons.clear();
            jets.clear(); 
            b_jets.clear();

            // Filling all the containers
            for (unsigned int i = 0; i < event.rec()->electrons().size(); i++) {
                const RecLeptonFormat* electron = &(event.rec()->electrons()[i]);
                if (electron->pt() > 15. and fabs(electron->eta()) < 2.5) {
                    electrons.push_back(electron);
                    leptons.push_back(electron);
                }
            }

            for (unsigned int i = 0; i < event.rec()->muons().size(); i++) {
                const RecLeptonFormat* muon = &(event.rec()->muons()[i]);
                if (muon->pt() > 15. and fabs(muon->eta()) < 2.5) {
                    muons.push_back(muon);
                    leptons.push_back(muon);
                }
            }

            for (unsigned int i = 0; i < event.rec()->jets().size(); i++) {
                const RecJetFormat* jet = &(event.rec()->jets()[i]);
                jets.push_back(jet);
                if (jet->btag() == true and jet->pt() > 30. and fabs(jet->eta()) < 2.5) {
                    b_jets.push_back(jet);
                }
            }

            // Sorting jets and leptons by PT
            SORTER->sort(jets, PTordering);
            SORTER->sort(leptons, PTordering);
            SORTER->sort(b_jets, PTordering);

        """)

    def write_begin_finalize(self, f):
        f.write('void Analysis::Finalize(const SampleFormat& summary, const std::vector<SampleFormat>& files) {\n')

    def write_end_finalize(self, f):
        f.write('\treturn;\n')
        f.write('}\n\n')
    
    def write_finalize_block(self, f):
        self.write_begin_finalize(f)
        self.write_end_finalize(f)

    def write_analysis_cpp(self, dirname):
        analysis_cpp_file = dirname+'/Build/SampleAnalyzer/User/Analyzer/Analysis.cpp'

        with open(analysis_cpp_file, 'w') as f:
            self.write_includes(f)
            self.write_execute_block(f)
            self.write_initialize_block(f)
            self.write_finalize_block(f)
