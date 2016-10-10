from Analysis import Analysis
from Cut import Cut

class CutAndCountAnalysis(Analysis):

    def __init__(self):
        self.histos = []
        self.cuts = []
        self.region_names = ['Signal']
    
    def write_execute_block(self, f, m_R, m_T_R):
        met_filter = Cut(
            name = "MET",
            cpp_condition = "met > 400.",
            signal_region = "Signal"
        )

        at_least_one_lepton = Cut(
            name = "at least one lepton",
            cpp_condition = "leptons.size() != 0",
            signal_region = "Signal"
        )

        lepton_trigger = Cut(
            name = "Lepton trigger",
            cpp_condition = "leptons[0]->pt() > 100.",
            signal_region = "Signal"
        )

        pt_eta_cut = Cut(
            name = "pt_eta_cuts",
            cpp_condition = "pt_eta_condition == true",
            signal_region = "Signal"
        )

        two_leptons = Cut(
            name = "2 leptons",
            cpp_condition = "leptons.size() == 2",
            signal_region = "Signal"
        )

        SF_leptons = Cut(
            name = "SF leptons",
            cpp_condition = "electrons.size() != 1",
            signal_region = "Signal"
        )

        OS_leptons = Cut(
            name = "OS leptons",
            cpp_condition = "leptons[0]->charge() != leptons[1]->charge()",
            signal_region = "Signal"
        )

        two_b_jets = Cut(
            name = "2 b jets",
            cpp_condition = "b_jets.size() > 1",
            signal_region = "Signal"
        )

        # Invariant mass of Z candidate
        m_ll = Cut(
            name = "m_ll", 
            cpp_condition = "Z_candidate.m() > 85. and Z_candidate.m() < 95.", 
            signal_region = "Signal"
        )

        # Invariant mass of higgs candidate
        m_bb = Cut(
            name = "m_bb", 
            cpp_condition = "h_candidate.m() > 75. and h_candidate.m() < 150.", 
            signal_region = "Signal"
        )

        def m_R_cut(m_R):
            return Cut(
                name = "m_R", 
                cpp_condition = "m_R > {}".format(str(m_R)), 
                signal_region = "Signal"
            )

        def m_T_R_cut(m_T_R):
            return Cut(
                name = "m_T_R", 
                cpp_condition = "m_T_R > {}".format(str(m_T_R)), 
                signal_region = "Signal"
            )

        # PT and Eta conditions
        pt_eta_condition = """\

    bool pt_eta_condition = true;

    for (unsigned int i = 0; i < leptons.size(); i++) {
        if (leptons[i]->pt() < 15. or fabs(leptons[i]->eta()) > 2.5) pt_eta_condition = false;
    }

    for (unsigned int i = 0; i < b_jets.size(); i++) {
        if (b_jets[i]->pt() < 30. or fabs(b_jets[i]->eta()) > 2.5) pt_eta_condition = false;
    }

    """

        # MET definition
        met_definition = """\
    RecParticleFormat met_particle = event.rec()->MET();
    double met = met_particle.pt();
    MAVector3 met_vector = met_particle.momentum().Vect(); 
    """

        # Invariant mass definitions
        invariant_mass_definitions = """\
    // Z and h candidates
    ParticleBaseFormat Z_candidate = leptons[0]->momentum()+leptons[1]->momentum();
    ParticleBaseFormat h_candidate = b_jets[0]->momentum() + b_jets[1]->momentum();
    """

        razor_variable_definitions = """\

    ParticleBaseFormat q_1, q_2;
    q_1 = Z_candidate.momentum(); q_2 = h_candidate.momentum();

    MAVector3 q_12T = MAVector3(Z_candidate.px()+h_candidate.px(),
                                Z_candidate.py()+h_candidate.py(),
                                0.);

    double E_1, E_2, q_1z, q_2z, m_R, m_T_R, R_squared;

    E_1 = Z_candidate.e(); E_2 = h_candidate.e();
    q_1z = Z_candidate.pz(); q_2z = h_candidate.pz();

    m_R = sqrt( pow(E_1 + E_2, 2) - pow(q_1z + q_2z, 2)); 
    m_T_R = sqrt(.5*(met*(q_1.pt()+q_2.pt()) - met_vector.Dot(q_12T)));
    R_squared = pow(m_T_R/m_R, 2); 

    """
        self.write_pre_execute(f)

        at_least_one_lepton.write(f, self.cuts)
        lepton_trigger.write(f, self.cuts)

        f.write(pt_eta_condition)
        pt_eta_cut.write(f, self.cuts)

        two_leptons.write(f, self.cuts)
        SF_leptons.write(f, self.cuts)
        OS_leptons.write(f, self.cuts)
        two_b_jets.write(f, self.cuts)

        f.write(met_definition)
        met_filter.write(f, self.cuts)

        f.write(invariant_mass_definitions)
        m_ll.write(f, self.cuts)
        m_bb.write(f, self.cuts)

        f.write(razor_variable_definitions)
        m_R_cut(m_R).write(f, self.cuts)
        m_T_R_cut(m_T_R).write(f, self.cuts)
        f.write("\treturn true;\n")
        f.write("}\n\n")

    def write_analysis_cpp(self, directory, m_R, m_T_R):
        analysis_cpp_file = directory+'/Build/SampleAnalyzer/User/Analyzer/Analysis.cpp'
        with open(analysis_cpp_file, 'w') as f:
            self.write_includes(f)
            self.write_execute_block(f, m_R, m_T_R)
            self.write_initialize_block(f)
            self.write_finalize_block(f)
