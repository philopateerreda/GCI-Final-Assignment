# Track M closure note

Track M is closed. The frozen submission model was already refit on all 75,000 non-test customers, with 10,000 further customers used for calibration, so adding data to that pool cannot change the fit: the audit's point prediction of the extra gain is exactly 0.0000 AUC, below the pre-declared 0.0015 gate.

A repeated ten-fold learning curve over the same pool shows the model is close to its data asymptote. Mean held-out AUC rises from 0.678565 to 0.689170 to 0.693949 to 0.696203 to 0.696845 as training grows through 15,000, 30,000, 45,000, 60,000 and 67,500 rows; the last step adds 0.000641. The fitted curve has exponent c = 0.672 (95% interval 0.403 to 0.964).

Extrapolation [A], not a measured result: another 10,000 training rows would add about +0.0008 AUC, and doubling the training pool to 150,000 would add about +0.0037 AUC. Both are far below the gate. No model was refit, no candidate was added, no test row was read, and M2 to M6 are not run.
