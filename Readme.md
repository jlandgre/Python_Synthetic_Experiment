**Background**</br>
Synthetic data experiments are a way to explore an experimental space prior to running sometimes expensive and time-consuming physical experiments. As an example use case, simulation can provide an idea of whether a qualification has a chance of passing versus specification criteria. It is also a way to explore whether a particular sampling plan can resolve effects in a designed experiment.

This repository shares a Python Monte Carlo-based simulator for running synthetic lab or industrial experiments. The simulator is comprised of a Python Class, **SyntheticExpt** in the **synthetic.py** file. Pytest validation is in tests/test_synthetic.py. 

In the Class, the experiment is described by a list of “degrees of freedom“ describing sampling dimensions for the experimental domain. This high level of abstraction allows the simulator to be used broadly in applications ranging from small lab experiments to multi-lot manufacturing qualifications spanning months of production and for contexts of liquid chemical processes, part molding, extruded piece production or web substrate production. The simulation outputs a matrix of simulated measurement results for specified degrees of freedom and their levels.

The simulator's Monte Carlo engine introduces random variability for each degree of freedom. This is based on user input of a standard deviation for unknown cause variation due to that degree of freedom. Even prior to running a trial or qualification, it is common for experts to have experience-based estimates of such variability ("lot-to-lot raw material variability is typically about 5% of the mean for products like these"). Lab or measurement variability can be pre-quantified by running a lab co-op study on small quantities of the product.

For simulating designed experiments, **SyntheticExpt** can take inputs for user-specified effects within a degree of freedom's levels such as for different batches of product whose results vary due to varying their formulation or process conditions. 

Monte Carlo simulation is an alternative to and not a replacement for rigorous statistical power calculations. However, working with simulated data is a good way to internalize what to expect from a manufacturing process or to explore analysis techniques for upcoming experiments and product qualifications. It also can be helpful as a comparison to real data for vetting control strategy improvements.

**SyntheticExpt Python Class Inputs and Usage**</br>
The simulator takes several required and optional inputs when the Class is instanced. Each instance is for a specific measurement, so multiple instances should be used to simulate the collection of measurements in a typical product or raw material specification.
* **xbarbar** [Required] Measurement grand mean (in measurement's units). This is used as a reference point for generating results.  
* **sig_digits** [Required] Number of significant digits for rounding calculated measurements.
* **nms_dof** [Required] List of names of the degrees of freedom. Each degree of freedom is a categorical variable describing a sampling location or time. Here are some example lists for lab and industrial contexts:
  * **Batch process qualification**: raw material lot, batch, within batch or within filling run, lab measurement 
  * **Substrate raw material qualification**: raw material lot, master roll, within roll, CD lane, MD short distance, lab measurement
  * **Injection molded part**: raw material lot, within lot, injection shot, mold cavity, lab measurement 

  Notice that "lab measurement" is often the last item since it is usually the final step in the chain of acquiring data. This might not be needed if the experimental data is generated precisely by direct, instrumental measurement.

* **n_levels** [Required] Dictionary (degree of freedom keys) specifying integer number of levels for each degree of freedom. The definition of “level” depends on the degree of freedom. For example, N_levels for lab measurement specifies number of measurements performed on each sample. For a batch degree of freedom, N_levels specifies the the number of batches in the experiment.
* **var_fracs** [Required] Dictionary (degree of freedom keys) specifying random variability to introduce as a percent of the grand mean for each degree of freedom. This can optionally be zero.
* **lvl_val_names** [Optional] Dictionary (degree of freedom keys) of lists specifying names for within degree of freedom levels such as Batch ID's. If specified, the length of the **lvl_val_names** list must match **n_levels** for the degree of freedom.
* **lvl_val_effects** [Optional] Dictionary (degree of freedom keys) of lists specifying effects (as a fraction of grand mean) to apply to the levels as a way of simulating designed experiment effects caused by varying input conditions such as the formulation or process conditions

<p align="center">
  Sampling Degree of Freedom Inputs for a Batch Product Simulation</br>
  <img src=images/case_study1_1.png "Overall Inputs" width=600></br>
</p>
<p align="center">
  Example Level-Specific Inputs</br>
  <img src=images/case_study1_2.png "Level-specific Inputs" width=600></br>
</p>

To run a simulated experiment, instance the **SyntheticExpt** Class and run its **create_experiment_procedure()** method. The output **SyntheticExpt.df_expt** dataframe contains the details, including simulated lab measurement results. See the separate file, case_study1.md, for an example.

<p align="center">
  Class Instancing and Data Output</br>
  <img src=images/case_study1_3.png "Example Experiment and Output" width=400></br>
</p>


J.D. Landgrebe / Data Delve LLC, August 2023