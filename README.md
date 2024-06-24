# Hyperparameter_sweep
code to create configurationfiles and jobscripts or all possible combinations of hyperparameters. This includes a check if the combination aldready exists. 


This code has some room for improvement: 
1. Save new combinations by adding instead of re-writing. (possible solution in branch)
2. The base temlate should be complete with a "standard" configuration, as it is now only the hyperparameters thet I have picked can be changed and they also needs to have a value assigned even if it is kept constant in the specifc sweep.
3. The input to the function could be better, maby the dict of hyperparameters is from a separate file? Maby you get a prompt to fill in name of the seew and filenames?
4. Perhaps the biggest improvement would be if the script could include os.system('sbatch jobscript_{name}_%i' % (i+1)) or somthing equivelent.
6. When it is deployed to alvis there are 2 things to consider:
   - The thousends of files that are generated should be placed in a ziped file on Alvis. 
   - The jobbs should be submitted as an array to alvis sbatch --array=1-400 my_jobscript.sh 
