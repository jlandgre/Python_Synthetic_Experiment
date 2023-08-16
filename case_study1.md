**Example Case Study**: See files in case_study1 subfolder</br>
A designed experiment will consist of making five batches that will each be sampled in n=3 within-batch locations referred to as "Begin", "Middle" and "End" based on sampling during batch pumpout. Each sample is measured by the lab for viscosity n=2 times. 

To simulate the experiment prior to running it, the grand mean viscosity is assumed to be 400 centipoise (cps) based on the specification target. Random, batch-to-batch variation (due to unknown causes)is expected to be about 2% of the mean based on prior, industrial experience with similar products. Similarly, within-batch variability is expected to be about 3% of the mean. The viscosity lab method is relatively noisy for this product type --5% of the mean.

The five batches will have incremental formula variations of 2.3 to 2.8% of ingredient x -- modeled by lab data to cause a linear increase in viscosity from -20% of grand mean (320 cps) to +20% of grand mean (480 cps)

Finally, there is known to be a 10% drift in viscosity from Begin to End of batch pumpout.

These screen pictures from **Case_Studies.ipynb** show input variables based on the above description --with options for running with or without the within-batch effect described above.

<p align="center">
  Sampling Degree of Freedom Inputs for Viscosity Simulation</br>
  <img src=images/case_study1_1.png "Overall Inputs" width=600></br>
</p>
<p align="center">
  Level-Specific Inputs</br>
  <img src=images/case_study1_2.png "Level-specific Inputs" width=600></br>
</p>

 To produce simulated experiment results, instance a **SyntheticExpt** Class as shown and run its **create_experiment_procedure()** method. The resulting **df_expt** dataframe contains the details, including simulated lab measurement results in the right-most column. The printout shows a high-level view by batch name, within-batch, lab sample number and simulated measurement value.

<p align="center">
  Class Instancing and Data Output</br>
  <img src=images/case_study1_3.png "Example Experiment" width=400></br>
</p>

 Without filtering the columns (not shown; see *.ipynb), additional diagnostic columns show how the simulated lab measurements are generated
* Columns with "devns_ prefix" are the random (unexplained)variability for that dof. These are in the measurement's cps units
* Columns with "effect_" prefix are the user-specified effects --also in cps

**Example Statistical Analysis**</br>
A benefit of simulation is being able to explore how to analyze the data and to check that the data can answer desired questions. The following discussion illustrates a first level analysis of the Case Study 1 simulation data using [JMP by SAS Institute](https://www.jmp.com/en_us/home.html) software. This can also be done in Python using SciKit-Learn, but JMP does a good job presenting results both graphically and with accompanying statistical results.

A first check is to use JMP's Analyze/Fit Y by X to compare results by batch --initially ignoring within-batch effects. The effects inputs for **batch** were a +/- 20% range expected to create a range of 320 to 480 cps on average and without variability. The plot and accompanying statistical report shows statistically significant batch to batch differences as evidenced by the heights of the means diamonds showing the least significant difference for each grouping. The combination of lab and process variation causes Batches A and B and Batches D and E to not have the expected separation though. The range is 319.6 to 447.1 cps for Batches A to E.

<p align="center">
  <img src=images/case_study1_jmp4.png "Results by batch" width=400></br>
</p>

In this single-variable analysis, the least significant difference is exaggerated because we have not attempted to quantify within-batch effects. We know this effect is there based on our simulation inputs. In an actual experiment, we might not be aware of this. 

To look at the batch and within-batch effects together, we can run multiple regression with the **batch**, and **within batch** categoricals both as x variables. The pictures show the JMP menu selection and dialog box for this. The By variable, sim_run, is optional for our case of only a single simulation run, but it will be useful for future comparisons of alternate sampling such as if we were to try doubling the lab sampling to n=4 measurements per sample location or try increasing or decreasing the number of batches.

<p align="center">
  <img src=images/case_study1_jmp0.png "Results by batch" width=200>   <img src=images/case_study1_jmp1.png "Results by batch" width=400></br>
</p>

JMP excels at illustrating how well this model predicts viscosity with the first plot of predicted versus actual results. The accompanying leverage plots show that both **within batch** and **batch** are statistically significant (effect p-values <0.0001 and =0.0014). In experimental data, this analysis would be how we would discover and prove that there is a within-batch effect. The overall model's R-squared of 0.90 is indicates an excellent fit. The RMSE (Root Mean Square Error) of 21 cps suggests that individual measurements fall within about +/- 63 cps prediction accuracy (e.g. 3 x 21 for 95% of points if model residuals are normally distributed as they appear to be here). Not coincidentally, the 21 cps RMSE is about 5% of the grand mean, which is the lab measurement variability we specified in the **var_fracs_dof** dictionary input.

<p align="center">
  <img src=images/case_study1_jmp2.png "Results by batch" width=300>   <img src=images/case_study1_jmp3.png "Results by batch" width=400></br>
</p>

The least squares means are interesting. They may be thought of as alternate intercept values for the model based on Batch and within-batch level. Since we ran a balanced "experiment," they match the batch averages from the previous Fit Y by X. The **within batch** LS Means range from 372 to 408 versus expected 380 to 420 based on our +/- 5% effect input. 

This is a good start on analysis and exploration of the case study. It illustrates the usefulness of Monte Carlo synthetic data simulations. 

Without showing the details, the synthetic data simulator is a great way to explore alternate sampling --possibly aiding negotiations with lab personnel if it makes sense to use increased sampling. In this case, increasing the lab sampling from n=2 to n=4 measurements per sample brought the LS Means closer to our inputs, but even with this relatively high lab sampling, the 2% of mean batch-to-batch variation would make it difficult to create a precise formulation model from an industrial scale experiment like this. With n=4 lab measurements, Batch A to E averages were 320, 329, 387, 444 and 447 cps (versus 320, 360, 400, 440 and 480 expected based on inputs). The within-batch LS Means were 372, 375 and 408 cps (versus 380, 400 and 420 cps expected). In particular, the 375 is several [within-batch] standard deviations from expected, but its n=4 lab samples are subject to their own measurement variabilities, which contributes to the gap.

J.D. Landgrebe / Data Delve LLC, August 2023