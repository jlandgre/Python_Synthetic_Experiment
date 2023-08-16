#Version 8/8/23
"""
python -m pytest test_synthetic.py -v -s

#2345678901234567890123456789012345678901234567890123456789012345678901234567890
"""
import sys, os
import pandas as pd
import numpy as np
import pytest

#Append the roll_scripts subdirectory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

#Import project-specific class(es)
from synthetic import SyntheticExpt

@pytest.fixture
def synth():
    """
    A SyntheticExpt experiment with normal variability and user-specified level 
    names and effects
    JDL 8/10/23
    """
    #Define dof names, N levels for each and variability as frac of mean
    names = ['batch-to-batch', 'within batch', 'lab']
    n_levels = dict(zip(names, [2, 3, 2]))
    var_fracs = dict(zip(names, [0.01, 0.005, 0.02]))

    #User-specified lvl_val names and deviations/effects (as frac of mean)
    lvl_val_names = {'batch-to-batch':['Batch A', 'Batch B'], 
                     'within batch':['Top', 'Middle', 'Bottom']}
    lvl_val_effects = {'batch-to-batch':[-0.08, 0.08], 
                       'within batch':[-0.04, 0.0, 0.03]}

    return SyntheticExpt(10000, xbarbar=1.10, names=names, n_levels=n_levels, \
            var_fracs=var_fracs, lvl_val_names=lvl_val_names, \
            lvl_val_effects=lvl_val_effects, digits=4)

@pytest.fixture
def synth_lst_dfs_0(synth):
    synth.create_cum_levels_dict()
    create_df(synth, 'batch-to-batch')
    synth.set_col_names()
    return synth

@pytest.fixture
def synth_lst_dfs_1(synth):
    synth.create_cum_levels_dict()
    create_df(synth, 'within batch')
    synth.set_col_names()
    return synth

def create_df(synth, name):
    """
    Helper function for creating fixtures
    """
    synth.create_cum_levels_dict()
    n_levels = synth.n_levels[name]
    cum_levels = synth.cum_levels[name]
    var_frac = synth.var_fracs[name]

    synth.create_dof_df(name, n_levels, cum_levels, var_frac)
    synth.set_col_names()
    return synth

def synth2():
    """
    A SyntheticExpt experiment with normal variability only -- no user-specified  
    level names and effects
    JDL 8/10/23
    """
    #Define dof names, N levels for each and variability as frac of mean
    names = ['batch-to-batch', 'within batch', 'lab']
    n_levels = dict(zip(names, [2, 3, 2]))
    var_fracs = dict(zip(names, [0.01, 0.005, 0.02]))

    return SyntheticExpt(10000, xbarbar=1.10, names=names, n_levels=n_levels, \
            var_fracs=var_fracs, digits=4)

def test_add_measurement_col(synth):
    """
    Add a simulated measurement column to the experiment df
    (xbarbar + sum of deviations for each degree of freedom
    + sum of effects for each degree of freedom)
    JDL 8/10/23
    """
    synth.create_cum_levels_dict()
    synth.create_lst_dof_dfs()
    synth.set_col_names()
    synth.add_level_name_and_effect_cols()
    synth.create_experiment_df()
    synth.add_measurement_col()

    assert 'sim_meas' in synth.df_expt.columns
    sum_expected = synth.xbarbar
    for col in ['devns_batch-to-batch', 'devns_within batch', 'devns_lab', \
                'effect_batch-to-batch', 'effect_within batch']:
        sum_expected += synth.df_expt.loc[0, col]

    assert np.isclose(sum_expected, synth.df_expt.loc[0, 'sim_meas'], atol=0.0001)

def test_create_experiment_df(synth):
    """
    Create experiment's output dataframe
    JDL 8/10/23
    """
    synth.create_cum_levels_dict()
    synth.create_lst_dof_dfs()
    synth.set_col_names()
    synth.add_level_name_and_effect_cols()
    synth.create_experiment_df()

    #Check columns are as expected
    cols_expected = ['level_batch-to-batch', 'devns_batch-to-batch', \
                    'batch-to-batch', 'effect_batch-to-batch', \
                    'level_within batch', 'devns_within batch', \
                    'within batch', 'effect_within batch', \
                    'level_lab', 'devns_lab', 'effect_lab']
    assert synth.df_expt.columns.tolist() == cols_expected

    #Check values
    assert synth.df_expt['effect_lab'].tolist() == 12 * [0.0]

    vals = synth.df_expt['effect_batch-to-batch'].values
    np_ary_expected = np.array(6 * [-0.088] + 6 * [0.088])
    result = np.isclose(vals, np_ary_expected, atol=0.0001)
    assert result.all()

    vals = synth.df_expt['effect_within batch'].values
    np_ary_expected = np.array(2 * [-0.044, -0.044, 0.0, 0.0, 0.033, 0.033])
    result = np.isclose(vals, np_ary_expected, atol=0.0001)
    assert result.all()

    assert synth.df_expt['batch-to-batch'].tolist() \
        == 6 * ['Batch A'] + 6 * ['Batch B']
    assert synth.df_expt['within batch'].tolist() \
        == 2 * ['Top', 'Top', 'Middle', 'Middle', 'Bottom', 'Bottom']

