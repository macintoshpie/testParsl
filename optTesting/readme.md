## Context
Ran Parsl with bayesian optimization package, with number of cpus and memory per cpu as variables  
It randomly chose configurations for two runs (see bayes_log.json)  
I killed it after those two ran becuase of problem below  

## Problem
After running the application with two randomly selected configurations, I 'asked' for the next configuration
to basically returned the better of the two configs I had just tested.  
My understanding of how it suggests the next point is by fitting a gaussian process with the data, 
then using a utility function (in this case we used upper conficence bound) searches for a point in the process 
with the highest predicted utility.  
After investigating (see the notebook) it seems that our gaussian process is not fitting in a desirable way  
If you look at the figures in the notebook, I've recreated the gaussian processes, and plotted the predicted  
function along with the 95% confidence intervals.  
The problem is that the fit is a flat line at the average of the two points, and spikes sharply to the
points before returning back to the average.  
So as you can imagine, looking at the UCB of this fucntion is just going to pick points very very close
to the current best value (which we obviously don't want...)  

## How to fix this
I tried fooling around with the kappa value of the utility function, which determines the explore/exploit proneness 
but that didn't help. Plus it's pretty obvious by the graphs that the fit is bad  
So now I think it must be the configuration of our gaussian process regressor's kernel  
But this is something I know very little about.  
I've played around with these things in the notebook, but I really don't know what I'm doing  
Here are the resources I've found:  
general info about gp kernels: https://www.cs.toronto.edu/~duvenaud/cookbook/  
sklearn kernels for gp (which is what we're using): https://scikit-learn.org/stable/modules/gaussian_process.html#gp-kernels  
has an OK section on sklearn gp kernels: https://blog.dominodatalab.com/fitting-gaussian-process-models-python/  
the gaussian process regressor we're using: https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html#sklearn.gaussian_process.GaussianProcessRegressor.fit  
