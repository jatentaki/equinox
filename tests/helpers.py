import functools as ft
import operator

import jax.numpy as jnp
import jax.random as jr
import jax.tree_util as jtu
import numpy as np


def random_pytree(key, treedef):
    keys = jr.split(key, treedef.num_leaves)
    leaves = []
    for key in keys:
        dimkey, sizekey, valuekey = jr.split(key, 3)
        num_dims = jr.randint(dimkey, (), 0, 5)
        dim_sizes = jr.randint(sizekey, (num_dims,), 0, 5)
        value = jr.normal(valuekey, dim_sizes)
        leaves.append(value)
    return jtu.tree_unflatten(treedef, leaves)


treedefs = [
    jtu.tree_structure(x)
    for x in (
        0,
        None,
        {"a": [0, 0], "b": 0},
    )
]


def _shaped_allclose(x, y, **kwargs):
    if type(x) is not type(y):
        return False
    if isinstance(x, jnp.ndarray):
        if jnp.issubdtype(x.dtype, jnp.inexact):
            return (
                x.shape == y.shape
                and x.dtype == y.dtype
                and jnp.allclose(x, y, **kwargs)
            )
        else:
            return x.shape == y.shape and x.dtype == y.dtype and jnp.all(x == y)
    elif isinstance(x, np.ndarray):
        if np.issubdtype(x.dtype, np.inexact):
            return (
                x.shape == y.shape
                and x.dtype == y.dtype
                and np.allclose(x, y, **kwargs)
            )
        else:
            return x.shape == y.shape and x.dtype == y.dtype and np.all(x == y)
    else:
        return x == y


def shaped_allclose(x, y, **kwargs):
    """As `jnp.allclose`, except:
    - It also supports PyTree arguments.
    - It mandates that shapes match as well (no broadcasting)
    """
    same_structure = jtu.tree_structure(x) == jtu.tree_structure(y)
    allclose = ft.partial(_shaped_allclose, **kwargs)
    return same_structure and jtu.tree_reduce(
        operator.and_, jtu.tree_map(allclose, x, y), True
    )
