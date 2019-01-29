import parsl
from parsl.executors.threads import ThreadPoolExecutor
from parsl.app.app import python_app

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction

from parslLibrary import timeCmd

class ParslOptimizer:
  def __init__(self, command, command_params, init_points, n_iter, parsl_config):
    self.parsl_config = parsl_config
    self.command = command
    self.command_params = command_params

    self.init_points = init_points
    self.n_iter = n_iter
    self.optimizer = BayesianOptimization(
      f=None,
      pbounds=command_params,
      verbose=2,
      random_state=1,
    )
    self.utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)
  
  def registerResult(params, res):
    if res[0] == 0:
      # invert result (trying to MINIMIZE time)
      self.optimizer.register(
        params=params,
        target=-res[2],
      )
    else:
      raise Exception("NON_ZERO_EXIT:\n  PARAMS: {}\n  OUT: {}".format(params, res[1]))
  
  def run(self, debug):
    parsl.set_stream_logger()

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
    
    cmd = self.command
    if debug:
      cmd = '#!/usr/bin/env bash\n' + '\n'.join(["{}: {}".format(n, params[name]) for n in params])

    def prepareAndRun(params, debug=False):
      # TODO: currently casting all to int - need to check configured type
      params = {key: int(val) for key, val in params.items()}
      cmd = self.command
      if debug:
        cmd = '#!/usr/bin/env bash\n' + '\n'.join(['{}: {}'.format(n, params[n]) for n in params])
      return timeApp(cmd, params, True)

    # attempt to run initial, random points in parallel
    init_params = []
    init_futures = []
    for i in range(self.init_points):
      init_params.append(self.optimizer.suggest(utility))
      init_futures.append(prepareAndRun(init_params[i], debug))
    
    # Wait for initial results before continuing
    # add results to GP model
    for init_point, init_fut in zip(init_params, init_futures):
      res = init_fut.result()
      self.registerResult(init_point, res)
    
    # run remaining tests
    for i in range(n_iter):
      probe_point = bo.suggest(utility)
      res = prepareAndRun(probe_point, debug).result()
      self.registerResult(probe_point, res)
    
  def registerResult(self, point, result):
    if res[0] == 0:
      bo.register(
          params=params,
          target=res[2],
      )
    else:
      raise Exception("NON_ZERO_EXIT:\n  PARAMS: {}\n  OUT: {}".format(params, res[1]))
  
  @property
  def max():
    return self.optimizer.max

    

    



    
    