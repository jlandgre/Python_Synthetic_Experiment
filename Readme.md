**Background**</br>
Synthetic data experiments are a way to explore an experimental space prior to running sometimes expensive and time-consuming physical experiments. As an example use case, simulation can provide an idea of whether a qualification has a chance of passing versus specification criteria. It is also a way to explore whether a particular sampling plan can resolve effects that may be present in a designed experiment.

This repository shares a Python Monte Carlo simulator for running synthetic lab or industrial experiments. The simulator is comprised of a Python Class, **SyntheticData** in the **synthetic.py** file. The class is validated by Pytest tests in tests/test_synthetic.The experiment is described by a list of the “degrees of freedom“ describing the sampling dimensions for the experimental domain. This high level of abstraction allows the simulator to be used broadly in applications ranging from small lab experiments to multi-lot manufacturing qualifications spanning months and for contexts of liquid chemical processes, part molding, extruded part production or web substrate production.

The simulator's Monte Carlo engine introduces random variability for each degree of freedom. This is based on user input of a standard deviation representing variability from unknown causes in that degree of freedom. Even prior to running a trial or qualification, it is common to have experience-based estimates of such variability (e.g. "lot-to-lot raw material variability typically about 5% of the mean for products like these"). Lab or measurement variability can often be pre-quantified by running a lab co-op study on small quantities of the product.

In addition to random variability, for designed experiments, **SyntheticData** can take inputs for user-specified effects within a degree of freedom's levels such as for different batches of product. The simulation outputs a matrix of simulated measurement results for the specified degrees of freedom and their levels.

Monte Carlo simulation is an alternative to and not a replacement for rigorous statistical power calculations. However, working with simulated data is often a good way to internalize what to expect from a manufacturing process or to practice techniques for analyzing real-world experiments and product qualifications. It also can be helpful as a comparison to real data for understanding the value of potential control strategy improvements.

