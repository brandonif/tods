from typing import Any, Callable, List, Dict, Union, Optional, Sequence, Tuple
from numpy import ndarray
from collections import OrderedDict
from scipy import sparse
import os
import sklearn
# import numpy
import typing

# Custom import commands if any
import warnings
import numpy as np
from sklearn.utils import check_array
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted
from sklearn.linear_model import LinearRegression
# from numba import njit
from pyod.utils.utility import argmaxn

from d3m.container.numpy import ndarray as d3m_ndarray
from d3m.container import DataFrame as d3m_dataframe
from d3m.metadata import hyperparams, params, base as metadata_base
from d3m import utils
from d3m.base import utils as base_utils
from d3m.exceptions import PrimitiveNotFittedError
from d3m.primitive_interfaces.base import CallResult, DockerContainer

# from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from d3m.primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase
from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase

from d3m.primitive_interfaces.base import ProbabilisticCompositionalityMixin, ContinueFitMixin
from d3m import exceptions
import pandas

from d3m import container, utils as d3m_utils

from .UODBasePrimitive import Params_ODBase, Hyperparams_ODBase, UnsupervisedOutlierDetectorBase
from .core.MultiAutoRegOD import MultiAutoRegOD
from .core.AutoRegOD import AutoRegOD

from sklearn.utils import check_array, column_or_1d
from sklearn.utils.validation import check_is_fitted

from combo.models.score_comb import average, maximization, median, aom, moa
from combo.utils.utility import standardizer
import uuid

Inputs = d3m_dataframe
Outputs = d3m_dataframe
from tods.utils import construct_primitive_metadata

class Params(Params_ODBase):
    ######## Add more Attributes #######

    pass


class Hyperparams(Hyperparams_ODBase):
    ######## Add more Hyperparamters #######

    method = hyperparams.Enumeration[str](
        values=['average', 'maximization', 'median'],
        default='average',
        description='Combination method: {average, maximization, median}. Pass in weights of detector for weighted version.',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter']
    )

    weights = hyperparams.Union(
        configuration=OrderedDict({
            'ndarray': hyperparams.Hyperparameter[ndarray](
                default=np.array([]),
                semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'],
            ),
            'none': hyperparams.Constant(
                default=None,
                semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'],
            )
        }),
        default='none',
        description='Score weight by dimensions. If None, [1,1,...,1] will be used.',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )

    pass


class AutoRegODetectorPrimitive(UnsupervisedOutlierDetectorBase[Inputs, Outputs, Params, Hyperparams]):
    """
    Autoregressive models use linear regression to calculate a sample's
    deviance from the predicted value, which is then used as its
    outlier scores. This model is for multivariate time series.
    This model handles multivariate time series by various combination
    approaches. See AutoRegOD for univarite data.

    See :cite:t:`aggarwal2015outlier` for details.

Parameters
----------
    window_size : int
        The moving window size.
    step_size : int, optional (default=1)
        The displacement for moving window.
    contamination : float in (0., 0.5), optional (default=0.1)
        The amount of contamination of the data set, i.e.
        the proportion of outliers in the data set. When fitting this is used
        to define the threshold on the decision function.
    method : str, optional (default='average')
        Combination method: {'average', 'maximization',
        'median'}. Pass in weights of detector for weighted version.
    weights : numpy array of shape (1, n_dimensions)
        Score weight by dimensions. (default=[1,1,...,1])

.. dropdown:: Attributes

    decision_scores_ : numpy array of shape (n_samples,)
        The outlier scores of the training data.
        The higher, the more abnormal. Outliers tend to have higher
        scores. This value is available once the detector is
        fitted.
    labels_ : int, either 0 or 1
        The binary labels of the training data. 0 stands for inliers
        and 1 for outliers/anomalies. It is generated by applying
        ``threshold_`` on ``decision_scores_``.
    """

    metadata = construct_primitive_metadata(module='detection_algorithm', name='AutoRegODetector', id='AutoRegODetector', primitive_family='anomaly_detect', hyperparams=['window_size', 'contamination', 'step_size', 'method', 'weights'],description='AutoRegODetector')

    def __init__(self, *,
                 hyperparams: Hyperparams, #
                 random_seed: int = 0,
                 docker_containers: Dict[str, DockerContainer] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)

        self._clf = MultiAutoRegOD(window_size=hyperparams['window_size'],
                                    contamination=hyperparams['contamination'],
                                    step_size=hyperparams['step_size'],
                                    method=hyperparams['method'],
                                    weights=hyperparams['weights'],
                                    )

        return

    def set_training_data(self, *, inputs: Inputs) -> None:
        """
        Set training data for outlier detection.
        Args:
            inputs: Container DataFrame
        Returns:
            None
        """
        super().set_training_data(inputs=inputs)

    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        """
        Fit model with training data.
        Args:
            *: Container DataFrame. Time series data up to fit.
        Returns:
            None
        """
        return super().fit()

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        """
        Process the testing data.
        Args:
            inputs: Container DataFrame. Time series data up to outlier detection.
        Returns:
            Container DataFrame
            1 marks Outliers, 0 marks normal.
        """
        return super().produce(inputs=inputs, timeout=timeout, iterations=iterations)

    def produce_score(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        """
        Process the testing data.
        Args:
            inputs: Container DataFrame. Time series data up to outlier detection.
        Returns:
            Container DataFrame
            Outlier score of input DataFrame.
        """
        return super().produce_score(inputs=inputs, timeout=timeout, iterations=iterations)

    def get_params(self) -> Params:
        """
        Return parameters.
        Args:
            None
        Returns:
            class Params
        """
        return super().get_params()

    def set_params(self, *, params: Params) -> None:
        """
        Set parameters for outlier detection.
        Args:
            params: class Params
        Returns:
            None
        """
        super().set_params(params=params)