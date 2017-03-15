#include "SampleAnalyzer/User/Analyzer/Analysis.h"
using namespace MA5;
using namespace std;

// -----------------------------------------------------------------------------
// Initialize
// function called one time at the beginning of the analysis
// -----------------------------------------------------------------------------

bool Analysis::Initialize(const MA5::Configuration& cfg, const std::map<std::string,std::string>& parameters)
{
  cout << "BEGIN Initialization" << endl;
  // initialize variables, histos
  PHYSICS -> recConfig().Reset();
  Manager()->AddRegionSelection("Signal");
  Manager()->AddCut("At least one lepton", "Signal");
  Manager()->AddCut("Lepton trigger", "Signal");
  Manager()->AddCut("2 leptons", "Signal");
  Manager()->AddCut("SF leptons", "Signal");
  Manager()->AddCut("OS leptons", "Signal");
  Manager()->AddCut("2 b jets", "Signal");
  outputFilename = "../Output/"+cfg.GetInputName()+"/feature_array.txt";
  std::ofstream myfile; myfile.open(outputFilename.c_str(), std::ios::trunc);

  myfile << "ptl1" << ',';
  myfile << "ptl2" << ',';
  myfile << "ptb1" << ',';
  myfile << "ptb2" << ',';
  myfile << "mll" << ',';
  myfile << "mbb" << ',';
  myfile << "mllbb" << ',';
  myfile << "mR" << ',';
  myfile << "mTR" << ',';
  myfile << "MET" << ',';
  myfile << "THT" << '\n';
  myfile.close();

  cout << "END   Initialization" << endl;
  return true;
}

// -----------------------------------------------------------------------------
// Execute
// function called each time one event is read
// -----------------------------------------------------------------------------
bool Analysis::Execute(SampleFormat& sample, const EventFormat& event)
{
    double myEventWeight = 1.;
    Manager()->InitializeForNewEvent(myEventWeight);

    // Declaration of all particle containers
    std::vector<const RecLeptonFormat*> electrons, muons, leptons;
    std::vector<const RecJetFormat*> jets, b_jets;

    // Clear particle containers
    electrons.clear(); muons.clear(); leptons.clear();
    jets.clear(); b_jets.clear();

    //Filling all particle containers
    for (unsigned int i = 0; i < event.rec()->electrons().size(); i++) {
        const RecLeptonFormat* electron = &(event.rec()->electrons()[i]);
        if (electron->pt() > 15. and fabs(electron->eta()) < 2.5) {
            electrons.push_back(electron); leptons.push_back(electron);
        }
    }
    for (unsigned int i = 0; i < event.rec()->muons().size(); i++) {
        const RecLeptonFormat* muon = &(event.rec()->muons()[i]);
        if (muon->pt() > 15. and fabs(muon->eta() < 2.5)) {
            muons.push_back(muon); leptons.push_back(muon);
        }
    }
    for (unsigned int i = 0; i < event.rec()->jets().size(); i++) {
        const RecJetFormat* jet = &(event.rec()->jets()[i]);
        if (jet->pt() > 30. and fabs(jet->eta() < 2.5)) {
            jets.push_back(jet);
            if (jet->btag() == true) b_jets.push_back(jet);
        }
    }

    // Sorting jets and leptons by PT
    SORTER->sort(leptons, PTordering);
    SORTER->sort(jets, PTordering);
    SORTER->sort(b_jets, PTordering);

    // Trigger and identification cuts
    if(!Manager()->ApplyCut(leptons.size() != 0, "At least one lepton")) return false;
    double ptl1 = leptons[0]->pt();
    if(!Manager()->ApplyCut(ptl1 > 100., "Lepton trigger")) return false;
    if(!Manager()->ApplyCut(leptons.size() == 2, "2 leptons")) return false;
    if(!Manager()->ApplyCut(electrons.size() !=1, "SF leptons")) return false;
    if(!Manager()->ApplyCut(leptons[0]->charge() != leptons[1]->charge(), "OS leptons")) return false;
    if(!Manager()->ApplyCut(b_jets.size() == 2, "2 b jets")) return false;

    double ptl2 = leptons[1]->pt();

    // MET definition
    RecParticleFormat met_particle = event.rec()->MET();
    MAVector3 met_vector = met_particle.momentum().Vect();
    double MET = met_particle.pt();
    
    // Scalar sum of hadronic transverse energy
    double THT = event.rec()->THT();
    
    // Define Z and h candidates
    ParticleBaseFormat Z_candidate = leptons[0]->momentum() + leptons[1]-> momentum();
    ParticleBaseFormat h_candidate = b_jets[0]->momentum() + b_jets[1]-> momentum();
    ParticleBaseFormat Zh_candidate = Z_candidate+h_candidate;

    double mll = Z_candidate.m();
    double mbb = h_candidate.m();
    double mllbb = Zh_candidate.m();
    double ptb1 = b_jets[0]->pt();
    double ptb2 = b_jets[1]->pt();

    // Calculating razor variables
    ParticleBaseFormat q1 = Z_candidate.momentum();
    ParticleBaseFormat q2 = h_candidate.momentum();

    MAVector3 q12T = MAVector3(Z_candidate.px()+h_candidate.px(),
                               Z_candidate.py()+h_candidate.py(),
                               0.);
    double E1 = Z_candidate.e();
    double E2 = h_candidate.e();

    double q1z = Z_candidate.pz();
    double q2z = h_candidate.pz();

    double E12 = E1+E2;
    double q12z = q1z+q2z;
    double mR = sqrt(pow(E12,2)-pow(q12z,2));
    double q12pt = q1.pt()+q2.pt();
    double mTR = sqrt(.5*(MET*(q12pt)-met_vector.Dot(q12T)));

    std::ofstream myfile; myfile.open(outputFilename.c_str(), std::ios::app);
    myfile << ptl1 << ',';
    myfile << ptl2 << ',';
    myfile << ptb1 << ',';
    myfile << ptb2 << ',';
    myfile << mll << ',';
    myfile << mbb << ',';
    myfile << mllbb << ',';
    myfile << mR << ',';
    myfile << mTR << ',';
    myfile << MET << ',';
    myfile << THT << '\n';
    myfile.close();
    
    return true;
}

// -----------------------------------------------------------------------------
// Finalize
// function called one time at the end of the analysis
// -----------------------------------------------------------------------------
void Analysis::Finalize(const SampleFormat& summary, const std::vector<SampleFormat>& files)
{
    return;
}
