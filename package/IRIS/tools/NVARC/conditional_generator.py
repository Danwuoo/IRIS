import argparse
import hashlib
import json
import os
import random
from pathlib import Path


VALID_TAXONOMY_CODES = {"F_REP", "F_PROC", "F_SEARCH", "F_MEM", "F_ABS", "F_EVAL"}


def _load_failure_tags(config_path: Path) -> dict:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    tags = data.get("tags", [])
    tag_index = {}
    for entry in tags:
        tag = entry.get("tag")
        code = entry.get("taxonomy_code")
        if not tag or code not in VALID_TAXONOMY_CODES:
            raise ValueError(f"Invalid failure tag entry: {entry}")
        if tag in tag_index:
            raise ValueError(f"Duplicate failure tag: {tag}")
        tag_index[tag] = entry
    if not tag_index:
        raise ValueError("No failure tags found in config.")
    return {"version": data.get("version", "unknown"), "tags": tag_index}


def _hash_config(config: dict) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _clamp_intensity(intensity: float) -> float:
    return max(0.0, min(1.0, float(intensity)))


def _make_grid(h: int, w: int, fill: int) -> list[list[int]]:
    return [[fill for _ in range(w)] for _ in range(h)]


def _copy_grid(grid: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in grid]


def _place_rect(grid: list[list[int]], top: int, left: int, height: int, width: int, color: int) -> None:
    for r in range(top, top + height):
        for c in range(left, left + width):
            grid[r][c] = color


def _place_dot(grid: list[list[int]], row: int, col: int, color: int) -> None:
    grid[row][col] = color


def _rand_color(rng: random.Random, exclude: set[int]) -> int:
    choices = [c for c in range(10) if c not in exclude]
    return rng.choice(choices)


def _sample_noise(
    rng: random.Random,
    occupied: set[tuple[int, int]],
    count: int,
    h: int,
    w: int,
    palette: list[int],
) -> list[tuple[int, int, int]]:
    noise = []
    attempts = 0
    while len(noise) < count and attempts < 200:
        attempts += 1
        r = rng.randrange(0, h)
        c = rng.randrange(0, w)
        if (r, c) in occupied:
            continue
        noise.append((r, c, rng.choice(palette)))
        occupied.add((r, c))
    return noise


def _apply_noise(grid: list[list[int]], noise: list[tuple[int, int, int]]) -> None:
    for r, c, color in noise:
        grid[r][c] = color


