import argparse
import ast
import os
import random
import inspect
import sys
import copy

class RuntimeTracer:
    def __init__(self):
        self.branch_distances = {}
    
    def reset(self):
        self.branch_distances = {}

    def update_distance(self, branch_id, distance):
        if branch_id not in self.branch_distances:
            self.branch_distances[branch_id] = distance
        else:
            self.branch_distances[branch_id] = min(self.branch_distances[branch_id], distance)
            
    def get_distance(self, branch_id):
        return self.branch_distances.get(branch_id, float('inf'))
    
tracer = RuntimeTracer()

def evaluate_condition(left, op_type, right, branch_id):
    """
    계측된 코드에서 호출되는 함수.
    실제 비교를 수행하고, Branch Distance를 계산하여 트레이서에 기록함.
    """
    distance = 0.0
    k = 1.0 
    result = False
    if op_type == 'Eq': result = (left == right)
    elif op_type == 'NotEq': result = (left != right)
    elif op_type == 'Lt': result = (left < right)
    elif op_type == 'LtE': result = (left <= right)
    elif op_type == 'Gt': result = (left > right)
    elif op_type == 'GtE': result = (left >= right)

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

    tracer.update_distance(branch_id, distance)
    
    return result


class Instrumenter(ast.NodeTransformer):
    def __init__(self):
        self.branch_count = 0
        self.branches = [] 

    def visit_Compare(self, node):
        """
        비교 연산자 (x > y 등)를 evaluate_condition(x, 'Gt', y, id) 형태로 변환
        """
        if len(node.ops) != 1:
            return node 
        
        op = node.ops[0]
        op_name = op.__class__.__name__
        
    
        branch_id = self.branch_count
        self.branch_count += 1
        self.branches.append(branch_id)

        
        return ast.Call(
            func=ast.Name(id='_sbst_eval', ctx=ast.Load()),
            args=[
                node.left,
                ast.Constant(value=op_name),
                node.comparators[0],
                ast.Constant(value=branch_id)
            ],
            keywords=[]
        )



def generate_random_inputs(sig):
    """함수 시그니처를 보고 랜덤 정수 입력 생성"""
    args = []
    for param in sig.parameters.values():
        if param.annotation == int:
            args.append(random.randint(-100, 100))
        elif param.annotation == float:
            args.append(random.uniform(-100, 100))
    return args

def mutate(args):
    """입력값 중 하나를 랜덤하게 약간 변경"""
    new_args = list(args)
    idx = random.randint(0, len(new_args) - 1)
    change = random.choice([-1, 1, -5, 5, -10, 10])
    new_args[idx] += change
    return new_args

def run_hill_climbing(target_func, branch_id, seeds=[], max_iter=10000):
    sig = inspect.signature(target_func)
    
    # 1. 후보군 생성: (완전 랜덤 값) + (이전에 성공했던 값들)
    candidates = [generate_random_inputs(sig)] + seeds
    
    current_args = None
    best_dist = float('inf')

    # 2. 후보군 중 가장 유망한(거리가 짧은) 시작점 찾기
    for args in candidates:
        tracer.reset()
        try:
            target_func(*args)
        except: pass
        
        dist = tracer.get_distance(branch_id)
        
        # 만약 이전에 성공했던 값을 넣었더니 바로 통과(거리 0)되면 즉시 반환
        if dist == 0:
            return args
            
        # 거리가 더 짧은(유망한) 값을 시작점으로 선택
        if dist < best_dist:
            best_dist = dist
            current_args = args

    # 만약 모든 후보가 진입조차 못했다면(inf), 그냥 랜덤값으로 진행
    if current_args is None:
        current_args = generate_random_inputs(sig)

    # 3. 선택된 시작점에서 힐 클라이밍 시작
    # (여기서부터는 기존 로직과 동일하지만, start point가 훨씬 좋습니다)
    if best_dist == 0:
        return current_args

    for _ in range(max_iter):
        candidate_args = mutate(current_args)
        
        tracer.reset()
        try:
            target_func(*candidate_args)
        except: pass 
        
        candidate_dist = tracer.get_distance(branch_id)
        
        if candidate_dist < best_dist:
            best_dist = candidate_dist
            current_args = candidate_args
            if best_dist == 0:
                return current_args
                
    return None 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="the target python file to generate unit tests for")
    args = parser.parse_args()

    target_path = args.target
    if not os.path.exists(target_path):
        print(f"Error: File {target_path} not found.")
        sys.exit(1)

    with open(target_path, "r") as f:
        code = f.read()

    tree = ast.parse(code)
    instrumenter = Instrumenter()
    instrumented_tree = instrumenter.visit(tree)
    ast.fix_missing_locations(instrumented_tree)

    exec_globals = {
        '_sbst_eval': evaluate_condition,
        '__builtins__': __builtins__
    }
    
   
    compiled_code = compile(instrumented_tree, filename="<string>", mode="exec")
    exec(compiled_code, exec_globals)

    
    target_functions = []
    for name, obj in exec_globals.items():
        if inspect.isfunction(obj) and name != '_sbst_eval':
             
             target_functions.append(name)

    print(f"Instrumented {len(instrumenter.branches)} branches.")
    print(f"Target functions found: {target_functions}")

    generated_tests = []
    population = {fname: [] for fname in target_functions}
    
    for func_name in target_functions:
        func_obj = exec_globals[func_name]
        
        
        for branch_id in instrumenter.branches:

            result_args = run_hill_climbing(func_obj, branch_id, seeds=population[func_name])
            if result_args:
                generated_tests.append((func_name, result_args))
                if result_args not in population[func_name]:
                    population[func_name].append(result_args)
            

    unique_tests = []
    seen = set()
    for fname, fargs in generated_tests:
        key = (fname, tuple(fargs))
        if key not in seen:
            seen.add(key)
            unique_tests.append((fname, fargs))


    target_module_name = os.path.basename(target_path).removesuffix(".py")
    test_file_name = os.path.join(os.path.dirname(target_path), "test_" + os.path.basename(target_path))
    
    with open(test_file_name, 'w') as f:
        f.write("import pytest\n")
 
        f.write(f"from {target_module_name} import *\n\n")

        for idx, (fname, fargs) in enumerate(unique_tests):
            f.write(f"def test_{fname}_{idx}():\n")
            args_str = ", ".join(map(str, fargs))
            f.write(f"    {fname}({args_str})\n\n")

    print(f"Test suite generated in {test_file_name} with {len(unique_tests)} test cases.")