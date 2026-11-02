# WP8 — fixed preregistered contrasts

Status: COMPLETED

[E] Preregistration SHA-256: 15fd44322e73c281b85d173ac51fbfc631415b07a152f8a3041ae5892d32c779
[E] Script SHA-256: e678102b5e9448c1b0f4182391036b91e898389e958fc8472c7578897eb2696e

[A] One fixed 113-feature LightGBM candidate (frozen 87 + 26). No tuning, early stopping, blending or target encoding.
[E] 50 complete classifier fits: 30 inner diagnostic, 10 development, 10 outer; 10 complete sigmoid fits. Baseline reused: 30 inner and 10 outer caches; baseline refits: 0.
[E] 150,000 repeated outer OOF rows; 75,000 unique customers, each twice. No new test look or original calibration-policy feature processing.
[A] Policy uses unchanged numeric tau=1.711493684172072 for both models; deployment prior 0.02 is hypothetical. Value limits and peer/category references are fit-training-only.

## Equal-weight outer mean metrics

| Metric | Candidate | Cached baseline | Paired difference |
|---|---:|---:|---:|
| auc | 0.696313030947 | 0.696036977709 | 0.000276053237653 |
| value_capture | 0.296220682858 | 0.295874731995 | 0.000345950862391 |
| contact_share | 0.0988745824709 | 0.0983889298536 | 0.000485652617297 |
| baseline_tail_brier | 0.044442724643 | 0.0444613580253 | -1.86333823083e-05 |
| baseline_tail_logloss | 0.182828414337 | 0.182892647722 | -6.42333851281e-05 |
| own_tail_brier | 0.0442742429157 | 0.0444613580253 | -0.00018711510963 |
| own_tail_logloss | 0.182205182828 | 0.182892647722 | -0.000687464894141 |
| sample_brier | 0.22002484486 | 0.220156137422 | -0.000131292561422 |
| sample_logloss | 0.629147628109 | 0.629492214786 | -0.000344586676901 |
| deployment_brier | 0.0192988125778 | 0.0193010333546 | -2.22077681166e-06 |
| deployment_logloss | 0.0925806072564 | 0.0926056127525 | -2.50054961103e-05 |
| calibrated_auc | 0.696313030947 | 0.696036977709 | 0.000276053237653 |
| raw_contacts | 2476.3 | 2470.2 | 6.1 |

## All ten paired folds

| Fold | Candidate AUC | Baseline AUC | Delta AUC | Delta capture | Candidate contact share | Baseline contact share | Converged |
|---|---:|---:|---:|---:|---:|---:|---|
| r0_f0 | 0.693907853523 | 0.693502578638 | 0.000405274885091 | -0.00330127266443 | 0.0952918170298 | 0.098306297673 | True |
| r0_f1 | 0.694921370266 | 0.693707267357 | 0.00121410290902 | -0.000850334890586 | 0.094470191505 | 0.0937280049634 | True |
| r0_f2 | 0.702184919422 | 0.700650276135 | 0.00153464328722 | -0.000777191610792 | 0.098285657108 | 0.0962266795274 | True |
| r0_f3 | 0.694669635217 | 0.694441066405 | 0.00022856881148 | 0.00514080674273 | 0.100263924438 | 0.0967913035185 | True |
| r0_f4 | 0.695809741284 | 0.697217548082 | -0.00140780679834 | 0.00543600199177 | 0.0977110526106 | 0.0978786346548 | True |
| r1_f0 | 0.699129454612 | 0.698933973263 | 0.000195481349488 | 0.00373986833413 | 0.102547268662 | 0.103519060765 | True |
| r1_f1 | 0.698693164576 | 0.697888035561 | 0.000805129015857 | 0.000618340432135 | 0.106442766661 | 0.105538769189 | True |
| r1_f2 | 0.693099362504 | 0.693482165481 | -0.000382802977596 | -0.00565636796653 | 0.106048805486 | 0.106140277103 | True |
| r1_f3 | 0.695057736382 | 0.694589202321 | 0.000468534061056 | -0.00165959654737 | 0.0915783366264 | 0.0932971598654 | True |
| r1_f4 | 0.695657071684 | 0.69595766385 | -0.000300592166746 | 0.000769254802856 | 0.0961060045823 | 0.0924631112767 | True |

## Complete per-fold metrics

