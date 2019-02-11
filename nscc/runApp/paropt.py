import os
import time
from string import Template

import parsl
from parsl.executors.threads import ThreadPoolExecutor
from parsl.config import Config
from parsl.app.app import python_app

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from bayes_opt.observer import JSONLogger
from bayes_opt.event import Events

class ParslOptimizer:
  def __init__(self, parsl_config, parsl_cmd, paropt_config, kappa=2.5):
    self.paropt_config = paropt_config

    self.parsl_config = parsl_config
    self.parsl_cmd = parsl_cmd
    with open(os.path.dirname(os.path.abspath(__file__))+"/"+paropt_config['script_path'], 'r') as f:
      self.command = f.read()
    self.command_params = paropt_config['parameters']

    self.init_points = paropt_config['init_points']
    self.n_iter = paropt_config['n_iter']
    self.optimizer = BayesianOptimization(
      f=None,
      pbounds=self.command_params,
      verbose=2,
      random_state=1,
    )
    self.utility = UtilityFunction(kind="ucb", kappa=kappa)
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

    # run initial random points
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
    
    # run remaining tests
    for i in range(self.n_iter):
      probe_point = self.optimizer.suggest(self.utility)
      res = prepareAndRun(probe_point, debug).result()
      self.validateResult(probe_point, res)
      self.registerResult(probe_point, res)
  
  @property
  def max(self):
    return self.optimizer.max
