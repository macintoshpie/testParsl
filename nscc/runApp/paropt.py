import os
import time
from string import Template
import numpy as np
import itertools

import parsl
from parsl.executors.threads import ThreadPoolExecutor
from parsl.config import Config
from parsl.app.app import python_app

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from bayes_opt.observer import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs

class ParslOptimizer:
  def __init__(self, parsl_config, parsl_cmd, paropt_config, kappa=2.5):
    self.paropt_config = paropt_config

    self.parsl_config = parsl_config
    self.parsl_cmd = parsl_cmd
    with open(os.path.dirname(os.path.abspath(__file__))+"/"+paropt_config['script_path'], 'r') as f:
      self.command = f.read()
    self.command_params = paropt_config['parameters']
    self.my_logs = "./my_logs_{}_{}.json".format(paropt_config['name'], int(time.time()))
    # create log header
    # FIXME: assuming order when logging, need to investigate...
    with open(self.my_logs, "a") as myfile:
      myfile.write(",".join(list(self.command_params.keys()) + ["negDays"])+"\n")

    # setup point selection model (grid search or bayesian optimization)
    if paropt_config.get('grid_axis_points'):
      # run grid search
      # calculate sample indices for each param
      if paropt_config['grid_axis_points'] < 2:
        raise Exception("grid_axis_points must be >= 2")
      param_ranges = []
      for param, vals in self.command_params.items():
        param_ranges.append(np.linspace(vals[0], vals[1], paropt_config['grid_axis_points']))
      # get cartesian product of param configs
      search_points = itertools.product(*param_ranges)
      # convert sets into dictionaries -   param: value
      # FIXME: I'm assuming it's going through dict keys in same order as above...
      param_names = [name for name, _ in self.command_params.items()]
      self.grid_search_points = []
      for point in search_points:
        self.grid_search_points.append(dict(zip(param_names, point)))
      print("Finished Grid search: ", self.grid_search_points)
    else:
      self.init_points = paropt_config['init_points']
      self.n_iter = paropt_config['n_iter']
      self.optimizer = BayesianOptimization(
        f=None,
        pbounds=self.command_params,
        verbose=2,
        random_state=1,
      )
      self.utility = UtilityFunction(kind="ucb", kappa=kappa, xi=0.0)
      self.logger = JSONLogger(path="./bayes_logs_{}_{}.json".format(paropt_config['name'], int(time.time())))
      self.optimizer.subscribe(Events.OPTMIZATION_STEP, self.logger)

  
  def registerResult(self, params, res):
    # result is assumed to be validated
    self.optimizer.register(
      params=params,
      target=res[2],
    )
  
  def validateResult(self, params, res):
    if res[0] != 0:
      raise Exception("NON_ZERO_EXIT:\n  PARAMS: {}\n  OUT: {}".format(params, res[1]))
  
  def logResult(self, params, res):
    with open(self.my_logs, "a") as mylog:
      mylog.write(",".join(map(str, list(params.values())+[res[2]]))+"\n")
  
  def run(self, savePlots=False, debug=False):
    parsl.set_stream_logger()

    # load configuration - run on local threads if debugging
    if debug:
      local_config = Config(
        executors=[
          ThreadPoolExecutor(
            max_threads=8,
            label='local_threads'
          )
        ]
      )
      parsl.load(local_config)
    else:
      parsl.load(self.parsl_config)

    def prepareAndRun(params, debug):
      """prepares parameters and run the parsl app"""
      # TODO: currently casting all to int - need to check configured type
      params = {key: int(val) for key, val in params.items()}
      cmd = Template(self.command).safe_substitute(params)
      cmd_script = os.path.expanduser("~/timeCmdScript_{}_{}.sh".format(self.paropt_config['name'], int(time.time())))
      with open(cmd_script, "w") as f:
        f.write(cmd)
      return self.parsl_cmd(cmd_script)

    if self.grid_search_points:
      # run grid search
      for point in self.grid_search_points:
        res = prepareAndRun(point, debug).result()
        self.validateResult(point, res)
        self.logResult(point, res)
      return
    # run initial random points
    # do this before loading logs b/c otherwise they won't be random points
    init_params = [self.optimizer.suggest(self.utility) for i in range(self.init_points)]
    init_results = []
    for i in range(self.init_points):
      # wait for the result
      # FIXME: originally these points were run in parallel, but then I realized
      # the tasks were being sent to the same block/node, which I don't want
      res = prepareAndRun(init_params[i], debug).result()
      init_results.append(res)
      self.validateResult(init_params[i], res)
      self.registerResult(init_params[i], res)
    
    # fit previous observations into model
    if self.paropt_config.get('load_logs'):
      load_logs(self.optimizer, logs=[self.paropt_config['load_logs']])
    
    # run remaining tests
    for i in range(self.n_iter):
      probe_point = self.optimizer.suggest(self.utility)
      res = prepareAndRun(probe_point, debug).result()
      self.validateResult(probe_point, res)
      self.registerResult(probe_point, res)
  
  @property
  def max(self):
    return self.optimizer.max
