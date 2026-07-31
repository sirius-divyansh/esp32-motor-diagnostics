#pragma once
#include <cstdarg>
namespace Eloquent {
    namespace ML {
        namespace Port {
            class RandomForest {
                public:
                    /**
                    * Predict class for features vector
                    */
                    int predict(float *x) {
                        uint8_t votes[3] = { 0 };
                        // tree #1
                        if (x[108] <= 41.51381301879883) {
                            if (x[177] <= 15.817848205566406) {
                                if (x[1796] <= 0.6191550642251968) {
                                    votes[2] += 1;
                                }

                                else {
                                    votes[0] += 1;
                                }
                            }

                            else {
                                if (x[39] <= 98.15486145019531) {
                                    if (x[4262] <= 2.5613383054733276) {
                                        votes[0] += 1;
                                    }

                                    else {
                                        if (x[1506] <= 9.11919641494751) {
                                            votes[2] += 1;
                                        }

                                        else {
                                            votes[0] += 1;
                                        }
                                    }
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #2
                        if (x[1213] <= 1.8247786164283752) {
                            votes[2] += 1;
                        }

                        else {
                            if (x[46] <= 76.51961135864258) {
                                if (x[2808] <= 1.7009254097938538) {
                                    votes[0] += 1;
                                }

                                else {
                                    if (x[4324] <= 1.2502796053886414) {
                                        votes[0] += 1;
                                    }

                                    else {
                                        votes[2] += 1;
                                    }
                                }
                            }

                            else {
                                votes[1] += 1;
                            }
                        }

                        // tree #3
                        if (x[31] <= 422.02960205078125) {
                            if (x[7] <= 245.47882843017578) {
                                votes[2] += 1;
                            }

                            else {
                                votes[0] += 1;
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #4
                        if (x[129] <= 60.02438545227051) {
                            if (x[6] <= 172.73455047607422) {
                                votes[0] += 1;
                            }

                            else {
                                votes[2] += 1;
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #5
                        if (x[512] <= 36.26552963256836) {
                            if (x[25] <= 120.77637481689453) {
                                if (x[1607] <= 4.802602529525757) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }

                            else {
                                if (x[194] <= 13.647602558135986) {
                                    votes[2] += 1;
                                }

                                else {
                                    votes[1] += 1;
                                }
                            }
                        }

                        else {
                            if (x[196] <= 12.36997938156128) {
                                if (x[3074] <= 3.4047725200653076) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }

                            else {
                                votes[1] += 1;
                            }
                        }

                        // tree #6
                        if (x[175] <= 23.987889289855957) {
                            if (x[4270] <= 1.2715226411819458) {
                                votes[2] += 1;
                            }

                            else {
                                if (x[28] <= 74.55624771118164) {
                                    if (x[4103] <= 3.441781997680664) {
                                        votes[0] += 1;
                                    }

                                    else {
                                        votes[2] += 1;
                                    }
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #7
                        if (x[20] <= 154.09494018554688) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[149] <= 47.64588928222656) {
                                votes[2] += 1;
                            }

                            else {
                                votes[1] += 1;
                            }
                        }

                        // tree #8
                        if (x[19] <= 231.61173248291016) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[9] <= 784.9748840332031) {
                                votes[2] += 1;
                            }

                            else {
                                votes[1] += 1;
                            }
                        }

                        // tree #9
                        if (x[100] <= 62.95415496826172) {
                            if (x[4741] <= 2.85139000415802) {
                                if (x[4484] <= 3.4434173107147217) {
                                    if (x[2156] <= 3.859116315841675) {
                                        votes[0] += 1;
                                    }

                                    else {
                                        votes[2] += 1;
                                    }
                                }

                                else {
                                    if (x[1729] <= 2.1102222204208374) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[0] += 1;
                                    }
                                }
                            }

                            else {
                                votes[2] += 1;
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #10
                        if (x[153] <= 16.302932739257812) {
                            if (x[4677] <= 2.5284727811813354) {
                                if (x[3728] <= 2.7586145401000977) {
                                    votes[2] += 1;
                                }

                                else {
                                    votes[0] += 1;
                                }
                            }

                            else {
                                if (x[845] <= 4.806986093521118) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #11
                        if (x[22] <= 76.57067108154297) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 637.4955444335938) {
                                votes[2] += 1;
                            }

                            else {
                                votes[1] += 1;
                            }
                        }

                        // tree #12
                        if (x[30] <= 122.48767471313477) {
                            if (x[6] <= 172.73455047607422) {
                                votes[0] += 1;
                            }

                            else {
                                votes[2] += 1;
                            }
                        }

                        else {
                            if (x[196] <= 11.447608947753906) {
                                votes[2] += 1;
                            }

                            else {
                                votes[1] += 1;
                            }
                        }

                        // tree #13
                        if (x[85] <= 67.28131103515625) {
                            if (x[4947] <= 1.6451881527900696) {
                                if (x[3202] <= 0.4939471036195755) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }

                            else {
                                if (x[33] <= 252.89401245117188) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #14
                        if (x[3] <= 228.447998046875) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[9] <= 784.6535949707031) {
                                votes[2] += 1;
                            }

                            else {
                                votes[1] += 1;
                            }
                        }

                        // tree #15
                        if (x[92] <= 48.57168006896973) {
                            if (x[4373] <= 1.823437511920929) {
                                if (x[2817] <= 1.0275295972824097) {
                                    votes[0] += 1;
                                }

                                else {
                                    if (x[4657] <= 3.827185273170471) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[0] += 1;
                                    }
                                }
                            }

                            else {
                                if (x[3524] <= 1.31050705909729) {
                                    votes[2] += 1;
                                }

                                else {
                                    votes[0] += 1;
                                }
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #16
                        if (x[98] <= 35.42958641052246) {
                            if (x[1876] <= 1.2805668115615845) {
                                votes[0] += 1;
                            }

                            else {
                                if (x[3638] <= 0.7057934701442719) {
                                    votes[0] += 1;
                                }

                                else {
                                    if (x[601] <= 10.806224822998047) {
                                        if (x[764] <= 1.9218088388442993) {
                                            votes[0] += 1;
                                        }

                                        else {
                                            votes[2] += 1;
                                        }
                                    }

                                    else {
                                        if (x[2124] <= 4.630252838134766) {
                                            votes[2] += 1;
                                        }

                                        else {
                                            votes[0] += 1;
                                        }
                                    }
                                }
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #17
                        if (x[148] <= 15.218347072601318) {
                            if (x[2369] <= 2.253847122192383) {
                                if (x[3168] <= 1.1357465982437134) {
                                    if (x[1506] <= 6.396358966827393) {
                                        votes[0] += 1;
                                    }

                                    else {
                                        votes[2] += 1;
                                    }
                                }

                                else {
                                    votes[0] += 1;
                                }
                            }

                            else {
                                if (x[18] <= 194.46399688720703) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #18
                        if (x[69] <= 112.94015884399414) {
                            if (x[4098] <= 3.0585564374923706) {
                                if (x[11] <= 239.060791015625) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }

                            else {
                                votes[2] += 1;
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #19
                        if (x[133] <= 10.695657730102539) {
                            if (x[9] <= 593.6820373535156) {
                                votes[0] += 1;
                            }

                            else {
                                votes[2] += 1;
                            }
                        }

                        else {
                            votes[1] += 1;
                        }

                        // tree #20
                        if (x[151] <= 24.557451248168945) {
                            if (x[2455] <= 1.777661144733429) {
                                if (x[19] <= 231.2890396118164) {
                                    votes[0] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }

                            else {
                                if (x[752] <= 6.198435544967651) {
                                    votes[2] += 1;
                                }

                                else {
                                    votes[0] += 1;
                                }
                            }
                        }

                        else {
                            if (x[4606] <= 4.257633090019226) {
                                votes[1] += 1;
                            }

                            else {
                                votes[2] += 1;
                            }
                        }

                        // return argmax of votes
                        uint8_t classIdx = 0;
                        float maxVotes = votes[0];

                        for (uint8_t i = 1; i < 3; i++) {
                            if (votes[i] > maxVotes) {
                                classIdx = i;
                                maxVotes = votes[i];
                            }
                        }

                        return classIdx;
                    }

                    /**
                    * Predict readable class name
                    */
                    const char* predictLabel(float *x) {
                        return idxToLabel(predict(x));
                    }

                    /**
                    * Convert class idx to readable name
                    */
                    const char* idxToLabel(uint8_t classIdx) {
                        switch (classIdx) {
                            case 0:
                            return "Healthy";
                            case 1:
                            return "Electrical Fault";
                            case 2:
                            return "Mechanical Fault";
                            default:
                            return "Houston we have a problem";
                        }
                    }

                protected:
                };
            }
        }
    }