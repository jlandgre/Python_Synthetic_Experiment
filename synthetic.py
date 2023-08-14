import pandas as pd
import numpy as np

class SyntheticData:
    """
    This class generates normally-distributed synthetic data for a simulated measurement
    JDL 8/7/23
    """
    def __init__(self, len_seed_dist, xbarbar=None, names=None, n_levels=None, var_fracs=None, \
                 lvl_val_names={}, lvl_val_effects={}, digits=None, meas_nm=None):
            
            #Generate a seed distribution of normally distributed data
            self.dist_seed_normal = pd.Series(np.random.normal(loc=0.0, scale=1.0, size=len_seed_dist))
            self.dist_seed_normal.name = "dist_seed_normal"
            
            #Experiments based on multiple degrees of freedom (aka deg-of-freedom)
            self.df_data = None #Temporary df
            self.lst_dfs = []   #List of df's for each deg-of-freedom
            self.xbarbar = xbarbar  #Grand mean for measurement
            self.names = names  #List of deg-of-freedom names (e.g. batch-to-batch, lab etc.)
            self.n_levels = n_levels    #Dict of N levels/permutations for each deg-of-freedom
            self.var_fracs = var_fracs  #Dict of variabilities for each deg-of-freedom (frac of mean)
            self.digits = digits        #Number of digits for rounding
            self.meas_nm = meas_nm      #Name of measurement
            self.cum_levels = {}        #Dict of cumulative N levels for each deg-of-freedom

            #Variables for naming within-dof levels and specifying level deviations
            self.lvl_val_names = lvl_val_names #Dict of level names for specific deg-of-freedom
            self.lvl_val_effects = lvl_val_effects #List of level deviations for specific deg-of-freedom

            # Column names for experiment's output dataframe
            self.lst_idx_cols = []
            self.lst_devn_cols = []

            # Column names for within-dof level names and level effects
            self.lst_lvl_names_cols = []
            self.lst_lvl_effects_cols = []

    def scaled_val(self, mean, sdev):
        """
        Pick a random val from seed distribution
        """
        idx = np.random.choice(self.dist_seed_normal.index)
        return mean + (self.dist_seed_normal[idx] * sdev)
    
    def gen_synthetic_data(self, len_data, mean, sdev, digits):
        """
        Generate a specified number of data points with specified mean and standard deviation
        """
        self.df_data = pd.DataFrame(index=range(len_data))
        self.df_data['vals'] = np.nan
        self.df_data['vals'] = self.df_data.apply(lambda row: self.scaled_val(mean, sdev), axis=1)
        self.df_data['vals'] = self.df_data['vals'].round(digits)

    """
    ================================================================================
    Generate synthetic experiment - random variation in degrees of freedom
    ================================================================================
    """
    def create_experiment_procedure(self):
        self.create_cum_levels_dict()
        self.create_lst_dof_dfs()
        self.set_col_names()
        self.add_level_name_and_effect_cols()
        self.create_experiment_df()
        self.add_measurement_col()
    
    def create_cum_levels_dict(self):
        """
        Calculate cumulative number of levels at each degree of freedom
        """
        cum_lvls = 1
        for name in self.names:
            cum_lvls *= self.n_levels[name]
            self.cum_levels[name] = int(cum_lvls)

    def create_lst_dof_dfs(self):
        """
        Create df's for all degrees of freedom
        """
        for name in self.names:
            self.create_dof_df(name, self.n_levels[name], self.cum_levels[name], self.var_fracs[name])
    
    def create_dof_df(self, name, n_levels, cum_levels, var_frac):
        """
        Create a DataFrame with deviations (as frac of mean) for a degree of freedom
        JDL 8/7/23
        """
        #Generate synthetic data based on specified mean and variability for deg. of freedom
        self.gen_synthetic_data(cum_levels, self.xbarbar, self.xbarbar * var_frac, 4)
        df = self.df_data
        
        #label the levels for current degree of freedom (index from 1)
        len_lvl_block = int(cum_levels / n_levels)
        df['level'] = [j for i in range(len_lvl_block) for j in range(1, n_levels + 1)]
        
        #Calculate deviation column (in units of measurement); drop measurement
        df['devns'] = df['vals'] - self.xbarbar
        df.drop('vals', inplace=True, axis=1)
        
        #Name the index to make the DataFrame identifiable
        df.index.name = name

        #Add the DataFrame to the list of degree-of-freedom DataFrames
        self.lst_dfs.append(df)

    def set_col_names(self):
        """
        Set column names for experiment's output dataframe
        JDL 8/8/23
        """
        for df in self.lst_dfs:
            self.lst_idx_cols.append('level_' + df.index.name)
            self.lst_devn_cols.append('devns_' + df.index.name)
            self.lst_lvl_names_cols.append(df.index.name)
            self.lst_lvl_effects_cols.append('effect_' + df.index.name)
            #self.lst_lvl_names_cols.append('lvl_names_' + df.index.name)
            #self.lst_lvl_effects_cols.append('lvl_effects_' + df.index.name)
    
    def add_level_name_and_effect_cols(self):
        """
        Add level name and effect columns to each dof's dataframe
        JDL 8/10/23
        """
        for idx_df in range(0, len(self.lst_dfs)):

            #Create a level name and effect value column if specified
            name_df = self.lst_dfs[idx_df].index.name
            if name_df in self.lvl_val_names: self.create_dof_lvl_names_col(idx_df)
            if name_df in self.lvl_val_effects: self.create_dof_lvl_effects_col(idx_df)
            
    def create_dof_lvl_names_col(self, idx_df):
        """
        Create column with level names in df for dof
        (called if lvl_val_names is not None)
        JDL 8/10/23
        """
        #Create dictionary of integer level keys and specified lvl val names
        name = self.names[idx_df]
        lst_levels = list(range(1, self.n_levels[name] + 1))
        dict_lvl_val_names = dict(zip(lst_levels, self.lvl_val_names[name]))

        #Map levls to level val names
        self.lst_dfs[idx_df]['lvl_names'] = self.lst_dfs[idx_df]['level'].map(dict_lvl_val_names)

    def create_dof_lvl_effects_col(self, idx_df):
        """
        Create column with effect values (frac of mean) in df for dof
        (called if lvl_val_names is not None)
        JDL 8/10/23
        """
        #Create dictionary of integer level keys and specified lvl val effect values
        name = self.names[idx_df]
        lst_levels = list(range(1, self.n_levels[name] + 1))
        dict_lvl_val_effects = dict(zip(lst_levels, self.lvl_val_effects[name]))

        #Map levls to level val names
        self.lst_dfs[idx_df]['lvl_effects'] = \
            self.lst_dfs[idx_df]['level'].map(dict_lvl_val_effects)
        
        #Convert effect values from frac of mean to measurement units
        self.lst_dfs[idx_df]['lvl_effects'] *= self.xbarbar

    def create_experiment_df(self):
        """
        Create a DataFrame for the experiment with simulated measurement data for sampling
        and detailed columns for each degree of freedom
        JDL 8/8/23
        """
        n_rows = self.cum_levels[self.names[-1]]
        self.df_expt = pd.DataFrame(index=range(0, n_rows))

        #Iterate over degrees of freedom and add columns for level ids and deviations
        for idx_df in range(0, len(self.lst_dfs)):
        
            #Block length is n_rows total divided by cum_levels for current degree of freedom
            len_lvl_block = int(n_rows / self.cum_levels[self.names[idx_df]])

            #Set temp variables for readability
            df, col, col_devn, col_name, col_effect = self.set_expt_col_names(idx_df)

            #Iterate over df rows (level, devn) for each degree of freedom
            idx_0 = 0
            for idx in df.index:
                
                #Define a df_expt block row slice for the level and deviation and set values
                row_slice = self.df_expt.index[idx_0:(idx_0 + len_lvl_block)]
                self.set_expt_row_slice_vals(row_slice, idx, df, col, col_devn, col_name, col_effect)

                #Increment to start of next block slice
                idx_0 += len_lvl_block
                
            #Convert idx col to integer
            self.df_expt[col] = self.df_expt[col].astype(int)

    def set_expt_col_names(self, idx_df):
        """
        For readability, set temp variables for df and column names
        JDL 8/8/23
        """
        df = self.lst_dfs[idx_df]
        col = self.lst_idx_cols[idx_df]
        col_devn = self.lst_devn_cols[idx_df]
        col_name = self.lst_lvl_names_cols[idx_df]
        col_effect = self.lst_lvl_effects_cols[idx_df]
        return df, col, col_devn, col_name, col_effect

    def set_expt_row_slice_vals(self, row_slice, idx, df, col, col_devn, col_name, col_effect):
        self.df_expt.loc[row_slice, col] = df.loc[idx, 'level']
        self.df_expt.loc[row_slice, col_devn] = df.loc[idx, 'devns']
        if 'lvl_names' in df.columns:
            self.df_expt.loc[row_slice, col_name] = df.loc[idx, 'lvl_names']

        #Add level effects = 0 if not specified
        if 'lvl_effects' in df.columns:
            self.df_expt.loc[row_slice, col_effect] = df.loc[idx, 'lvl_effects']
        else:
            self.df_expt.loc[row_slice, col_effect] = 0.0

    def add_measurement_col(self):
        """
        Add a simulated measurement column to the experiment df
        (xbarbar + sum of deviations for each degree of freedom)
        + sum of effects for each degree of freedom)
        JDL 8/10/23
        """
        self.df_expt['sim_meas'] = self.xbarbar
        for col in self.lst_devn_cols:
            self.df_expt['sim_meas'] +=  self.df_expt[col]

        for col in self.lst_lvl_effects_cols:
            self.df_expt['sim_meas'] +=  self.df_expt[col]
        
        self.df_expt['sim_meas'] = self.df_expt['sim_meas'].round(self.digits)

        if not self.meas_nm is None:
            self.df_expt.rename(columns={'sim_meas': self.meas_nm}, inplace=True)

            