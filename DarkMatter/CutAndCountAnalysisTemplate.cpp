#include "SampleAnalyzer/User/Analyzer/Analysis.h"
using namespace MA5;
bool Analysis::Initialize(const MA5::Configuration& cfg, 
                          const std::map<std::string,std::string>& parameters) {
  PHYSICS->recConfig().Reset();
\tManager()->AddRegionSelection("{}");\n
\tManager()->AddCut("{}", "Signal");\n
\tManager()->AddHisto({});\n
\treturn true;\n
}\n\n

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


