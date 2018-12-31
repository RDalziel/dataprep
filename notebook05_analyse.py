#%% [markdown]
# # Stage 5 - Analyse
# This is where we want to apply all of the generic data quality checks

# ## Common
# So this is where we are trying to do all the common stuff to ingest all of the files.  Key is recognition that there are common patterns we can exploit across the files.
# NOTE - still to figure out how to do this from a single file and import it successfully.

#%%
# Import all of the libraries we need to use...
import pandas as pd
import azureml.dataprep as dprep
import seaborn as sns
import os as os
import re as re
import collections
from azureml.dataprep import value
from azureml.dataprep import col
from azureml.dataprep import Package

# Let's also set up global variables and common functions...

# Path to the source data
dataPath = "./data"

# Path to the location where the dataprep packags that are created
packagePath = "./packages"

# Name of package file
packageFileSuffix = "_package.dprep"

# A helper function to create full package path
def createFullPackagePath(packageName, stage, qualityFlag):
    return packagePath + '/' + packageName + '_' + stage + '_' + qualityFlag + packageFileSuffix

# A save package helper function
def savePackage(dataFlowToPackage, packageName, stage, qualityFlag):
    dataFlowToPackage = dataFlowToPackage.set_name(packageName)
    packageToSave = dprep.Package(dataFlowToPackage)
    fullPackagePath = createFullPackagePath(packageName, stage, qualityFlag)
    packageToSave = packageToSave.save(fullPackagePath)
    return fullPackagePath

# An open package helper function
def openPackage(packageName, stage, qualityFlag):
    fullPackagePath = createFullPackagePath(packageName, stage, qualityFlag)
    packageToOpen = Package.open(fullPackagePath)
    dataFlow = packageToOpen[packageName]
    return dataFlow

#%% [markdown]
# ## Open CANONICAL data flow
# NOTE - Should be picking up canonical data flow from stage 4, but we don't have that defined yet.
# So will pick up pick up the JOINED the data flow from stage 3 for now and refactor later on...

#%%
canonicalDataFlow = openPackage('JOINED', '3', 'A')

#%% [markdown]
# ## Date Checks

# ### Check : Date Joined Company is after Date Joined Scheme

#%%
canonicalDataFlow = canonicalDataFlow.add_column(new_column_name='Test1',
                           prior_column='MEMBERS_DJS',
                           expression=canonicalDataFlow['MEMBERS_DJS'] > canonicalDataFlow['PEOPLE_DOB'])


#%%
canonicalDataFlow = canonicalDataFlow.new_script_column(new_column_name='Test2', insert_after='Test1', script="""
def newvalue(row):
    return 'ERROR - DJS earlier than DJC'
""")

#%%
canonicalDataFlow.get_profile()

#%%
canonicalDataFlow.head(20)

#%% [markdown]
# ### Check : Date of Birth is after Date Joined Scheme