**SyntheticData Python Class Inputs and Usage**</br>
The simulator takes several required and optional inputs when a **SyntheticData** Class is instanced. Each class instance is for a specific measurement, so multiple instances should be used to simulate the collection of measurements in a typical product or raw material specification.
* **xbarbar** [Required] Measurement grand mean (in measurement's units). This is used as a reference point for generating results.  
* **sig_digits** [Required] Number of significant digits for rounding calculated measurements.
* **nms_dof** [Required] List of names of the degrees of freedom. See example below. Each degree of freedom is a categorical variables describing a sampling location or time. Here are some example lists for lab and industrial contexts:
  * **Batch process qualification**: raw material lot to lot, batch to batch, within batch or within filling run, lab measurement 
  * **Substrate raw material qualification**: raw material lot to lot, master roll to master roll, within roll, lane to lane, MD short distance, lab measurement
  * **Injection molded part**: raw material lot to lot, within lot, injection shot, cavity to cavity, lab measurement 

  Notice that "lab measurement" is often the last item since lab measurement is often the last step in the chain of acquiring data. This might not be present if the measurement is generated precisely by direct, instrumental measurement.

* **n_levels** [Required] Dictionary (degree of freedom keys) specifying integer number of levels for each degree of freedom. This uses  degree of freedom names as the dictionary keys. The definition of “level” depends on the degree of freedom. For example, N_levels for lab measurement specifies number of measurements performed by the lab on each sample,  For a batch to batch degree of freedom, N_levels specifies the the number of batches in the experiment.
* **var_fracs** [Required] Dictionary (degree of freedom keys) specifying random variability as a percent of the grand mean for each degree of freedom. This can optionally be zero.
* **lvl_val_names** [Optional] Dictionary (degree of freedom keys) of lists specifying names for within degree of freedom levels such as Batch ID's. If specified for a degree of freedom, the length of the **lvl_val_names** list must match **n_levels** for the degree of freedom.
* **lvl_val_effects** [Optional] Dictionary (degree of freedom keys) of lists specifying effects (as a fraction of grand mean) to apply to the levels as a way of simulating designed experiment measurement effects caused by varying input conditions such as the formulation or process conditions

**Example Case Study**: "Case Study 1" in Case_Studies.ipynb</br>
A designed experiment will consist of making five batches that will each be sampled in n=3 within-batch locations referred to as "Begin", "Middle" and "End" based on sampling during batch pumpout. Each sample is measured for viscosity n=2 times. 

To simulate the experiment prior to running it, the grand mean viscosity is assumed to be 400 centipoise (cps). Random batch to batch variation (due to unknown causes)is expected to be about 2% of the mean based on prior, industrial experience with similar products. Similarly, within-batch variability is expected to be about  3% of the mean. The viscosity lab method is relatively noisy for this product type --5% of the mean.

The five batches will have incremental formula variations of 2.3 to 2.8% of ingredient x -- modeled in the lab to cause a linear increase in viscosity from -20% of grand mean (320 cps) to +20% of grand mean (480 cps)

<p align="center">
  Degree of Freedom Inputs for Viscosity Simulation</br>
  <img src=images/case_study1_1.png "Overall Inputs" width=600></br>
</p>
<p align="center">
  Level-Specific Inputs</br>
  <img src=images/case_study1_2.png "Level-specific Inputs" width=600></br>
</p>

 To produce simulated experiment results, instance a **SyntheticData** Class as shown with the specified parameters and run its **create_experiment_procedure()** method. The resulting **df_expt** dataframe contains the details, including simulated measurement results in the right-most column. The printout shows a high-level view by batch name, within-batch, lab sample number and simulated measurement value.

<p align="center">
  Class Instancing and Data Output</br>
  <img src=images/case_study1_3.png "Example Experiment" width=400></br>
</p>

 Without filtering the columns (not shown; see *.ipynb), additional diagnostics show how the simulated lab measurements are generated
* Columns with "devns_ prefix" are the random (unexplained)variability for that dof. These are in the measurements cps units
* Columns with "effect_ prefix are the user-specified effects --also in cps

**Example Statistical Analysis of Case Study 1**</br>
A benefit of simulation is being able to explore how to analyze the real data and to check that the data can answer desired questions. The following discussion illustrates a first level analysis of the Case Study 1 simulation data using JMP software. This can also be done in Python using SciKit-Learn, but JMP does a good job presenting results both graphically and with accompanying statistical results.

A first check is to use JMP's Analyze/Fit Y by X to compare results by batch --initially ignoring within batch effects. The input effects for **batch** were a +/- 20% range expected to create a range of 320 to 480 cps. The Fit Y by X plot shows statistically significant batch to batch differences, but random variation causes Batches A and B and Batches D and E to not have the expected separation. The range is 319.6 to 447.1 cps for Batches A to E. This discrepancy versus inputs is caused by the realistic variation in the simulation. That is good to know.

<p align="center">
  <img src=images/case_study1_jmp4.png "Results by batch" width=400></br>
</p>

In this single-variable analysis, the least significant difference is exaggerated because we have not accounted for within batch differences. We know this effect is there based on our simulation inputs. In an actual experiment, we might not be aware of this. 

To look at the batch and within batch effects together, we can run multiple regression with the **batch**, and **within batch** categoricals both as x variables. The pictures show the menu selection and dialog box for this. The By variable, sim_run, is optional for our case of only a single simulation run, but it will be useful for future comparisons of alternate sampling such as if we were to double the lab sampling to n=4 measurements per sample location.

<p align="center">
  <img src=images/case_study1_jmp0.png "Results by batch" width=200>   <img src=images/case_study1_jmp1.png "Results by batch" width=400></br>
</p>

JMP excels at illustrating how well this model predicts viscosity and shows that both **within batch** and **batch** are statistically significant (effect p-values <0.0001 and =0.0014). In experimental data, this analysis would be how we would discover and prove that there is a within-batch effect.  The overall model's R-squared of 0.90 is indicates an excellent fit. The RMSE (Root Mean Square Error) of 21 cps suggests that individual measurements fall within about +/- 63 cps prediction accuracy (e.g. 3 x 21 for 95% of points if model residuals are normally distributed as they appear to be here).

<p align="center">
  <img src=images/case_study1_jmp2.png "Results by batch" width=300>   <img src=images/case_study1_jmp3.png "Results by batch" width=400></br>
</p>

The least squares means are interesting. Since we ran a balanced "experiment," they match the batch averages from the previous Fit Y by X.  The **within batch** LS Means range from 372 to 408 versus expected 380 to 420 based on our +/- 5% effect input. 

This is a good start on analysis and exploration of the case study. It illustrates the usefulness of Monte Carlo synthetic data simulations. 

Without showing the details, increasing the lab sampling from n=2 to n=4 measurements per sample brought the LS Means closer to our inputs, but even with this relatively high lab sampling, the 2% of mean batch-to-batch variation would make it difficult to create a precise formulation model from an experiment having variabilities like this simulation. With n=4 lab measurements, Batch A to E averages were 320, 329, 387, 444 and 447 cps (versus 320, 360, 400, 440 and 480 expected based on inputs). The within-batch LS Means were 372, 375 and 408 cps (versus 380, 400 and 420 cps expected). In particular, the 375 is several [within-batch] standard deviations from expected, but its n=4 lab samples are subject to their own measurement variabilities, which contributes to the gap.

J.D. Landgrebe / Data Delve LLC, August 2023