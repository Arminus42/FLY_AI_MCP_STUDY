import argparse
import ast
import os
import random
import inspect
import sys
import copy
import math
import time

# ==========================================
# 1. Runtime Tracer & Helpers
# ==========================================

class RuntimeTracer:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.path = []
        self.distances = {}
        # 복합 조건 처리를 위해 스택 사용 가능성을 열어두지만, 
        # 여기서는 단순화를 위해 마지막 비교 거리만 저장
        self.last_compare_dist = 0.0

tracer = RuntimeTracer()

def _get_iterable_distance(elem, target, is_in):
    """Calculate distance for 'in' / 'not in' operators"""
    if not target: 
        return 999.0
    
    dists = []
    try:
        for t in target:
            if isinstance(elem, (int, float)) and isinstance(t, (int, float)):
                dists.append(abs(elem - t))
            else:
                dists.append(0.0 if elem == t else 1.0)
    except TypeError:
        return 999.0

    if not dists: return 999.0
    
    # in: 가장 가까운 요소와의 거리
    min_dist = min(dists)
    
    if is_in:
        return float(min_dist)
    else:
        # not in: 포함되어 있으면(거리 0) 페널티(1.0), 아니면 0
        return 1.0 if min_dist == 0 else 0.0

def _sbst_compare(left, op_type, right):
    """Compare and record branch distance."""
    distance = 0.0
    k = 1.0
    result = False

    try:
        if op_type == 'Eq': result = (left == right)
        elif op_type == 'NotEq': result = (left != right)
        elif op_type == 'Lt': result = (left < right)
        elif op_type == 'LtE': result = (left <= right)
        elif op_type == 'Gt': result = (left > right)
        elif op_type == 'GtE': result = (left >= right)
        elif op_type == 'In': result = (left in right)
        elif op_type == 'NotIn': result = (left not in right)
    except Exception:
        tracer.last_compare_dist = 999.0
        return False

    if op_type == 'Eq':
        if result: distance = 0
        else: distance = abs(left - right) + k
    elif op_type == 'NotEq':
        if result: distance = 0
        else: distance = k
    elif op_type == 'Lt': 
        if result: distance = 0
        else: distance = (left - right) + k
    elif op_type == 'LtE':
        if result: distance = 0
        else: distance = (left - right)
    elif op_type == 'Gt': 
        if result: distance = 0
        else: distance = (right - left) + k
    elif op_type == 'GtE': 
        if result: distance = 0
        else: distance = (right - left)
    elif op_type == 'In':
        distance = _get_iterable_distance(left, right, is_in=True)
    elif op_type == 'NotIn':
        distance = _get_iterable_distance(left, right, is_in=False)
    
    tracer.last_compare_dist = float(distance)
    return result

def _sbst_decision(condition_result, branch_id):
    """Record execution path and distances"""
    current_dist = tracer.last_compare_dist
    
    # 비교 연산 없이 온 경우 (예: if flag) 처리
    if current_dist == 0.0 and not condition_result:
        current_dist = 1.0

    if branch_id not in tracer.distances:
        tracer.distances[branch_id] = {}
    
    if condition_result:
        tracer.distances[branch_id][True] = 0.0
        tracer.distances[branch_id][False] = current_dist + 1.0
    else:
        tracer.distances[branch_id][False] = 0.0
        tracer.distances[branch_id][True] = current_dist

    tracer.path.append((branch_id, condition_result))
    tracer.last_compare_dist = 0.0
    return condition_result

# ==========================================
# 2. Instrumenter
# ==========================================

