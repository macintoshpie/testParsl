## Ted's Practicum Notes

I have two repos which automate optimization. One being a messy prototype (this repository), and another which is a bit more organized and has the ability to save results to a database (see the paropt repository). 

You should use this repository on NSCC just for now since I haven't had time to test the new stuff on it.  
If you want to run stuff on AWS, use the paropt repository. 

### NSCC Setup
Perform the following steps logged in on Aspire  
```bash
# load anaconda
module load anaconda/3
conda create --name parsl_py36 python=3.6
source activate parsl_py36
# NOTE: on ASPIRE 1, it is necessary to force compilation of the zmq bindings.
# First, make sure that all versions of pyzmq are removed from the path.
python3 -m pip install --no-binary pyzmq pyzmq
# package for doing bayesian optimization
python3 -m pip install bayesian-optimization
python3 -m pip install numpy

# clone parsl so we can do a hacky modification later to the torque template
git clone https://github.com/Parsl/parsl.git
# clone this repo for running the optimization
git clone https://github.com/macintoshpie/testParsl.git
```

Now we'll update and install parsl. Go into the cloned parsl repo, and edit the torque/pbs template file so that the nodes line looks like this:
```
#PBS -l nodes=${nodes_per_block}:ppn=24
```
In my case, I always wanted to request 24 cores, but maybe your case is different. As far as I could tell this seemed to be the easiest way to request 24 cores for a node (see this issue: https://github.com/Parsl/parsl/issues/669)

Then pip install the modified parsl
```
cd parsl
pip install ./
```

Lastly, you'll need to make sure you have the actual tool setup that you want to test, as well as the data for testing it.

### NSCC Usage
To run the optimizer on a tool, you'll need a config file and a bash/shell script to actually run your tool.

#### Experiment Configuration
The config script is a json file with the following attributes:
- name: the name of the experiment you're running
- script_path: a path to the bash/shell file which runs the tool
- parameters: an object keyed by a parameter name and its range of possible values for testing. The parameter name must exactly match the names inside of your template script (script_path) in order for their values to get substituted in.
- init_points: number of trials to run with random configurations
- n_iter: number of trials to run using the model, after the random points have been evaluated
- grid_axis_points: this field is mutually exclusive with the two fields above (init_points and n_iter) - ie you can only have init_points and n_iter OR only grid_axis_points. This field indicates you want to run a grid search, with this number of configurations for each parameter linearly spaced apart. Note that this will run a total of `grid_axis_points^(number of parameters)` trials because it takes the cartesian cross product of the configurations.
- walltime: how much *TOTAL* walltime you need to run all trials
- load_logs: this is an optional field which points to a bayes_logs.json file which has previous results for running the same tool with the same configuration. Those results will be loaded into the model after the initial random points are run, and before the iter points are run.  

I would recommend checking out the configuration files for tools in this repo - they're usually named configToolName.json.

Here's an example of a config file and a script file.

paroptConfig.json:
```
{
  "name": "platypus",
  "script_path": "../platypus/runPlatypus.sh",
  "parameters": {
    "nCPU": [4, 24],
    "bufferSize": [100000, 400000]
  },
  "walltime": "10:00:00",
  "init_points": 2,
  "n_iter": 3
}
```

runTool.sh:
```
bam="chr1rg.bam"
ref="GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"

vcf="${HOME}/results/chr1platypus.vcf.gz"

# see here for configs:
# https://www.well.ox.ac.uk/research/research-groups/lunter-group/softwares/platypus-documentation

echo "Loading platypus env"
source activate platypus_py27
echo "Starting platypus..."
platypus callVariants --bamFiles=${bam} --refFile=${ref} --output=${vcf} --nCPU ${nCPU} --bufferSize ${bufferSize}
```

#### Run Experiment
On NSCC you can't run these long parsl processes without them being shutdown. So you have to run the parsl head on a node as well. This repository has another script for automating that for: `nscc/runApp/submit.py`.
With your parsl_py36 env loaded:
```
python3 submit.py path/to/configTool.json
```
From there you should be good to go.

#### Results
Since this was a prototype, files are scattered all over the place.  
The results (ie configuration values and resulting runtimes) should be stored in your home directory, labeled something like `bayes_logs_toolname_1234321431.json` where the numbers are the time the first run was completed. This is the file that is loadable in future runs, if the path to this file is given in the config.json.  
If you did a grid search, it should put the results in a file called `my_logs_toolname_1234321231.csv` (note that this file still gets created even if you're not running a grid search...).  
You can also see the templated scripts it's running in the home directory, they should be named something like `timeCmd_toolname_1234321234.sh`.  
Stderr and stdout of the head node are directed to files in the directories `~/errorfiles` and `~/outputfiles`.

### Visualization
Checkout the notebooks in the optTesting directory for visualization stuff.