| Fold | Metric | Candidate | Baseline | Difference |
|---|---|---:|---:|---:|
| r0_f0 | auc | 0.693907853523 | 0.693502578638 | 0.000405274885091 |
| r0_f0 | value_capture | 0.283936001725 | 0.287237274389 | -0.00330127266443 |
| r0_f0 | contact_share | 0.0952918170298 | 0.098306297673 | -0.00301448064321 |
| r0_f0 | baseline_tail_brier | 0.0429407264002 | 0.0429616681424 | -2.09417422133e-05 |
| r0_f0 | baseline_tail_logloss | 0.17794783117 | 0.178015785356 | -6.79541861382e-05 |
| r0_f0 | own_tail_brier | 0.0438780434052 | 0.0429616681424 | 0.000916375262766 |
| r0_f0 | own_tail_logloss | 0.180673227746 | 0.178015785356 | 0.00265744239015 |
| r0_f0 | sample_brier | 0.220847003629 | 0.22101783801 | -0.000170834381063 |
| r0_f0 | sample_logloss | 0.631309881602 | 0.631757544384 | -0.000447662781891 |
| r0_f0 | deployment_brier | 0.0193267260565 | 0.0193270431083 | -3.1705179885e-07 |
| r0_f0 | deployment_logloss | 0.0928201492908 | 0.0928448354683 | -2.46861775536e-05 |
| r0_f0 | calibrated_auc | 0.693907853523 | 0.693502578638 | 0.000405274885091 |
| r0_f0 | raw_contacts | 2367 | 2403 | -36 |
| r0_f1 | auc | 0.694921370266 | 0.693707267357 | 0.00121410290902 |
| r0_f1 | value_capture | 0.298521548407 | 0.299371883298 | -0.000850334890586 |
| r0_f1 | contact_share | 0.094470191505 | 0.0937280049634 | 0.000742186541592 |
| r0_f1 | baseline_tail_brier | 0.0468924491061 | 0.0469064700458 | -1.4020939722e-05 |
| r0_f1 | baseline_tail_logloss | 0.191302678093 | 0.191203407182 | 9.92709106226e-05 |
| r0_f1 | own_tail_brier | 0.046204621153 | 0.0469064700458 | -0.000701848892836 |
| r0_f1 | own_tail_logloss | 0.189070785751 | 0.191203407182 | -0.00213262143137 |
| r0_f1 | sample_brier | 0.220403162619 | 0.220793753225 | -0.000390590605293 |
| r0_f1 | sample_logloss | 0.629844319268 | 0.630772380105 | -0.000928060837241 |
| r0_f1 | deployment_brier | 0.0193048433163 | 0.0193103184135 | -5.47509718189e-06 |
| r0_f1 | deployment_logloss | 0.0926659084627 | 0.0927278575813 | -6.19491185729e-05 |
| r0_f1 | calibrated_auc | 0.694921370266 | 0.693707267357 | 0.00121410290902 |
| r0_f1 | raw_contacts | 2443 | 2450 | -7 |
| r0_f2 | auc | 0.702184919422 | 0.700650276135 | 0.00153464328722 |
| r0_f2 | value_capture | 0.2997458547 | 0.300523046311 | -0.000777191610792 |
| r0_f2 | contact_share | 0.098285657108 | 0.0962266795274 | 0.00205897758056 |
| r0_f2 | baseline_tail_brier | 0.0463294615801 | 0.0463349729233 | -5.51134312858e-06 |
| r0_f2 | baseline_tail_logloss | 0.189558125987 | 0.189714820407 | -0.000156694420082 |
| r0_f2 | own_tail_brier | 0.0452629740391 | 0.0463349729233 | -0.00107199888416 |
| r0_f2 | own_tail_logloss | 0.1859828222 | 0.189714820407 | -0.00373199820734 |
| r0_f2 | sample_brier | 0.218384128439 | 0.218868310213 | -0.000484181773678 |
| r0_f2 | sample_logloss | 0.625615510516 | 0.626701041168 | -0.00108553065229 |
| r0_f2 | deployment_brier | 0.01929974614 | 0.0193045783867 | -4.83224669668e-06 |
| r0_f2 | deployment_logloss | 0.0923681282549 | 0.092459426217 | -9.12979620106e-05 |
| r0_f2 | calibrated_auc | 0.702184919422 | 0.700650276135 | 0.00153464328722 |
| r0_f2 | raw_contacts | 2494 | 2483 | 11 |
| r0_f3 | auc | 0.694669635217 | 0.694441066405 | 0.00022856881148 |
| r0_f3 | value_capture | 0.291953488114 | 0.286812681371 | 0.00514080674273 |
| r0_f3 | contact_share | 0.100263924438 | 0.0967913035185 | 0.00347262091976 |
| r0_f3 | baseline_tail_brier | 0.0437370307157 | 0.0438713560071 | -0.000134325291439 |
| r0_f3 | baseline_tail_logloss | 0.18035714193 | 0.180993798905 | -0.000636656974781 |
| r0_f3 | own_tail_brier | 0.0431578957772 | 0.0438713560071 | -0.000713460229859 |
| r0_f3 | own_tail_logloss | 0.178021095294 | 0.180993798905 | -0.00297270361095 |
| r0_f3 | sample_brier | 0.220470554641 | 0.220627232879 | -0.000156678238542 |
| r0_f3 | sample_logloss | 0.629930740076 | 0.630446806171 | -0.000516066094451 |
| r0_f3 | deployment_brier | 0.0192768001649 | 0.0192898453759 | -1.30452110585e-05 |
| r0_f3 | deployment_logloss | 0.0925340794973 | 0.0926107504201 | -7.66709227703e-05 |
| r0_f3 | calibrated_auc | 0.694669635217 | 0.694441066405 | 0.00022856881148 |
| r0_f3 | raw_contacts | 2475 | 2410 | 65 |
| r0_f4 | auc | 0.695809741284 | 0.697217548082 | -0.00140780679834 |
| r0_f4 | value_capture | 0.297257502182 | 0.29182150019 | 0.00543600199177 |
| r0_f4 | contact_share | 0.0977110526106 | 0.0978786346548 | -0.00016758204422 |
| r0_f4 | baseline_tail_brier | 0.0438097516265 | 0.0438417097887 | -3.19581621766e-05 |
| r0_f4 | baseline_tail_logloss | 0.180434904395 | 0.180598276557 | -0.000163372161489 |
| r0_f4 | own_tail_brier | 0.0447503080373 | 0.0438417097887 | 0.000908598248634 |
| r0_f4 | own_tail_logloss | 0.183847570056 | 0.180598276557 | 0.00324929349873 |
| r0_f4 | sample_brier | 0.220076082695 | 0.219776631207 | 0.000299451487528 |
| r0_f4 | sample_logloss | 0.629207228834 | 0.628664476504 | 0.000542752330014 |
| r0_f4 | deployment_brier | 0.0192887400867 | 0.0192915675672 | -2.82748046714e-06 |
| r0_f4 | deployment_logloss | 0.0925275864216 | 0.0925004028952 | 2.71835263952e-05 |
| r0_f4 | calibrated_auc | 0.695809741284 | 0.697217548082 | -0.00140780679834 |
| r0_f4 | raw_contacts | 2469 | 2437 | 32 |
| r1_f0 | auc | 0.699129454612 | 0.698933973263 | 0.000195481349488 |
| r1_f0 | value_capture | 0.313742803433 | 0.310002935099 | 0.00373986833413 |
| r1_f0 | contact_share | 0.102547268662 | 0.103519060765 | -0.000971792103496 |
| r1_f0 | baseline_tail_brier | 0.0444165189863 | 0.0443846000469 | 3.19189394268e-05 |
| r1_f0 | baseline_tail_logloss | 0.183045644107 | 0.182607607606 | 0.000438036500251 |
| r1_f0 | own_tail_brier | 0.0453886279173 | 0.0443846000469 | 0.00100402787045 |
| r1_f0 | own_tail_logloss | 0.186421107521 | 0.182607607606 | 0.00381349991495 |
| r1_f0 | sample_brier | 0.219182416366 | 0.219231877171 | -4.9460804437e-05 |
| r1_f0 | sample_logloss | 0.627273089221 | 0.627372386827 | -9.9297606148e-05 |
| r1_f0 | deployment_brier | 0.0192911269261 | 0.0192884373216 | 2.68960448331e-06 |
| r1_f0 | deployment_logloss | 0.0924212043051 | 0.0924153900465 | 5.81425859614e-06 |
| r1_f0 | calibrated_auc | 0.699129454612 | 0.698933973263 | 0.000195481349488 |
| r1_f0 | raw_contacts | 2612 | 2596 | 16 |
| r1_f1 | auc | 0.698693164576 | 0.697888035561 | 0.000805129015857 |
| r1_f1 | value_capture | 0.307295417105 | 0.306677076673 | 0.000618340432135 |
| r1_f1 | contact_share | 0.106442766661 | 0.105538769189 | 0.000903997472231 |
| r1_f1 | baseline_tail_brier | 0.0431725014601 | 0.0430872516027 | 8.52498573091e-05 |
| r1_f1 | baseline_tail_logloss | 0.178460329492 | 0.177917716997 | 0.000542612495232 |
| r1_f1 | own_tail_brier | 0.0428152548864 | 0.0430872516027 | -0.000271996716312 |
| r1_f1 | own_tail_logloss | 0.17742550342 | 0.177917716997 | -0.00049221357658 |
| r1_f1 | sample_brier | 0.219482706805 | 0.21970863307 | -0.000225926265093 |
| r1_f1 | sample_logloss | 0.628051435645 | 0.628478971103 | -0.000427535457774 |
| r1_f1 | deployment_brier | 0.0192902858549 | 0.019282670313 | 7.61554195339e-06 |
| r1_f1 | deployment_logloss | 0.0924593079712 | 0.0924536998416 | 5.60812958586e-06 |
| r1_f1 | calibrated_auc | 0.698693164576 | 0.697888035561 | 0.000805129015857 |
| r1_f1 | raw_contacts | 2603 | 2597 | 6 |
| r1_f2 | auc | 0.693099362504 | 0.693482165481 | -0.000382802977596 |
| r1_f2 | value_capture | 0.301069114037 | 0.306725482004 | -0.00565636796653 |
| r1_f2 | contact_share | 0.106048805486 | 0.106140277103 | -9.14716168953e-05 |
| r1_f2 | baseline_tail_brier | 0.0435884189692 | 0.0437198404284 | -0.00013142145914 |
| r1_f2 | baseline_tail_logloss | 0.180218278803 | 0.181037357282 | -0.000819078478841 |
| r1_f2 | own_tail_brier | 0.0428395035376 | 0.0437198404284 | -0.000880336890762 |
| r1_f2 | own_tail_logloss | 0.177476210302 | 0.181037357282 | -0.00356114697962 |
| r1_f2 | sample_brier | 0.220776381642 | 0.220820601407 | -4.42197656556e-05 |
| r1_f2 | sample_logloss | 0.63063644635 | 0.630923318755 | -0.000286872404976 |
| r1_f2 | deployment_brier | 0.0192989356493 | 0.0193075475604 | -8.61191108581e-06 |
| r1_f2 | deployment_logloss | 0.0926936271995 | 0.0927360710392 | -4.24438397638e-05 |
| r1_f2 | calibrated_auc | 0.693099362504 | 0.693482165481 | -0.000382802977596 |
| r1_f2 | raw_contacts | 2598 | 2632 | -34 |
| r1_f3 | auc | 0.695057736382 | 0.694589202321 | 0.000468534061056 |
| r1_f3 | value_capture | 0.278794495579 | 0.280454092126 | -0.00165959654737 |
| r1_f3 | contact_share | 0.0915783366264 | 0.0932971598654 | -0.001718823239 |
| r1_f3 | baseline_tail_brier | 0.0442034580869 | 0.0441828758292 | 2.05822576523e-05 |
| r1_f3 | baseline_tail_logloss | 0.181600449692 | 0.18168361912 | -8.31694276577e-05 |
| r1_f3 | own_tail_brier | 0.0446401120703 | 0.0441828758292 | 0.000457236241026 |
| r1_f3 | own_tail_logloss | 0.183083919117 | 0.18168361912 | 0.00140029999714 |
| r1_f3 | sample_brier | 0.22052025939 | 0.220678608765 | -0.000158349375094 |
| r1_f3 | sample_logloss | 0.630349340944 | 0.630712072651 | -0.000362731707165 |
| r1_f3 | deployment_brier | 0.0193129676635 | 0.0193142182557 | -1.25059227954e-06 |
| r1_f3 | deployment_logloss | 0.0927287165227 | 0.0927583010603 | -2.95845375964e-05 |
| r1_f3 | calibrated_auc | 0.695057736382 | 0.694589202321 | 0.000468534061056 |
| r1_f3 | raw_contacts | 2311 | 2337 | -26 |
| r1_f4 | auc | 0.695657071684 | 0.69595766385 | -0.000300592166746 |
| r1_f4 | value_capture | 0.289890603296 | 0.289121348493 | 0.000769254802856 |
| r1_f4 | contact_share | 0.0961060045823 | 0.0924631112767 | 0.00364289330566 |
| r1_f4 | baseline_tail_brier | 0.0453369294991 | 0.0453228354387 | 1.40940603486e-05 |
| r1_f4 | baseline_tail_logloss | 0.185358759704 | 0.185154087812 | 0.000204671891603 |
| r1_f4 | own_tail_brier | 0.0438050883335 | 0.0453228354387 | -0.00151774710524 |
| r1_f4 | own_tail_logloss | 0.180049586876 | 0.185154087812 | -0.00510450093651 |
| r1_f4 | sample_brier | 0.220105752377 | 0.220037888269 | 6.78641071089e-05 |
| r1_f4 | sample_logloss | 0.629258288639 | 0.629093150196 | 0.000165138442913 |
| r1_f4 | deployment_brier | 0.0192979539199 | 0.0192941072439 | 3.84667601515e-06 |
| r1_f4 | deployment_logloss | 0.0925873646378 | 0.0925493929552 | 3.79716825878e-05 |
| r1_f4 | calibrated_auc | 0.695657071684 | 0.69595766385 | -0.000300592166746 |
| r1_f4 | raw_contacts | 2391 | 2357 | 34 |

