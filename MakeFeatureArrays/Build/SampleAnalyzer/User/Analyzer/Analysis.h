#ifndef analysis_Analysis_h
#define analysis_Analysis_h

#include "SampleAnalyzer/Process/Analyzer/AnalyzerBase.h"

namespace MA5
{
class Analysis : public AnalyzerBase
{
  INIT_ANALYSIS(Analysis,"Analysis")

 public:
  virtual bool Initialize(const MA5::Configuration& cfg, const std::map<std::string,std::string>& parameters);
  virtual void Finalize(const SampleFormat& summary, const std::vector<SampleFormat>& files);
  virtual bool Execute(SampleFormat& sample, const EventFormat& event);

 private:
 std::string outputFilename;
};
}

#endif
