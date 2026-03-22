import ast
from typing import Dict, List, Optional
import difflib
import re

class CodeScanner:
    def __init__(self):
        self.code_smells = {
            'long_method': {'threshold': 50},  # lines
            'complex_condition': {'threshold': 3},  # logical operators
            'duplicate_code': {'threshold': 0.8}  # similarity ratio
        }

    def analyze_diff(self, old_code: str, new_code: str) -> Dict:
        """Analyzes git diff and detects potential issues"""
        results = {
            'smells': [],
            'risk_score': 0,
            'suggestions': []
        }

        # Parse both versions
        try:
            old_ast = ast.parse(old_code)
            new_ast = ast.parse(new_code)
        except SyntaxError:
            results['smells'].append('Syntax error in code')
            return results

        # Check for code smells
        self._check_method_length(new_ast, results)
        self._check_complexity(new_ast, results)
        self._check_duplication(old_code, new_code, results)

        # Calculate risk score
        results['risk_score'] = len(results['smells']) * 10
        
        return results

    def _check_method_length(self, tree: ast.AST, results: Dict) -> None:
        """Detects long methods"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_lineno = getattr(node, 'end_lineno', node.lineno + len(node.body))
                method_length = end_lineno - node.lineno
                
                if method_length > self.code_smells['long_method']['threshold']:
                    results['smells'].append(f'Long method: {node.name} ({method_length} lines)')
                    results['suggestions'].append(f'Consider breaking {node.name} into smaller functions')

    def _check_complexity(self, tree: ast.AST, results: Dict) -> None:
        """Detects complex conditional statements"""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                operators = len([x for x in ast.walk(node.test) 
                               if isinstance(x, (ast.And, ast.Or))])
                
                if operators >= self.code_smells['complex_condition']['threshold']:
                    results['smells'].append(f'Complex condition found ({operators + 1} conditions)')
                    results['suggestions'].append('Consider simplifying complex conditions into smaller checks')

    def _check_duplication(self, old_code: str, new_code: str, results: Dict) -> None:
        """Detects potential code duplication"""
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()

        matcher = difflib.SequenceMatcher(None)
        
        # Check for duplicates in blocks of 5 lines
        for i in range(len(new_lines) - 4):
            block = '\n'.join(new_lines[i:i+5])
            
            for j in range(i + 5, len(new_lines) - 4):
                compare_block = '\n'.join(new_lines[j:j+5])
                matcher.set_seqs(block, compare_block)
                
                if matcher.ratio() > self.code_smells['duplicate_code']['threshold']:
                    results['smells'].append(f'Possible code duplication found at lines {i+1} and {j+1}')
                    results['suggestions'].append('Consider extracting duplicate code into a shared function')

    def get_diff_stats(self, old_code: str, new_code: str) -> Dict:
        """Returns statistical information about the diff"""
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()
        
        diff = difflib.unified_diff(old_lines, new_lines)
        additions = len([l for l in diff if l.startswith('+')])
        deletions = len([l for l in diff if l.startswith('-')])
        
        return {
            'lines_added': additions,
            'lines_removed': deletions,
            'net_change': additions - deletions
        }
