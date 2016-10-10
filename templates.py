suspect_input_template = """\
# Input file for Suspect. This file specifies input parameters to create
# a consistent mass spectrum for MSSM particles. The Suspect2 output is decayed
# in the program SUSY-HIT, and the output of SUSY-HIT can be fed into MadGraph as
# a param_card.dat
#
Block MODSEL
    1   0 # General MSSM with low scale input
# 
Block SU_ALGO
    2   21  # 2-loop RGE
    3   1   # g_1(gut) = g_2(gut) is consistently calculated from input
    4   2   # RGE accuracy: accurate (but slightly slower)
    6   0   # mA_pole and \mu(EWSB) input
    7   1   # No radiative corrections in squarks and gauginos
    8   1   # EWSB scale=sqrt(mt_L*mt_R)
    9   2   # Final spectrum accuracy: 0.01%
    10  2   # one loop + Dominant DSVZ 2-loop r.c. to Higgs mass
#
Block SMINPUTS
    1   127.934
    3   0.1172
    5   4.25      # bottom quark pole mass
    6   172.5     # top quark pole mass
    7   1.7771    # tau lepton pole mass
#
Block EXTPAR
    1   {bino_mass}   # M_1 (Bino mass)
    2   {wino_mass}   # M_2 (Wino mass)
    3   14.0E+03      # M_3 (Gluino mass)
    11  2700.         # A_t
    12  0.0
    13  0.0
    14  0.0
    15  0.0
    16  0.0
    23  {higgsino_mass} # mu(EWSB) - Higgsino mass
    25  {tan_beta}  # tanbeta (MZ)
    26  8.0E+03 
    31  8.0E+03
    32  8.0E+03
    33  8.0E+03
    34  8.0E+03
    35  8.0E+03
    36  8.0E+03
    41  8.0E+03
    42  8.0E+03
    43  8.0E+03
    44  8.0E+03
    45  8.0E+03
    46  8.0E+03
    47  8.0E+03
    48  8.0E+03
    49  8.0E+03"""