class Instrumenter(ast.NodeTransformer):
    def __init__(self):
        self.branch_count = 0
        self.branch_structure = {} 
        self.branch_stack = []

    def _get_new_id(self):
        bid = self.branch_count
        self.branch_count += 1
        return bid
    
    def _register_branch(self, branch_id):
        parent = self.branch_stack[-1] if self.branch_stack else None
        self.branch_structure[branch_id] = parent
        return branch_id

    def visit_Compare(self, node):
        if len(node.ops) != 1: return node 
        op = node.ops[0]
        op_name = op.__class__.__name__
        return ast.Call(
            func=ast.Name(id='_sbst_compare', ctx=ast.Load()),
            args=[node.left, ast.Constant(value=op_name), node.comparators[0]],
            keywords=[]
        )

    # [Improved] BoolOp 지원 (and, or)
    # Python의 Short-circuit 특성상, BoolOp 자체를 하나의 함수로 감싸기보다
    # 내부 값들이 실행되면서 last_compare_dist를 갱신하도록 두는 것이 자연스러움.
    # 다만, visit_If 등에서 condition을 visit할 때 자식들이 처리됨.
    
    def visit_If(self, node):
        branch_id = self._get_new_id()
        self._register_branch(branch_id)
        node.test = self.visit(node.test)
        node.test = ast.Call(
            func=ast.Name(id='_sbst_decision', ctx=ast.Load()),
            args=[node.test, ast.Constant(value=branch_id)],
            keywords=[]
        )
        self.branch_stack.append(branch_id)
        for child in node.body: self.visit(child)
        for child in node.orelse: self.visit(child)
        self.branch_stack.pop()
        return node

    def visit_While(self, node):
        branch_id = self._get_new_id()
        self._register_branch(branch_id)
        node.test = self.visit(node.test)
        node.test = ast.Call(
            func=ast.Name(id='_sbst_decision', ctx=ast.Load()),
            args=[node.test, ast.Constant(value=branch_id)],
            keywords=[]
        )
        self.branch_stack.append(branch_id)
        for child in node.body: self.visit(child)
        self.branch_stack.pop()
        return node

    def visit_IfExp(self, node):
        branch_id = self._get_new_id()
        self._register_branch(branch_id)
        node.test = self.visit(node.test)
        node.test = ast.Call(
            func=ast.Name(id='_sbst_decision', ctx=ast.Load()),
            args=[node.test, ast.Constant(value=branch_id)],
            keywords=[]
        )
        self.branch_stack.append(branch_id)
        node.body = self.visit(node.body)
        node.orelse = self.visit(node.orelse)
        self.branch_stack.pop()
        return node

    def visit_Match(self, node):
        subject = node.subject
        new_nodes = []
        for case in node.cases:
            pattern = case.pattern
            body = case.body
            test_node = None
            if isinstance(pattern, ast.MatchValue):
                test_node = ast.Compare(left=subject, ops=[ast.Eq()], comparators=[pattern.value])
            elif isinstance(pattern, ast.MatchOr):
                sub_tests = []
                for p in pattern.patterns:
                    if isinstance(p, ast.MatchValue):
                        sub_tests.append(ast.Compare(left=subject, ops=[ast.Eq()], comparators=[p.value]))
                if sub_tests:
                    test_node = ast.BoolOp(op=ast.Or(), values=sub_tests)
            elif isinstance(pattern, ast.MatchAs) and pattern.name is None:
                test_node = ast.Constant(value=True)
            
            if test_node:
                new_nodes.append(ast.If(test=test_node, body=body, orelse=[]))

        if not new_nodes: return ast.Pass()
        
        top_node = new_nodes[0]
        curr_node = top_node
        for next_node in new_nodes[1:]:
            curr_node.orelse = [next_node]
            curr_node = next_node
            
        return self.visit(top_node)

# ==========================================
# 3. Fitness & Search (Tuple-Based)
# ==========================================

def get_approach_level_and_distance(target_branch, target_outcome, structure):
    if (target_branch, target_outcome) in tracer.path:
        return 0, 0.0 

    ancestry = []
    curr = target_branch
    while curr is not None:
        ancestry.append(curr)
        curr = structure.get(curr)
    ancestry.reverse() 
    
    executed_branches = {}
    for bid, res in tracer.path:
        if bid not in executed_branches: executed_branches[bid] = set()
        executed_branches[bid].add(res)
        
    divergence_node = None
    approach_level = 0
    
    for i, node_id in enumerate(ancestry):
        if node_id == target_branch:
            divergence_node = node_id
            approach_level = 0
            break
        if node_id in executed_branches:
            next_node = ancestry[i+1]
            if next_node in executed_branches: continue
            else:
                divergence_node = node_id
                approach_level = len(ancestry) - 1 - i
                break
        else:
            approach_level = len(ancestry)
            break
            
    branch_dist = 999.0
    if divergence_node is not None and divergence_node in tracer.distances:
        desired = not list(executed_branches[divergence_node])[0]
        if divergence_node == target_branch: desired = target_outcome
        branch_dist = tracer.distances[divergence_node].get(desired, 999.0)
        
    return approach_level, branch_dist

def generate_random_inputs(sig):
    args = []
    for param in sig.parameters.values():
        # [Strategy] 넓은 초기 범위 (example5 대응)
        if random.random() < 0.5:
             args.append(random.randint(-100, 100))
        else:
             args.append(random.randint(-2000000, 2000000))
    return args

