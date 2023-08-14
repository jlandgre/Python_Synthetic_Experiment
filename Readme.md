**Background**</br>
Synthetic experiments are a great way to explore an experimental space prior to running sometimes expensive and time-consuming physical experiments. Simulation can provide an idea of whether a qualification has a chance of passing versus specification criteria. It is a great way to explore whether a particular sampling plan can resolve effects that may be present in a designed experiment.

This repository shares a Python Monte Carlo simulator for running synthetic lab or industrial experiments. The simulator is comprised of a Python Class, **SyntheticData** in the **synthetic.py** file. Its inputs are a measurement grand mean and a list of the “degrees of freedom“ describing the sampling dimensions for the experimental domain. This high level of abstraction allows the simulator to be used broadly ranging from small lab experiments to multi-lot qualifications spanning months in a manufacturing system and for contexts of liquid chemical processes, part molding or web substrate production.

The simulator's Monte Carlo engine introduces random variability for each degree of freedom. This is based on user input of a standard deviation and represents typical variability from unknown causes in that degree of freedom. Even prior to running a trial or qualification, it is common to have experience-based estimates of such variability (e.g. "lot-to-lot raw material variability typically about 5% of the mean for products like these"). Lab or measurement variability can usually be pre-quantified by running a lab co-op study on small quantities of the product.

In addition to random variability, for designed experiments, **SyntheticData** can take user-specified effects within a degree of freedom's levels such as for different batches of product. This works when generating predicted values for a batch based on its formula or process making conditions. The Monte Carlo simulations provide simulated lab data for exploring data analysis techniques.

Monte Carlo simulation is an alternative to and not a replacement for rigorous statistical power calculations. However, working with simulated data is sometimes a good way to internalize what to expect from a manufacturing process or to practice techniques for analyzing real-world experiments and product qualifications. It also can be helpful as a comparison to real data for highlighting the value of potential control strategy improvements.

**SyntheticData Python Class Inputs**</br>
The simulator takes several required and optional inputs when a **SyntheticData** Class is instanced. Each class instance is for a specific measurement, so multiple instances should be used to simulate the collection of measurements in a typical product or raw material specification.
* **xbarbar** [Required] Measurement grand mean (in measurement's units). This is used as a reference point for generating results. If a formula/process simulator is used on the front 
* **sig_digits** [Required] Number of significant digits for the measurement .
* List of names of the degrees of freedom [Required]. These are nominal or categorical variables describing sampling locations or times. Here are some example lists for lab and industrial contexts:
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

Example questions to answer from simulation:
1.  Will this sampling plan allow resolution (>95% confidence) of batch-to-batch effects of this magnitude
2. how closely does statistical anlaysis of the slope agree with the formulation model's slope?
3.  Since the viscosity measure is relatively noisy, how could the analysis be improved if n=4 measurements were used instead of n=2?
4.  In the limiting case where there are no other degree of freedom variabilities (e.g. no raw material long term variability) in industrial production, is it possible to meet a +/- 10% specification limit with one of these formulas?

 To produce simulated experiment results, instance a **SyntheticData** Class as shown with the specified parameters and run its **create_experiment_procedure()** method. The resulting **df_expt** dataframe contains the details, including the measurement results in the right most column. The first printout shows just the high-level view by batch name, within-batch sample number and measurement number.

<p align="center">
  Class Instancing and Data Output</br>
  <img src=images/case_study1_3.png "Example Experiment" width=400></br>
</p>

 Without filtering the columns, additional diagnostics show how the simulated lab measurements are generated
* Columns with "devns_ prefix" are the random (unexplained)variability for that dof. These are in the measurements cps units
* Columns with "effect_ prefix are the user-specified effects --also in cps


J.D. Landgrebe / Data Delve LLC, August 2023

**Separate MS Excel Monte Carlo Simulator**
The Excel workbook, sampling.xlsx, shows a basic setup for creating Monte Carlo simulated measurement data (Rows in Sim Data sheet) having a specified mean and standard deviation. The Dists sheet contains seed data from which the simulated measurements are randomly pulled Dists columns are 10,000 normally distributed points having a mean of 0.0 and standard deviation 1.0. The Normal column (A) data were generated in JMP. The Normal2 column B data were generated in Excel using the formula. See the About sheet in the workbook for more details and screen pictures from JMP

J.D. Landgrebe / Data Delve LLC, July 10, 2023