def _gen_obj_split_merge(rng: random.Random, intensity: float) -> dict:
    h = rng.randint(8, 14)
    w = rng.randint(8, 14)
    bg = rng.randint(0, 9)
    fg = _rand_color(rng, {bg})
    grid = _make_grid(h, w, bg)
    horizontal = rng.choice([True, False])
    if horizontal:
        rect_h = rng.randint(2, min(4, h - 2))
        rect_w = rng.randint(2, min(4, (w - 3) // 2))
        top = rng.randint(0, h - rect_h)
        left = rng.randint(0, w - (2 * rect_w + 1))
        _place_rect(grid, top, left, rect_h, rect_w, fg)
        _place_rect(grid, top, left + rect_w + 1, rect_h, rect_w, fg)
        gap_col = left + rect_w
        output = _copy_grid(grid)
        for r in range(top, top + rect_h):
            output[r][gap_col] = fg
        occupied = {(r, c) for r in range(top, top + rect_h) for c in range(left, left + 2 * rect_w + 1)}
    else:
        rect_h = rng.randint(2, min(4, (h - 3) // 2))
        rect_w = rng.randint(2, min(4, w - 2))
        top = rng.randint(0, h - (2 * rect_h + 1))
        left = rng.randint(0, w - rect_w)
        _place_rect(grid, top, left, rect_h, rect_w, fg)
        _place_rect(grid, top + rect_h + 1, left, rect_h, rect_w, fg)
        gap_row = top + rect_h
        output = _copy_grid(grid)
        for c in range(left, left + rect_w):
            output[gap_row][c] = fg
        occupied = {(r, c) for r in range(top, top + 2 * rect_h + 1) for c in range(left, left + rect_w)}
    noise_count = int(1 + intensity * 3)
    palette = [c for c in range(10) if c not in (bg, fg)]
    noise = _sample_noise(rng, set(occupied), noise_count, h, w, palette)
    _apply_noise(grid, noise)
    _apply_noise(output, noise)
    return {"input": grid, "output": output}


def _gen_relation_overfit(rng: random.Random, intensity: float) -> dict:
    h = rng.randint(8, 14)
    w = rng.randint(8, 14)
    bg = rng.randint(0, 9)
    fg = _rand_color(rng, {bg})
    dg = _rand_color(rng, {bg, fg})
    grid = _make_grid(h, w, bg)
    row = rng.randint(1, h - 2)
    col1 = rng.randint(0, w - 4)
    col2 = col1 + rng.randint(2, min(5, w - col1 - 1))
    _place_dot(grid, row, col1, fg)
    _place_dot(grid, row, col2, fg)
    col = rng.randint(1, w - 2)
    row1 = rng.randint(0, h - 4)
    row2 = row1 + rng.randint(2, min(5, h - row1 - 1))
    _place_dot(grid, row1, col, dg)
    _place_dot(grid, row2, col, dg)
    output = _copy_grid(grid)
    for c in range(min(col1, col2), max(col1, col2) + 1):
        output[row][c] = fg
    noise_count = int(intensity * 2)
    palette = [c for c in range(10) if c not in (bg, fg, dg)]
    line_cells = {(row, c) for c in range(min(col1, col2), max(col1, col2) + 1)}
    occupied = {(row, col1), (row, col2), (row1, col), (row2, col)} | line_cells
    noise = _sample_noise(rng, set(occupied), noise_count, h, w, palette)
    _apply_noise(grid, noise)
    _apply_noise(output, noise)
    return {"input": grid, "output": output}


def _rotate90(grid: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*grid[::-1])]


def _gen_procedure_misorder(rng: random.Random, intensity: float) -> dict:
    h = rng.randint(9, 14)
    w = rng.randint(9, 14)
    bg = rng.randint(0, 9)
    fg = _rand_color(rng, {bg})
    marker = _rand_color(rng, {bg, fg})
    border = _rand_color(rng, {bg, fg, marker})
    grid = _make_grid(h, w, bg)
    obj_h = rng.randint(2, 4)
    obj_w = rng.randint(3, 5)
    if obj_h == obj_w:
        obj_w += 1
    top = rng.randint(0, h - obj_h)
    left = rng.randint(0, w - obj_w)
    _place_rect(grid, top, left, obj_h, obj_w, fg)
    rot_obj = _rotate90(_make_grid(obj_h, obj_w, fg))
    rh = len(rot_obj)
    rw = len(rot_obj[0])
    max_r = h - rh - 1
    max_c = w - rw - 1
    mark_r = rng.randint(0, max(0, max_r))
    mark_c = rng.randint(0, max(0, max_c))
    _place_dot(grid, mark_r, mark_c, marker)
    output = _make_grid(h, w, bg)
    for r in range(rh):
        for c in range(rw):
            output[mark_r + r][mark_c + c] = fg
    for r in range(max(0, mark_r - 1), min(h, mark_r + rh + 1)):
        for c in range(max(0, mark_c - 1), min(w, mark_c + rw + 1)):
            if output[r][c] == bg:
                output[r][c] = border
    noise_count = int(intensity * 2)
    palette = [c for c in range(10) if c not in (bg, fg, marker, border)]
    occupied_in = {(top + r, left + c) for r in range(obj_h) for c in range(obj_w)}
    occupied_in.add((mark_r, mark_c))
    occupied_out = {(mark_r + r, mark_c + c) for r in range(rh) for c in range(rw)}
    border_cells = {(r, c) for r in range(max(0, mark_r - 1), min(h, mark_r + rh + 1)) for c in range(max(0, mark_c - 1), min(w, mark_c + rw + 1))}
    occupied = occupied_in | occupied_out | border_cells
    noise = _sample_noise(rng, set(occupied), noise_count, h, w, palette)
    _apply_noise(grid, noise)
    _apply_noise(output, noise)
    return {"input": grid, "output": output}


def _gen_premature_abstraction(rng: random.Random, intensity: float) -> dict:
    h = rng.randint(9, 14)
    w = rng.randint(9, 14)
    bg = rng.randint(0, 9)
    fg = _rand_color(rng, {bg})
    marker = _rand_color(rng, {bg, fg})
    newc = _rand_color(rng, {bg, fg, marker})
    grid = _make_grid(h, w, bg)
    num_objs = 3 + int(intensity * 2)
    obj_h = rng.randint(2, 3)
    obj_w = rng.randint(2, 3)
    occupied = set()
    objs = []
    attempts = 0
    while len(objs) < num_objs and attempts < 200:
        attempts += 1
        top = rng.randint(0, h - obj_h)
        left = rng.randint(0, w - obj_w)
        cells = {(r, c) for r in range(top, top + obj_h) for c in range(left, left + obj_w)}
        if cells & occupied:
            continue
        _place_rect(grid, top, left, obj_h, obj_w, fg)
        occupied |= cells
        objs.append((top, left))
    special = rng.choice(objs)
    mark_r = special[0] + rng.randint(0, obj_h - 1)
    mark_c = special[1] + rng.randint(0, obj_w - 1)
    _place_dot(grid, mark_r, mark_c, marker)
    output = _copy_grid(grid)
    for top, left in objs:
        is_special = top == special[0] and left == special[1]
        color = fg if is_special else newc
        for r in range(top, top + obj_h):
            for c in range(left, left + obj_w):
                output[r][c] = color
    output[mark_r][mark_c] = fg
    return {"input": grid, "output": output}


def _generate_example(failure_tag: str, rng: random.Random, intensity: float) -> dict:
    if failure_tag == "obj_split_merge":
        return _gen_obj_split_merge(rng, intensity)
    if failure_tag == "relation_overfit":
        return _gen_relation_overfit(rng, intensity)
    if failure_tag == "procedure_misorder":
        return _gen_procedure_misorder(rng, intensity)
    if failure_tag == "premature_abstraction":
        return _gen_premature_abstraction(rng, intensity)
    raise ValueError(f"Unsupported failure_tag: {failure_tag}")


def _generate_task(
    failure_tag: str,
    intensity: float,
    rng: random.Random,
    num_train: int,
    num_test: int,
) -> dict:
    train = [_generate_example(failure_tag, rng, intensity) for _ in range(num_train)]
    test = [_generate_example(failure_tag, rng, intensity) for _ in range(num_test)]
    return {"train": train, "test": test}


def generate(
    failure_tag: str,
    intensity: float,
    seed: int | None = None,
    num_tasks: int = 8,
    num_train: int = 3,
    num_test: int = 1,
    output_root: str | None = None,
    config_path: str | None = None,
) -> list[dict]:
    intensity = _clamp_intensity(intensity)
    base_path = Path(__file__).resolve().parent
    cfg_path = Path(config_path) if config_path else base_path / "configs" / "failure_tags.yml"
    tag_spec = _load_failure_tags(cfg_path)
    if failure_tag not in tag_spec["tags"]:
        raise ValueError(f"Unknown failure_tag: {failure_tag}")
    tag_entry = tag_spec["tags"][failure_tag]
    config_blob = {
        "generator": "conditional_generator_v1",
        "failure_tag": failure_tag,
        "intensity": intensity,
        "num_train": num_train,
        "num_test": num_test,
        "tag_spec": tag_entry,
        "tag_spec_version": tag_spec["version"],
    }
    config_hash = _hash_config(config_blob)
    rng = random.Random(seed)
    tasks = []
    metadata = []
    for i in range(num_tasks):
        task_seed = rng.randint(0, 2**31 - 1)
        task_rng = random.Random(task_seed)
        task = _generate_task(failure_tag, intensity, task_rng, num_train, num_test)
        tasks.append(task)
        metadata.append(
            {
                "task_file": f"task_{i:04d}.json",
                "failure_tag": failure_tag,
                "generator_config_hash": config_hash,
                "seed": task_seed,
                "intensity": intensity,
            }
        )
    if output_root:
        out_root = Path(output_root)
    else:
        out_root = base_path / "output"
    out_dir = out_root / failure_tag
    os.makedirs(out_dir, exist_ok=True)
    for idx, task in enumerate(tasks):
        with open(out_dir / f"task_{idx:04d}.json", "w", encoding="utf-8") as f:
            json.dump(task, f)
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    return tasks


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NVARC conditional generator.")
    parser.add_argument("--failure-tag", required=True)
    parser.add_argument("--intensity", required=True, type=float)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--num-tasks", type=int, default=8)
    parser.add_argument("--num-train", type=int, default=3)
    parser.add_argument("--num-test", type=int, default=1)
    parser.add_argument("--output-root", type=str, default=None)
    parser.add_argument("--config", type=str, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    generate(
        failure_tag=args.failure_tag,
        intensity=args.intensity,
        seed=args.seed,
        num_tasks=args.num_tasks,
        num_train=args.num_train,
        num_test=args.num_test,
        output_root=args.output_root,
        config_path=args.config,
    )