def test_add_level_name_and_effect_cols(synth):
    """
    Add level name and effect columns to each dof's dataframe
    JDL 8/10/23
    """
    synth.create_cum_levels_dict()
    synth.create_lst_dof_dfs()
    synth.set_col_names()
    synth.add_level_name_and_effect_cols()

    #synth Class setup specifies lvl val names and effects for 2 of 3 dofs - not 'lab'
    assert 'batch-to-batch' in synth.lvl_val_names
    assert 'within batch' in synth.lvl_val_names
    assert not 'lab' in synth.lvl_val_names

    assert 'batch-to-batch' in synth.lvl_val_effects
    assert 'within batch' in synth.lvl_val_effects
    assert not 'lab' in synth.lvl_val_effects

    #Check that columns were created
    for df in synth.lst_dfs:
        if df.index.name in synth.lvl_val_names:
            assert 'lvl_names' in df.columns
        if df.index.name in synth.lvl_val_effects:
            assert 'lvl_effects' in df.columns

    #Check lvl_names and lvl_effects values
    assert synth.lst_dfs[0]['lvl_names'].tolist() == ['Batch A', 'Batch B'] 
    assert synth.lst_dfs[1]['lvl_names'].tolist() == 2 * ['Top', 'Middle', 'Bottom']
    
    vals = synth.lst_dfs[0]['lvl_effects'].values
    np_ary_expected = np.array([-0.088, 0.088])
    result = np.isclose(vals, np_ary_expected, atol=0.0001)
    assert result.all()

    vals = synth.lst_dfs[1]['lvl_effects'].values
    np_ary_expected = np.array(2 * [-0.044, 0.0, 0.033])
    result = np.isclose(vals, np_ary_expected, atol=0.0001)
    assert result.all()

def test_create_dof_lvl_effects_col1(synth_lst_dfs_1):
    """
    Create column with effect values (frac of mean) in df for dof
    (called if lvl_val_names is not None)
    JDL 8/8/23
    """
    #Add a dummy 0-index df to lst_dfs
    synth_lst_dfs_1.lst_dfs.insert(0, pd.DataFrame())

    synth_lst_dfs_1.create_dof_lvl_effects_col(idx_df=1)
    df = synth_lst_dfs_1.lst_dfs[1]
    #print('\n\n', df, '\n\n ')

    assert 'lvl_effects' in df.columns
    
    vals = df['lvl_effects'].values
    np_ary_expected = np.array(2 * [-0.044, 0.0, 0.033])
    result = np.isclose(vals, np_ary_expected, atol=0.0001)
    assert result.all()

def test_create_dof_lvl_effects_col0(synth_lst_dfs_0):
    """
    Create column with effect values (frac of mean) in df for dof
    (called if lvl_val_names is not None)
    JDL 8/8/23
    """
    synth_lst_dfs_0.create_dof_lvl_effects_col(idx_df=0)
    df = synth_lst_dfs_0.lst_dfs[0]
    #print('\n\n', df, '\n\n ')

    assert 'lvl_effects' in df.columns

    vals = df['lvl_effects'].values
    np_ary_expected = np.array([-0.088, 0.088])
    result = np.isclose(vals, np_ary_expected, atol=0.0001)
    assert result.all()

def test_create_dof_lvl_names_col1(synth_lst_dfs_1):
    """
    Create column with level names in df for dof
    (called if lvl_val_names is not None)
    JDL 8/8/23
    """
    #Add a dummy 0-index df to lst_dfs
    synth_lst_dfs_1.lst_dfs.insert(0, pd.DataFrame())

    synth_lst_dfs_1.create_dof_lvl_names_col(idx_df=1)
    df = synth_lst_dfs_1.lst_dfs[1]
    #print('\n\n', df, '\n\n ')

    assert 'lvl_names' in df.columns
    assert df['lvl_names'].tolist() == ['Top', 'Middle', 'Bottom', 'Top', 'Middle', 'Bottom']

def test_create_dof_lvl_names_col0(synth_lst_dfs_0):
    """
    Create column with level names in df for dof
    (called if lvl_val_names is not None)
    JDL 8/8/23
    """
    synth_lst_dfs_0.create_dof_lvl_names_col(idx_df=0)
    df = synth_lst_dfs_0.lst_dfs[0]
    #print('\n\n', df, '\n\n ')

    assert 'lvl_names' in df.columns
    assert df['lvl_names'].tolist() == ['Batch A', 'Batch B']

def test_set_col_names(synth):
    """
    Set column names for experiment's output dataframe
    JDL 8/8/23
    """
    #Create dummy Dataframes and name it
    df = pd.DataFrame(index=range(0, 2))
    df.index.name = 'test'
    synth.lst_dfs.append(df)
    synth.set_col_names()
    assert synth.lst_idx_cols == ['level_test']
    assert synth.lst_devn_cols == ['devns_test']
    assert synth.lst_lvl_names_cols == ['test']
    assert synth.lst_lvl_effects_cols == ['effect_test']

def test_create_dof_df(synth_lst_dfs_0):
    df = synth_lst_dfs_0.lst_dfs[0]

    assert df.shape == (2, 2)
    assert df.index.name == 'batch-to-batch'
    assert df['level'].tolist() == [1, 2]

def test_cum_levels_dict(synth):
    """
    Calculate cumulative number of levels at each degree of freedom
    JDL 8/8/23
    """
    synth.create_cum_levels_dict()
    assert synth.cum_levels == {'batch-to-batch': 2, 'within batch': 6, 'lab': 12}

def test_synth_fixture(synth):
    """
    Check fixture instantiation
    JDL 8/8/23
    """
    assert isinstance(synth, SyntheticExpt)
    assert synth.names == ['batch-to-batch', 'within batch', 'lab']