from typing import Dict, List, Callable, Tuple
from itertools import product
from concurrent.futures import ProcessPoolExecutor
from random import random, choice
from time import perf_counter
from multiprocessing import get_context
from multiprocessing.context import BaseContext
from _collections_abc import dict_keys, dict_values, Iterable

from tqdm import tqdm
from deap import creator, base, tools, algorithms


OUTPUT_FUNC = Callable[[str], None]
EVALUATE_FUNC = Callable[[dict], dict]
KEY_FUNC = Callable[[list], float]


# Create individual class used in genetic algorithm optimization
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


class OptimizationSetting:
    """
    Setting for runnning optimization.
    """

    def __init__(self) -> None:
        """"""
        self.params: Dict[str, List] = {}
        self.target_name: str = ""

    def add_parameter(
        self,
        name: str,
        start: float,
        end: float = None,
        step: float = None
    ) -> Tuple[bool, str]:
        """"""
        if end is None and step is None:
            self.params[name] = [start]
            return True, "Fixed parameter added."

        if start >= end:
            return False, "Start value must be lower than end value."

        if step <= 0:
            return False, "Step must be higher than 0."

        value: float = start
        value_list: List[float] = []

        while value <= end:
            value_list.append(value)
            value += step

        self.params[name] = value_list

        return True, f"Range parameter added, total count {len(value_list)}."

    def set_target(self, target_name: str) -> None:
        """"""
        self.target_name = target_name

    def generate_settings(self) -> List[dict]:
        """"""
        keys: dict_keys = self.params.keys()
        values: dict_values = self.params.values()
        products: list = list(product(*values))

        settings: list = []
        for p in products:
            setting: dict = dict(zip(keys, p))
            settings.append(setting)

        return settings


def check_optimization_setting(
    optimization_setting: OptimizationSetting,
    output: OUTPUT_FUNC = print
) -> bool:
    """"""
    if not optimization_setting.generate_settings():
        output("The optimization space is empty, please check the setting.")
        return False

    if not optimization_setting.target_name:
        output("The optimization target is not set, please check the setting.")
        return False

    return True


def run_bf_optimization(
    evaluate_func: EVALUATE_FUNC,
    optimization_setting: OptimizationSetting,
    key_func: KEY_FUNC,
    max_workers: int = None,
    output: OUTPUT_FUNC = print
) -> List[Tuple]:
    """Run brutal force optimization"""
    settings: List[Dict] = optimization_setting.generate_settings()

    output("Brute-force optimization started.")
    output(f"Total space conut: {len(settings)}")

    start: int = perf_counter()

    with ProcessPoolExecutor(
        max_workers,
        mp_context=get_context("spawn")
    ) as executor:
        it: Iterable = tqdm(
            executor.map(evaluate_func, settings),
            total=len(settings)
        )
        results: List[Tuple] = list(it)
        results.sort(reverse=True, key=key_func)

        end: int = perf_counter()
        cost: int = int((end - start))
        output(f"Brute-force optimization finished, time cost: {cost}s.")

        return results


def run_ga_optimization(
    evaluate_func: EVALUATE_FUNC,
    optimization_setting: OptimizationSetting,
    key_func: KEY_FUNC,
    max_workers: int = None,
    population_size: int = 100,
    ngen_size: int = 30,
    output: OUTPUT_FUNC = print
) -> List[Tuple]:
    """Run genetic algorithm optimization"""
    # Define functions for generate parameter randomly
    buf: List[Dict] = optimization_setting.generate_settings()
    settings: List[Tuple] = [list(d.items()) for d in buf]

    def generate_parameter() -> list:
        """"""
        return choice(settings)

    def mutate_individual(individual: list, indpb: float) -> tuple:
        """"""
        size: int = len(individual)
        paramlist: list = generate_parameter()
        for i in range(size):
            if random() < indpb:
                individual[i] = paramlist[i]
        return individual,

    # Set up multiprocessing Pool and Manager
    ctx: BaseContext = get_context("spawn")
    with ctx.Manager() as manager, ctx.Pool(max_workers) as pool:
        # Create shared dict for result cache
        cache: Dict[Tuple, Tuple] = manager.dict()

        # Set up toolbox
        toolbox: base.Toolbox = base.Toolbox()
        toolbox.register("individual", tools.initIterate, creator.Individual, generate_parameter)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", mutate_individual, indpb=1)
        toolbox.register("select", tools.selNSGA2)
        toolbox.register("map", pool.map)
        toolbox.register(
            "evaluate",
            ga_evaluate,
            cache,
            evaluate_func,
            key_func
        )

        total_size: int = len(settings)
        pop_size: int = population_size                      # number of individuals in each generation
        lambda_: int = pop_size                              # number of children to produce at each generation
        mu: int = int(pop_size * 0.8)                        # number of individuals to select for the next generation

        cxpb: float = 0.95          # probability that an offspring is produced by crossover
        mutpb: float = 1 - cxpb     # probability that an offspring is produced by mutation
        ngen: int = ngen_size       # number of generation

        pop: list = toolbox.population(pop_size)

        # Run ga optimization
        output("Genetic-algorithm optimization started.")
        output(f"Total space: {total_size}")
        output(f"Population size: {pop_size}")
        output(f"Selection size: {mu}")
        output(f"Generation limit: {ngen}")
        output(f"Crossover probability: {cxpb:.0%}")
        output(f"Mutation probability: {mutpb:.0%}")

        start: int = perf_counter()

        algorithms.eaMuPlusLambda(
            pop,
            toolbox,
            mu,
            lambda_,
            cxpb,
            mutpb,
            ngen,
            verbose=True
        )

        end: int = perf_counter()
        cost: int = int((end - start))

        output(f"Genetic-algorithm optimization finished, time cost: {cost}s.")

        results: list = list(cache.values())
        results.sort(reverse=True, key=key_func)
        return results


def ga_evaluate(
    cache: dict,
    evaluate_func: callable,
    key_func: callable,
    parameters: list
) -> float:
    """
    Functions to be run in genetic algorithm optimization.
    """
    tp: tuple = tuple(parameters)
    if tp in cache:
        result: tuple = cache[tp]
    else:
        setting: dict = dict(parameters)
        result: dict = evaluate_func(setting)
        cache[tp] = result

    value: float = key_func(result)
    return (value, )
