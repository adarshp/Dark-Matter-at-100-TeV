# Create background directories for the DM project

processes='tbW bbWW tt_fully_leptonic'
dm='/rsgrps/shufang/Dark-Matter-at-100-TeV'

target_dir='/extra/adarsh'

cd $target_dir

for process in $processes
do
    rm -rf $process
    mg5 $dm/Cards/mg5_proc_cards/$process'_proc_card.dat'
    cp $dm/Cards/delphes_cards/momentumResolutionVsP.tcl $process/Cards/
    cp $dm/Cards/delphes_cards/muonMomentumResolutionVsP.tcl $process/Cards/
    cp $dm/Cards/delphes_cards/FCChh.tcl $process/Cards/delphes_card.dat
    cp $dm/Cards/run_cards/run_card_bg.dat $process/Cards/run_card.dat
    cp $dm/bg_me5_script.txt $process/
done
