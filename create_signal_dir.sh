# Create signal directory for the DM project

dm=`pwd`
target_dir='/extra/adarsh/'
mg5='/home/u13/adarsh/MG5_aMC_v2_6_0/bin/mg5_aMC'

cd $target_dir

process='higgsino_NLSP_bino_LSP'
rm -rf $process
$mg5 $dm/Cards/mg5_proc_cards/$process'.dat'
cp $dm/Cards/delphes_cards/momentumResolutionVsP.tcl $process/Cards/
cp $dm/Cards/delphes_cards/muonMomentumResolutionVsP.tcl $process/Cards/
cp $dm/Cards/delphes_cards/FCChh.tcl $process/Cards/delphes_card.dat
cp $dm/Cards/run_cards/run_card.dat $process/Cards/run_card.dat

cd $dm