## Joint paired intervals

| Metric | Liberal IID | Hierarchical | Corrected t (df=4) | Conservative envelope |
|---|---|---|---|---|
| auc | [-0.000234877523273, 0.000751590458842] | [-0.000222554308929, 0.000829344977754] | [-0.00110998931618, 0.00166209579148] | [-0.00110998931618, 0.00166209579148] |
| value_capture | [-0.00177112104929, 0.00246148291485] | [-0.00193236174425, 0.00274153975294] | [-0.00556922085165, 0.00626112257644] | [-0.00556922085165, 0.00626112257644] |
| contact_share | [-0.000774987500079, 0.00175305409838] | [-0.000757555275705, 0.00177243925751] | [-0.00304579875174, 0.00401710398633] | [-0.00304579875174, 0.00401710398633] |
| baseline_tail_brier | [-6.09455723373e-05, 1.97486745285e-05] | [-6.54123660794e-05, 3.28674424604e-05] | [-0.000131426078651, 9.41593140342e-05] | [-0.000131426078651, 9.41593140342e-05] |
| baseline_tail_logloss | [-0.000321642020566, 0.000178406759219] | [-0.000326113980445, 0.000250907070708] | [-0.000764503672928, 0.000636036902671] | [-0.000764503672928, 0.000636036902671] |
| own_tail_brier | [-0.000726490507459, 0.000364111041347] | [-0.000729372161267, 0.000383230489066] | [-0.00171975148708, 0.00134552126782] | [-0.00171975148708, 0.00134552126782] |
| own_tail_logloss | [-0.00257184195588, 0.00124281891059] | [-0.00256977507845, 0.00124129728546] | [-0.00604340555414, 0.00466847576585] | [-0.00604340555414, 0.00466847576585] |
| sample_brier | [-0.000258384026252, 1.22942600448e-06] | [-0.000291680381844, -3.52727412611e-06] | [-0.000495772973291, 0.000233187850447] | [-0.000495772973291, 0.000233187850447] |
| sample_logloss | [-0.000618249979557, -5.87519259027e-05] | [-0.000714424273571, -6.50676814142e-05] | [-0.0011280159009, 0.000438842547094] | [-0.0011280159009, 0.000438842547094] |
| deployment_brier | [-5.84639337762e-06, 1.32918430428e-06] | [-7.14248693594e-06, 3.08841450247e-06] | [-1.22874166647e-05, 7.84586304137e-06] | [-1.22874166647e-05, 7.84586304137e-06] |
| deployment_logloss | [-5.07932749849e-05, 5.38288477641e-07] | [-6.25307542647e-05, 7.29676815302e-06] | [-9.70850511375e-05, 4.7074058917e-05] | [-9.70850511375e-05, 4.7074058917e-05] |
| calibrated_auc | [-0.000234877523273, 0.000751590458842] | [-0.000222554308929, 0.000829344977754] | [-0.00110998931618, 0.00166209579148] | [-0.00110998931618, 0.00166209579148] |
| raw_contacts | [-12.9, 25.6] | [-13.6, 28.5] | [-47.6099619847, 59.8099619847] | [-47.6099619847, 59.8099619847] |

