#pragma once
// #include <cstdarg>
namespace Eloquent {
    namespace ML {
        namespace Port {
            class RandomForest {
                public:
                    /**
                    * Predict class for features vector
                    */
                    int predict(float *x) {
                        uint8_t votes[16] = { 0 };
                        // tree #1
                        if (x[9] <= 578.5) {
                            if (x[5] <= 614.5) {
                                if (x[1] <= 346.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[10] <= 1125.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 1221.0) {
                                if (x[2] <= 1412.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1558.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        // tree #2
                        if (x[5] <= 611.0) {
                            if (x[9] <= 578.0) {
                                if (x[10] <= 570.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[6] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1321.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        else {
                            if (x[2] <= 1303.5) {
                                if (x[6] <= 1404.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }

                            else {
                                if (x[11] <= 1284.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #3
                        if (x[5] <= 611.0) {
                            if (x[8] <= 575.0) {
                                if (x[2] <= 355.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[7] <= 1444.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1349.5) {
                                if (x[10] <= 1032.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1433.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #4
                        if (x[5] <= 583.0) {
                            if (x[7] <= 553.0) {
                                if (x[7] <= 218.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 551.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1338.5) {
                                if (x[5] <= 1437.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 1174.5) {
                                    votes[2] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #5
                        if (x[6] <= 604.0) {
                            if (x[6] <= 180.5) {
                                if (x[10] <= 554.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[6] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 315.5) {
                                    votes[10] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 1120.5) {
                                if (x[9] <= 1344.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[8] <= 1466.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        // tree #6
                        if (x[7] <= 574.5) {
                            if (x[11] <= 631.0) {
                                if (x[11] <= 251.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 822.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 534.0) {
                                if (x[5] <= 1407.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1250.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        // tree #7
                        if (x[7] <= 567.5) {
                            if (x[11] <= 591.5) {
                                if (x[3] <= 353.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 1103.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 571.0) {
                                if (x[6] <= 1414.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 1158.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #8
                        if (x[3] <= 559.0) {
                            if (x[11] <= 631.0) {
                                if (x[11] <= 251.0) {
                                    votes[8] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[4] <= 1336.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[7] <= 1349.5) {
                                if (x[9] <= 1227.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1813.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #9
                        if (x[7] <= 568.0) {
                            if (x[2] <= 452.5) {
                                if (x[7] <= 228.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 560.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 844.0) {
                                if (x[4] <= 1381.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 1975.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }
                        }

                        // tree #10
                        if (x[9] <= 592.5) {
                            if (x[6] <= 648.0) {
                                if (x[11] <= 1107.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[10] <= 1123.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 558.5) {
                                if (x[1] <= 1505.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[11] <= 1032.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #11
                        if (x[6] <= 595.0) {
                            if (x[9] <= 591.5) {
                                if (x[11] <= 521.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1159.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1342.5) {
                                if (x[7] <= 1423.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[8] <= 1172.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #12
                        if (x[8] <= 609.5) {
                            if (x[0] <= 420.5) {
                                if (x[8] <= 229.5) {
                                    votes[8] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 544.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 1222.5) {
                                if (x[4] <= 1297.0) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[9] <= 1085.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #13
                        if (x[9] <= 578.5) {
                            if (x[5] <= 611.0) {
                                if (x[1] <= 322.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 555.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[6] <= 528.5) {
                                if (x[1] <= 1197.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 454.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #14
                        if (x[7] <= 541.5) {
                            if (x[11] <= 591.5) {
                                if (x[4] <= 373.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 561.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 1216.5) {
                                if (x[1] <= 1592.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[10] <= 1122.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #15
                        if (x[7] <= 576.5) {
                            if (x[1] <= 504.0) {
                                if (x[7] <= 224.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 1246.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[6] <= 1378.5) {
                                if (x[1] <= 592.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[4] <= 551.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #16
                        if (x[7] <= 613.0) {
                            if (x[11] <= 591.5) {
                                if (x[0] <= 334.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1175.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 496.5) {
                                if (x[6] <= 1422.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[11] <= 1321.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        // tree #17
                        if (x[9] <= 591.5) {
                            if (x[6] <= 631.5) {
                                if (x[0] <= 337.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[8] <= 2037.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[6] += 1;
                                }
                            }
                        }

                        else {
                            if (x[5] <= 562.5) {
                                if (x[3] <= 552.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1191.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #18
                        if (x[9] <= 577.5) {
                            if (x[4] <= 551.0) {
                                if (x[11] <= 521.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[4] <= 1243.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[2] <= 525.5) {
                                if (x[1] <= 926.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1593.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #19
                        if (x[10] <= 610.0) {
                            if (x[7] <= 589.0) {
                                if (x[10] <= 118.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 1449.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[3] <= 537.0) {
                                if (x[5] <= 1175.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 446.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #20
                        if (x[6] <= 615.0) {
                            if (x[9] <= 578.0) {
                                if (x[4] <= 376.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1186.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[11] <= 1007.5) {
                                if (x[1] <= 1339.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1353.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #21
                        if (x[7] <= 569.0) {
                            if (x[4] <= 594.0) {
                                if (x[2] <= 355.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[11] <= 1029.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 1184.0) {
                                if (x[6] <= 1428.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1780.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[1] += 1;
                                }
                            }
                        }

                        // tree #22
                        if (x[11] <= 631.0) {
                            if (x[3] <= 558.0) {
                                if (x[6] <= 815.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 847.0) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[3] <= 482.0) {
                                if (x[8] <= 569.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1332.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #23
                        if (x[10] <= 602.0) {
                            if (x[5] <= 583.5) {
                                if (x[10] <= 118.0) {
                                    votes[8] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 1142.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 469.0) {
                                if (x[4] <= 513.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1413.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #24
                        if (x[7] <= 541.5) {
                            if (x[1] <= 434.5) {
                                if (x[4] <= 470.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1175.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[3] <= 522.0) {
                                if (x[6] <= 1428.0) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 558.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #25
                        if (x[6] <= 602.5) {
                            if (x[2] <= 549.5) {
                                if (x[10] <= 627.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 1765.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 487.0) {
                                if (x[11] <= 914.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 655.0) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #26
                        if (x[9] <= 741.0) {
                            if (x[4] <= 594.0) {
                                if (x[10] <= 559.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[6] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1245.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 478.5) {
                                if (x[6] <= 1457.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[11] <= 1017.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        // tree #27
                        if (x[11] <= 658.5) {
                            if (x[6] <= 610.5) {
                                if (x[11] <= 236.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1531.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1199.5) {
                                if (x[3] <= 452.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1966.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        // tree #28
                        if (x[10] <= 610.0) {
                            if (x[6] <= 613.5) {
                                if (x[2] <= 347.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 1242.0) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 545.5) {
                                if (x[3] <= 509.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1747.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #29
                        if (x[11] <= 631.0) {
                            if (x[6] <= 634.5) {
                                if (x[3] <= 399.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1751.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[3] <= 1155.5) {
                                if (x[4] <= 472.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[9] <= 1088.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #30
                        if (x[7] <= 565.5) {
                            if (x[11] <= 576.5) {
                                if (x[5] <= 371.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 460.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[7] <= 1343.5) {
                                if (x[4] <= 551.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[7] <= 1838.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        // tree #31
                        if (x[9] <= 578.0) {
                            if (x[3] <= 538.5) {
                                if (x[11] <= 791.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 1232.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 502.0) {
                                if (x[5] <= 506.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1556.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #32
                        if (x[5] <= 602.5) {
                            if (x[3] <= 617.5) {
                                if (x[11] <= 576.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 2004.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1339.0) {
                                if (x[7] <= 1350.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1272.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #33
                        if (x[10] <= 615.0) {
                            if (x[5] <= 586.5) {
                                if (x[0] <= 324.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 1329.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1180.0) {
                                if (x[2] <= 1300.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1407.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #34
                        if (x[10] <= 604.5) {
                            if (x[6] <= 613.5) {
                                if (x[2] <= 340.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[7] <= 1214.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 553.0) {
                                if (x[3] <= 1333.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1655.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }
                        }

                        // tree #35
                        if (x[11] <= 631.0) {
                            if (x[8] <= 632.5) {
                                if (x[3] <= 399.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[4] <= 1182.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[2] <= 492.5) {
                                if (x[5] <= 513.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1375.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #36
                        if (x[9] <= 591.5) {
                            if (x[4] <= 610.0) {
                                if (x[1] <= 345.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 1142.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 492.0) {
                                if (x[3] <= 1355.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1788.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        // tree #37
                        if (x[10] <= 610.0) {
                            if (x[7] <= 626.0) {
                                if (x[8] <= 232.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 1455.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 1207.5) {
                                if (x[4] <= 1301.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[10] <= 1268.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }
                        }

                        // tree #38
                        if (x[7] <= 622.5) {
                            if (x[1] <= 350.5) {
                                if (x[10] <= 464.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[4] <= 628.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 843.5) {
                                if (x[4] <= 1437.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1278.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        // tree #39
                        if (x[4] <= 551.0) {
                            if (x[8] <= 575.5) {
                                if (x[10] <= 1097.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[7] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 1293.0) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[6] <= 1378.0) {
                                if (x[2] <= 1378.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }

                            else {
                                if (x[10] <= 1248.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #40
                        if (x[9] <= 573.5) {
                            if (x[9] <= 227.5) {
                                if (x[4] <= 594.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[9] <= 335.5) {
                                    votes[10] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }
                        }

                        else {
                            if (x[4] <= 482.5) {
                                if (x[3] <= 523.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[8] <= 1344.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        // tree #41
                        if (x[9] <= 578.5) {
                            if (x[5] <= 614.5) {
                                if (x[9] <= 107.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1969.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[1] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 558.5) {
                                if (x[2] <= 1430.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[6] <= 1283.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        // tree #42
                        if (x[8] <= 601.0) {
                            if (x[11] <= 585.0) {
                                if (x[0] <= 325.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 564.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1194.5) {
                                if (x[3] <= 498.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1572.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #43
                        if (x[9] <= 577.5) {
                            if (x[4] <= 594.0) {
                                if (x[0] <= 325.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[5] <= 823.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 614.0) {
                                if (x[2] <= 1568.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[3] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 1556.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #44
                        if (x[5] <= 611.5) {
                            if (x[8] <= 575.5) {
                                if (x[8] <= 229.5) {
                                    votes[8] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 553.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1340.5) {
                                if (x[5] <= 1435.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[4] <= 1311.0) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #45
                        if (x[10] <= 597.0) {
                            if (x[0] <= 409.5) {
                                if (x[11] <= 576.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 542.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 505.5) {
                                if (x[4] <= 482.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 1785.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #46
                        if (x[7] <= 574.0) {
                            if (x[11] <= 631.0) {
                                if (x[1] <= 343.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1159.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 502.5) {
                                if (x[6] <= 1377.0) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[8] <= 1134.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #47
                        if (x[7] <= 622.5) {
                            if (x[11] <= 555.5) {
                                if (x[2] <= 351.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[0] <= 463.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[0] <= 843.5) {
                                if (x[7] <= 1378.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[9] <= 978.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #48
                        if (x[5] <= 600.0) {
                            if (x[11] <= 519.5) {
                                if (x[10] <= 118.0) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[9] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 570.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[2] <= 1375.0) {
                                if (x[1] <= 1194.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[3] <= 1350.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }
                        }

                        // tree #49
                        if (x[10] <= 610.0) {
                            if (x[1] <= 379.5) {
                                if (x[5] <= 478.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[1] <= 614.0) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 1164.0) {
                                if (x[7] <= 1413.5) {
                                    votes[6] += 1;
                                }

                                else {
                                    votes[5] += 1;
                                }
                            }

                            else {
                                if (x[11] <= 948.5) {
                                    votes[4] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #50
                        if (x[9] <= 573.5) {
                            if (x[6] <= 653.0) {
                                if (x[0] <= 328.5) {
                                    votes[9] += 1;
                                }

                                else {
                                    votes[8] += 1;
                                }
                            }

                            else {
                                if (x[4] <= 1478.5) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        else {
                            if (x[1] <= 592.5) {
                                if (x[6] <= 1360.5) {
                                    votes[7] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }

                            else {
                                if (x[9] <= 1311.5) {
                                    votes[5] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // return argmax of votes
                        uint8_t classIdx = 0;
                        float maxVotes = votes[0];

                        for (uint8_t i = 1; i < 16; i++) {
                            if (votes[i] > maxVotes) {
                                classIdx = i;
                                maxVotes = votes[i];
                            }
                        }

                        return classIdx;
                    }

                protected:
                };
            }
        }
    }