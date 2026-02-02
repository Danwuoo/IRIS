import tqdm
import os
import json
import hashlib

from random import seed as set_seed, Random

import dsl
from dsl import *

import utils
from utils import *

import generators
import verifiers



def get_generators() -> dict:
    """
    returns mapper from task identifiers (keys) to example generator functions
    """
    prefix = 'generate_'
    return {
        strip_prefix(n, prefix): getattr(generators, n) for n in dir(generators) if n.startswith(prefix)
    }


def get_verifiers() -> dict:
    """
    returns mapper from task identifiers (keys) to example verifier functions
    """
    prefix = 'verify_'
    return {
        strip_prefix(n, prefix): getattr(verifiers, n) for n in dir(verifiers) if n.startswith(prefix)
    }


def _hash_config(config: dict) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _apply_color_mapping(grid, mapping):
    return tuple(tuple(mapping[val] for val in row) for row in grid)


def _apply_dihedral(grid, tid: int):
    if tid == 0:
        return grid
    if tid == 1:
        return tuple(tuple(row) for row in zip(*grid[::-1]))
    if tid == 2:
        return tuple(tuple(row[::-1]) for row in grid[::-1])
    if tid == 3:
        return tuple(tuple(row) for row in zip(*grid))[::-1]
    if tid == 4:
        return tuple(tuple(row[::-1]) for row in grid)
    if tid == 5:
        return tuple(tuple(row) for row in grid[::-1])
    if tid == 6:
        return tuple(tuple(row) for row in zip(*grid))
    if tid == 7:
        return tuple(tuple(row[::-1]) for row in zip(*grid[::-1]))
    raise ValueError(f"Invalid dihedral tid: {tid}")


def _choose_transform(rng: Random) -> dict:
    if rng.random() < 0.5:
        mapping = list(range(10))
        while True:
            rng.shuffle(mapping)
            if mapping != list(range(10)):
                break
        return {"type": "color_permutation", "settings": {"mapping": mapping}}
    return {"type": "dihedral", "settings": {"tid": rng.randint(1, 7)}}


def _apply_transform_example(example: dict, transform: dict) -> dict:
    ttype = transform["type"]
    settings = transform["settings"]
    if ttype == "color_permutation":
        mapping = settings["mapping"]
        return {
            "input": _apply_color_mapping(example["input"], mapping),
            "output": _apply_color_mapping(example["output"], mapping),
        }
    if ttype == "dihedral":
        tid = settings["tid"]
        return {
            "input": _apply_dihedral(example["input"], tid),
            "output": _apply_dihedral(example["output"], tid),
        }
    raise ValueError(f"Unknown transform type: {ttype}")


def _generate_examples(generator, verifier, n_examples: int, diff_lb: float, diff_ub: float) -> list:
    examples = []
    seen = set()
    attempts = 0
    while len(examples) < n_examples and attempts < n_examples * 50:
        attempts += 1
        example, identifier, success = None, None, True
        try:
            example = generator(diff_lb, diff_ub)
            assert is_grid(example['input'])
            assert is_grid(example['output'])
            identifier = hash(example['input'])
        except:
            success = False
        try:
            assert success and verifier(example['input']) == example['output']
        except:
            success = False
        try:
            assert success and example['input'] != example['output']
        except:
            success = False
        if success and identifier not in seen:
            examples.append(example)
            seen.add(identifier)
    if len(examples) < n_examples:
        raise RuntimeError(f"Failed to generate {n_examples} examples.")
    return examples


def get_rng_difficulty(
    example: dict
) -> float:
    """
    RNG-Difficulty: proxy measure for example difficulty, defined as the mean of sampled floats within example generation
    """
    rng = getattr(utils, 'rng')
    setattr(utils, 'rng', [])
    return sum(rng) / len(rng)


def get_pso_difficulty(
    example: dict
) -> float:
    """
    PSO-Difficulty: proxy measure for example difficulty, defined as weighted sum of #Pixels, #Symbols, #Objects
    """
    i, o = example['input'], example['output']
    hwi = height(i) * width(i)
    hwo = height(o) * width(o)
    pix_pct = (hwi + hwo) / 1800
    col_pct = len(palette(i) | palette(o)) / 10
    obj_dens = (len(objects(i, T, F, F)) / hwi + len(objects(o, T, F, F)) / hwo) / 2
    return (pix_pct + col_pct + obj_dens) / 3


