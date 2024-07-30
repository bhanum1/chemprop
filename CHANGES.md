# Summary of all changes to the base chemprop repository

This repository was created based on version 2.0.1 of the Chemprop library from MIT. It was made to allow usage of the arrhenius equation to predict properties of thermal fluids. This file contains a list of changes made to the repo, and a brief explanation. These changes are shown below.

- Model now has 2 output nodes, corresponding to arrhenius parameters
- Data is now passed in csv with columns: smiles, temperature, target, lnA
- The name of the smiles column and the target column can be changed and specified in the config file
- The name of the temperature and lnA columns must be exactly as listed here, including the case
- The MSELoss function now calculates the final parameter using temperature input, and the predicted arrhenius parameters, then compares it to the target
- MSELoss also can compute the loss between the predicted vs true lnA values and use it as part of the loss. The percent contribution is a hyperparameter
- lnA targets can be passed, or they can be left out to have the model not utilize them in prediction
- Data normalization during prediction was removed entirely, as it was causing errors. Data must now be normalized prior to passing into the model
- To normalize, calculate mean and stdev of the target values, and use them to normalize the target and the lnA values (same mean and stdev for both)
- For temperature normalization, find the max temperature in the train dataset, Tmax. The normalized temperature is equal to Tmax / T. This is done to ensure the lnA value does not change due to temperature normalization
- During hyperparameter optimization, a new term is added, "loss_reg". This defines what factor the lnA loss is multiplied by when added to the total loss. Typical values are 0.0 - 0.4.