[A] 100,000 hierarchical and 100,000 IID paired draws saved with all metric columns and resampling indices. Linear percentile endpoints. Corrected SE=sqrt((1/10+0.25)*sample variance), df=4. Conservative interval envelopes hierarchical and corrected-t endpoints.
[A] Repeated folds share customers/training rows. Hierarchical resampling is an exploratory variance heuristic, not independently sampled cohort uncertainty; no calibrated coverage or post-selection guarantee.

## Every gate

- [E] PASS: ten_complete_finite_id_matched_folds
- [E] PASS: all_classifier_and_sigmoid_fits_converged
- [E] PASS: protected_fingerprints_and_outside_boundary_unchanged
- [E] FAIL: mean_delta_auc_ge_0_003
- [E] FAIL: conservative_auc_lower_gt_0
- [E] PASS: mean_fixed_tau_value_capture_gain_gt_0
- [E] FAIL: conservative_value_capture_lower_gt_0
- [E] FAIL: baseline_tail_brier_conservative_upper_le_0
- [E] FAIL: baseline_tail_logloss_conservative_upper_le_0
- [E] FAIL: own_tail_brier_conservative_upper_le_0
- [E] FAIL: own_tail_logloss_conservative_upper_le_0

[E] Failed gates: mean_delta_auc_ge_0_003, conservative_auc_lower_gt_0, conservative_value_capture_lower_gt_0, baseline_tail_brier_conservative_upper_le_0, baseline_tail_logloss_conservative_upper_le_0, own_tail_brier_conservative_upper_le_0, own_tail_logloss_conservative_upper_le_0
[R] rejected_keep_frozen_v2_stop_model_track