def demo_generator(key, n=6):
    with open(f'arc_original/training/{key}.json', 'r') as fp:
        original_task = json.load(fp)
    original_task = original_task['train'] + original_task['test']
    generator = getattr(generators, f'generate_{key}')
    generated_examples = [generator(0, 1) for k in range(n)]
    plot_task(original_task)
    plot_task(generated_examples)
    

def generate_dataset(
    path: str | None = None,
    seed: int = 42,
    n_examples: int = 1000,
    pairs_per_task: int = 4,
    diff_lb: float = 0,
    diff_ub: float = 1
) -> None:
    """
    generates paired-task dataset

    path: which folder to save pairs to
    seed: for deterministic generation / reproducibility
    n_examples: number of examples per task
    pairs_per_task: number of pairs per generator key
    diff_lb: lower bound for difficulty
    diff_ub: upper bound for difficulty
    """
    set_seed(seed)
    rng = Random(seed)
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'pairs')
    os.makedirs(path, exist_ok=True)
    generators_mapper = get_generators()
    verifiers_mapper = get_verifiers()
    keys = sorted(generators_mapper.keys())
    k = len(keys)
    desc = f'task 0/{k}, pair 0/{pairs_per_task}'
    pbar = tqdm.tqdm(enumerate(keys), desc=desc, position=0, leave=True, total=k)
    for i, key in pbar:
        generator = generators_mapper[key]
        verifier = verifiers_mapper[key]
        for pair_idx in range(pairs_per_task):
            examples = _generate_examples(generator, verifier, n_examples, diff_lb, diff_ub)
            transform = _choose_transform(rng)
            transformed = [_apply_transform_example(ex, transform) for ex in examples]
            config = {
                "source_task": key,
                "diff_lb": diff_lb,
                "diff_ub": diff_ub,
                "n_examples": n_examples,
                "seed": seed,
                "pair_index": pair_idx,
                "transform": transform,
            }
            config_hash = _hash_config(config)
            pair_id = f"{key}_{transform['type']}_{pair_idx:04d}_{config_hash[:8]}"
            pair_dir = os.path.join(path, pair_id)
            os.makedirs(pair_dir, exist_ok=True)
            with open(os.path.join(pair_dir, "task_A.json"), 'w') as fp:
                json.dump(examples, fp)
            with open(os.path.join(pair_dir, "task_B.json"), 'w') as fp:
                json.dump(transformed, fp)
            changed_factor = transform["type"]
            meta = {
                "invariant_type": "representation_invariant",
                "changed_factor": changed_factor,
                "generator_config_hash": config_hash,
                "source_task": key,
                "pair_index": pair_idx,
                "transform": transform,
            }
            with open(os.path.join(pair_dir, "pair_meta.json"), 'w') as fp:
                json.dump(meta, fp)
            desc = f'task {i+1}/{k}, pair {pair_idx+1}/{pairs_per_task}'
            pbar.set_description(desc)


def demo_dataset(
    folder: str | None = None,
    n: int = 6,
    s: int = 0,
    e: int = 20
) -> None:
    """
    visualizing snippets from a paired dataset
    """
    if folder is None:
        folder = os.path.join(os.path.dirname(__file__), 'pairs')
    pair_dirs = sorted(os.listdir(folder))
    for i, pair_id in enumerate(pair_dirs):
        if s <= i < e:
            pair_dir = os.path.join(folder, pair_id)
            with open(os.path.join(pair_dir, "task_A.json"), "r") as fp:
                task_a = json.load(fp)
            with open(os.path.join(pair_dir, "task_B.json"), "r") as fp:
                task_b = json.load(fp)
            print(pair_id)
            print('task_A:')
            plot_task(task_a[:n])
            print('task_B:')
            plot_task(task_b[:n])


def evaluate_verifiers_on_original_tasks() -> None:
    """
    runs the verifiers on the original ARC training tasks
    """
    verifiers = get_verifiers()
    dataset = dict()
    for key in verifiers.keys():
        with open(f'arc_original/training/{key}.json', 'r') as fp:
            task = json.load(fp)
        dataset[key] = format_task(task)
    fix_bugs(dataset)
    failed_on = set()
    for key, verifier in verifiers.items():
        task = dataset[key]
        try:
            for example in task['train'] + task['test']:
                assert verifier(example['input']) == example['output']
        except:
            failed_on.add(key)
    n = len(dataset)
    k = len(failed_on)
    print(f'verification programs work for all examples for {n-k}/{n} tasks')
    print(f'verification fails (on one example) for tasks {failed_on}')