def mutate(args):
    if not args: return args
    new_args = list(args)
    idx = random.randint(0, len(new_args) - 1)
    
    if isinstance(new_args[idx], int):
        choice = random.random()
        if choice < 0.1: 
            # Random Reset
            new_args[idx] = random.randint(-10000, 10000)
        elif choice < 0.4:
            # [Core Fix] Big Jump for Large Numbers
            new_args[idx] += random.choice([-100000, 100000, -500000, 500000, -1000000, 1000000])
        elif choice < 0.7:
            # Medium Jump
            new_args[idx] += random.choice([-10, 10, -50, 50, -100, 100])
        else:
            # Fine Tuning
            new_args[idx] += random.choice([-1, 1, -5, 5])
            
    return new_args

def run_hill_climbing(target_func, branch_id, outcome, structure, timeout=2.0):
    """
    Time-Based Hill Climbing with Tuple Comparison
    timeout: 타겟당 최대 시간 (기본 2.0초로 상향)
    """
    sig = inspect.signature(target_func)
    start_time = time.time()
    
    current_args = generate_random_inputs(sig)
    tracer.reset()
    try: target_func(*current_args)
    except: pass
    ap, bd = get_approach_level_and_distance(branch_id, outcome, structure)
    
    # [Core Fix] Compare tuples directly: (AL, BD)
    # This prevents gradient vanishing for large BD.
    best_fitness = (ap, bd)
    
    if best_fitness == (0, 0.0): return current_args

    iter_count = 0
    
    while (time.time() - start_time) < timeout:
        iter_count += 1
        
        # Periodic Restart (every 300 iters)
        if iter_count % 300 == 0:
             candidate_args = generate_random_inputs(sig)
        else:
             candidate_args = mutate(current_args)
        
        tracer.reset()
        try: target_func(*candidate_args)
        except: pass
        
        ap, bd = get_approach_level_and_distance(branch_id, outcome, structure)
        fitness = (ap, bd)
        
        # Tuple Comparison (Lexicographical)
        if fitness <= best_fitness:
            best_fitness = fitness
            current_args = candidate_args
            if best_fitness == (0, 0.0): return current_args
            
    return None

# ==========================================
# 4. Main Execution
# ==========================================

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    target_path, save_path = sys.argv[1], sys.argv[2]
    
    with open(target_path, "r") as f: code = f.read()

    tree = ast.parse(code)
    instrumenter = Instrumenter()
    instrumented_tree = instrumenter.visit(tree)
    ast.fix_missing_locations(instrumented_tree)

    exec_globals = {
        '_sbst_compare': _sbst_compare,
        '_sbst_decision': _sbst_decision,
        '__builtins__': __builtins__
    }
    
    compiled_code = compile(instrumented_tree, filename="<string>", mode="exec")
    exec(compiled_code, exec_globals)

    target_functions = [name for name, obj in exec_globals.items() 
                       if inspect.isfunction(obj) and not name.startswith('_sbst')]
    
    generated_tests = []
    
    for func_name in target_functions:
        func_obj = exec_globals[func_name]
        
        target_branches = []
        for bid in instrumenter.branch_structure.keys():
            target_branches.append((bid, True))
            target_branches.append((bid, False))
            
        covered_targets = set()

        # 1. Initial Probe
        tracer.reset()
        try: func_obj(*generate_random_inputs(inspect.signature(func_obj)))
        except: pass
        for p in tracer.path: covered_targets.add(p)

        # 2. Targeted Search
        for (bid, outcome) in target_branches:
            if (bid, outcome) in covered_targets: continue
            
            # Timeout Increased to 2.0s per branch for deeper search
            result_args = run_hill_climbing(func_obj, bid, outcome, instrumenter.branch_structure, timeout=2.0)
            
            if result_args:
                generated_tests.append((func_name, result_args))
                tracer.reset()
                try: func_obj(*result_args)
                except: pass
                for p in tracer.path: covered_targets.add(p)

    unique_tests = []
    seen = set()
    for fname, fargs in generated_tests:
        key = (fname, tuple(fargs))
        if key not in seen:
            seen.add(key)
            unique_tests.append((fname, fargs))

    target_module_name = os.path.basename(target_path).removesuffix(".py")
    test_file_name = os.path.join(save_path, "test_" + os.path.basename(target_path))
    
    with open(test_file_name, 'w') as f:
        f.write("import pytest\n")
        f.write(f"from {target_module_name} import *\n\n")
        for idx, (fname, fargs) in enumerate(unique_tests):
            f.write(f"def test_{fname}_{idx}():\n")
            f.write(f"    {fname}({', '.join(map(str, fargs))})\n\n")