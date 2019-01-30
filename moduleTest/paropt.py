import os

import parsl
from parsl.executors.threads import ThreadPoolExecutor
from parsl.config import Config
from parsl.app.app import python_app

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction

from parslLibrary import timeCmd

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec

class ParslOptimizer:
  def __init__(self, parsl_config, command, command_params, init_points, n_iter, kappa=2.5):
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
    self.utility = UtilityFunction(kind="ucb", kappa=kappa, xi=0.0)
  
  def registerResult(params, res):
    if res[0] == 0:
      self.optimizer.register(
        params=params,
        target=res[2],
      )
    else:
      raise Exception("NON_ZERO_EXIT:\n  PARAMS: {}\n  OUT: {}".format(params, res[1]))
  
  def run(self, debug):
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

    def prepareAndRun(params, debug=False):
      """prepares parameters and run the parsl app"""
      # TODO: currently casting all to int - need to check configured type
      params = {key: int(val) for key, val in params.items()}
      cmd = self.command
      if debug:
        cmd = '#!/usr/bin/env bash\n' + '\n'.join(['echo "{}: {}"'.format(n, params[n]) for n in params])
      return timeCmd(cmd, params, True)

    # attempt to run initial, random points in parallel
    init_params = []
    init_futures = []
    for i in range(self.init_points):
      init_params.append(self.optimizer.suggest(self.utility))
      init_futures.append(prepareAndRun(init_params[i], debug))
    
    # Wait for initial results before continuing
    # add results to GP model
    for init_point, init_fut in zip(init_params, init_futures):
      res = init_fut.result()
      self.registerResult(init_point, res)
    
    # plot it
    for p in self.command_params:
      self.generatePlot(p)
    
    # run remaining tests
    for i in range(self.n_iter):
      probe_point = self.optimizer.suggest(self.utility)
      res = prepareAndRun(probe_point, debug).result()
      self.registerResult(probe_point, res)
      # plot it
      for p in self.command_params:
        self.generatePlot(p)
    
  def registerResult(self, point, result):
    if result[0] == 0:
      self.optimizer.register(
          params=point,
          target=result[2],
      )
    else:
      raise Exception("NON_ZERO_EXIT:\n  PARAMS: {}\n  OUT: {}".format(point, result[1]))
  
  @property
  def max(self):
    return self.optimizer.max

  def generatePlot(self, paramName):
    # code taken from BayesianOptimization module notebook:
    # https://github.com/fmfn/BayesianOptimization/blob/master/examples/visualization.ipynb
    def posterior(x_obs, y_obs, grid):
      self.optimizer._gp.fit(x_obs, y_obs)

      mu, sigma = self.optimizer._gp.predict(grid, return_std=True)
      return mu, sigma

    def plot_gp(paramName):
      x_lims = self.command_params[paramName]
      x = np.linspace(x_lims[0], x_lims[1], 10000).reshape(-1, 1)
      fig = plt.figure(figsize=(16, 10))
      steps = len(self.optimizer.space)
      fig.suptitle(
        'Gaussian Process and Utility Function for Param {} After {} Steps'.format(paramName, steps),
        fontdict={'size':30}
      )
      
      gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
      axis = plt.subplot(gs[0])
      acq = plt.subplot(gs[1])
      
      x_obs = np.array([[res["params"][paramName]] for res in self.optimizer.res])
      y_obs = np.array([res["target"] for res in self.optimizer.res])
      
      mu, sigma = posterior(x_obs, y_obs, x)
      axis.plot(x_obs.flatten(), y_obs, 'D', markersize=8, label=u'Observations', color='r')
      axis.plot(x, mu, '--', color='k', label='Prediction')

      axis.fill(np.concatenate([x, x[::-1]]), 
        np.concatenate([mu - 1.9600 * sigma, (mu + 1.9600 * sigma)[::-1]]),
        alpha=.6, fc='c', ec='None', label='95% confidence interval')
      
      axis.set_xlim(x_lims)
      axis.set_ylim((None, None))
      axis.set_ylabel('f(x)', fontdict={'size':20})
      axis.set_xlabel('x', fontdict={'size':20})
      
      utility_function = self.utility
      utility = utility_function.utility(x, self.optimizer._gp, 0)
      acq.plot(x, utility, label='Utility Function', color='purple')
      acq.plot(x[np.argmax(utility)], np.max(utility), '*', markersize=15, 
        label=u'Next Best Guess', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1)
      acq.set_xlim((-2, 10))
      acq.set_ylim((0, np.max(utility) + 0.5))
      acq.set_ylabel('Utility', fontdict={'size':20})
      acq.set_xlabel('x', fontdict={'size':20})
      
      axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
      acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)

      plt.savefig(os.path.dirname(os.path.realpath(__file__)) + '/paropt_steps-{}_param-{}.png'.format(steps, paramName))
    
    plot_gp(paramName)