## Warnings and non-adaptive inner evidence

- [E] r0_f0_inner0: converged=True; iterations=385; warnings=[]
- [E] r0_f0_inner1: converged=True; iterations=385; warnings=[]
- [E] r0_f0_inner2: converged=True; iterations=385; warnings=[]
- [E] r0_f0_development: converged=True; iterations=385; warnings=[]
- [E] r0_f0_outer: converged=True; iterations=385; warnings=[]
- [E] r0_f0_sigmoid: converged=True; iterations=4; warnings=[]
- [E] r0_f1_inner0: converged=True; iterations=385; warnings=[]
- [E] r0_f1_inner1: converged=True; iterations=385; warnings=[]
- [E] r0_f1_inner2: converged=True; iterations=385; warnings=[]
- [E] r0_f1_development: converged=True; iterations=385; warnings=[]
- [E] r0_f1_outer: converged=True; iterations=385; warnings=[]
- [E] r0_f1_sigmoid: converged=True; iterations=4; warnings=[]
- [E] r0_f2_inner0: converged=True; iterations=385; warnings=[]
- [E] r0_f2_inner1: converged=True; iterations=385; warnings=[]
- [E] r0_f2_inner2: converged=True; iterations=385; warnings=[]
- [E] r0_f2_development: converged=True; iterations=385; warnings=[]
- [E] r0_f2_outer: converged=True; iterations=385; warnings=[]
- [E] r0_f2_sigmoid: converged=True; iterations=4; warnings=[]
- [E] r0_f3_inner0: converged=True; iterations=385; warnings=[]
- [E] r0_f3_inner1: converged=True; iterations=385; warnings=[]
- [E] r0_f3_inner2: converged=True; iterations=385; warnings=[]
- [E] r0_f3_development: converged=True; iterations=385; warnings=[]
- [E] r0_f3_outer: converged=True; iterations=385; warnings=[]
- [E] r0_f3_sigmoid: converged=True; iterations=3; warnings=[]
- [E] r0_f4_inner0: converged=True; iterations=385; warnings=[]
- [E] r0_f4_inner1: converged=True; iterations=385; warnings=[]
- [E] r0_f4_inner2: converged=True; iterations=385; warnings=[]
- [E] r0_f4_development: converged=True; iterations=385; warnings=[]
- [E] r0_f4_outer: converged=True; iterations=385; warnings=[]
- [E] r0_f4_sigmoid: converged=True; iterations=4; warnings=[]
- [E] r1_f0_inner0: converged=True; iterations=385; warnings=[]
- [E] r1_f0_inner1: converged=True; iterations=385; warnings=[]
- [E] r1_f0_inner2: converged=True; iterations=385; warnings=[]
- [E] r1_f0_development: converged=True; iterations=385; warnings=[]
- [E] r1_f0_outer: converged=True; iterations=385; warnings=[]
- [E] r1_f0_sigmoid: converged=True; iterations=4; warnings=[]
- [E] r1_f1_inner0: converged=True; iterations=385; warnings=[]
- [E] r1_f1_inner1: converged=True; iterations=385; warnings=[]
- [E] r1_f1_inner2: converged=True; iterations=385; warnings=[]
- [E] r1_f1_development: converged=True; iterations=385; warnings=[]
- [E] r1_f1_outer: converged=True; iterations=385; warnings=[]
- [E] r1_f1_sigmoid: converged=True; iterations=5; warnings=[]
- [E] r1_f2_inner0: converged=True; iterations=385; warnings=[]
- [E] r1_f2_inner1: converged=True; iterations=385; warnings=[]
- [E] r1_f2_inner2: converged=True; iterations=385; warnings=[]
- [E] r1_f2_development: converged=True; iterations=385; warnings=[]
- [E] r1_f2_outer: converged=True; iterations=385; warnings=[]
- [E] r1_f2_sigmoid: converged=True; iterations=4; warnings=[]
- [E] r1_f3_inner0: converged=True; iterations=385; warnings=[]
- [E] r1_f3_inner1: converged=True; iterations=385; warnings=[]
- [E] r1_f3_inner2: converged=True; iterations=385; warnings=[]
- [E] r1_f3_development: converged=True; iterations=385; warnings=[]
- [E] r1_f3_outer: converged=True; iterations=385; warnings=[]
- [E] r1_f3_sigmoid: converged=True; iterations=3; warnings=[]
- [E] r1_f4_inner0: converged=True; iterations=385; warnings=[]
- [E] r1_f4_inner1: converged=True; iterations=385; warnings=[]
- [E] r1_f4_inner2: converged=True; iterations=385; warnings=[]
- [E] r1_f4_development: converged=True; iterations=385; warnings=[]
- [E] r1_f4_outer: converged=True; iterations=385; warnings=[]
- [E] r1_f4_sigmoid: converged=True; iterations=3; warnings=[]
- [E] r0_f0 inner paired AUC differences (diagnostic only): 0.00136466698232, 6.45986958376e-05, -0.000295132621305
- [E] r0_f1 inner paired AUC differences (diagnostic only): 0.00129013002558, 0.000947666305702, -0.00156947953828
- [E] r0_f2 inner paired AUC differences (diagnostic only): 0.000811765275779, -0.000703553865843, 8.24125597116e-05
- [E] r0_f3 inner paired AUC differences (diagnostic only): 0.00124651731148, -0.00125228337795, 0.00163137490214
- [E] r0_f4 inner paired AUC differences (diagnostic only): 0.00152894518487, 0.000353948974218, -0.000574528362328
- [E] r1_f0 inner paired AUC differences (diagnostic only): 0.00114663466422, -0.000149480194577, -0.000486663332341
- [E] r1_f1 inner paired AUC differences (diagnostic only): -0.00125931516632, 0.00142151508475, 0.00020870347886
- [E] r1_f2 inner paired AUC differences (diagnostic only): -0.000521305537455, 0.0008142654672, -3.60965136392e-06
- [E] r1_f3 inner paired AUC differences (diagnostic only): -0.000151871002624, 0.00183871890192, 0.00179009017878
- [E] r1_f4 inner paired AUC differences (diagnostic only): 0.00163228122153, 0.00143357850835, -0.0016362815278

## Integrity, limitations and stopping boundary

[E] Outside-sandbox full directory diff: {"added_outside": [], "changed_outside": [], "files_after": 4246, "files_before": 4246, "passed": true, "removed_outside": []}
[E] Frozen delivery unchanged: True; historical WP7 receipt and 118-file manifest unchanged: True.
[A] Sigmoid trained from a 48k development model is applied to a 60k refit: fit-size-shift limitation. The _Mean window is unspecified; curvature/contrasts are undated proxies, not verified acceleration or temporal validation.
[R] No test scoring even if all gates pass. Passing means eligible_requires_separate_confirmatory_scope, not deployment or delivery integration. Failing retains frozen v2 and stops this model track; no further candidate/revision/seed sweep.
[E] No notebook, PDF, PPTX, reference, configuration, old model/test, or historical receipt was edited.
