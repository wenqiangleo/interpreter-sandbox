import ast
import sys
from typing import List, Set
from ..core.sandbox import SecurityError

class CodeAnalyzer:
    """代码分析器，用于检查代码安全性"""
    
    def __init__(self, allowed_modules: List[str] = None):
        self.allowed_modules = set(allowed_modules or [])
        self._dangerous_nodes = {
            ast.Import: self._check_import,
            ast.ImportFrom: self._check_import_from,
            ast.Call: self._check_call,
            ast.Attribute: self._check_attribute
        }
        
    def analyze(self, code: str) -> None:
        """分析代码安全性"""
        try:
            tree = ast.parse(code)
            self._visit_nodes(tree)
        except SyntaxError as e:
            raise SecurityError(f"Invalid syntax: {str(e)}")
            
    def _visit_nodes(self, node: ast.AST) -> None:
        """遍历AST节点"""
        for node_type, checker in self._dangerous_nodes.items():
            if isinstance(node, node_type):
                checker(node)
                
        for child in ast.iter_child_nodes(node):
            self._visit_nodes(child)
            
    def _check_import(self, node: ast.Import) -> None:
        """检查import语句"""
        for name in node.names:
            module_name = name.name.split('.')[0]
            if module_name not in self.allowed_modules:
                raise SecurityError(f"Import of module '{module_name}' is not allowed")
                
    def _check_import_from(self, node: ast.ImportFrom) -> None:
        """检查from ... import语句"""
        module_name = node.module.split('.')[0] if node.module else ''
        if module_name not in self.allowed_modules:
            raise SecurityError(f"Import from module '{module_name}' is not allowed")
            
    def _check_call(self, node: ast.Call) -> None:
        """检查函数调用"""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self._get_dangerous_functions():
                raise SecurityError(f"Call to dangerous function '{func_name}' is not allowed")
                
    def _check_attribute(self, node: ast.Attribute) -> None:
        """检查属性访问"""
        if isinstance(node.value, ast.Name):
            obj_name = node.value.id
            attr_name = node.attr
            if (obj_name, attr_name) in self._get_dangerous_attributes():
                raise SecurityError(f"Access to dangerous attribute '{obj_name}.{attr_name}' is not allowed")
                
    def _get_dangerous_functions(self) -> Set[str]:
        """获取危险函数列表"""
        return {
            'eval', 'exec', 'compile', 'open', 'input',
            'os.system', 'os.popen', 'subprocess.run',
            'subprocess.Popen', 'pickle.loads', 'marshal.loads'
        }
        
    def _get_dangerous_attributes(self) -> Set[tuple]:
        """获取危险属性列表"""
        return {
            ('os', 'system'), ('os', 'popen'),
            ('subprocess', 'run'), ('subprocess', 'Popen'),
            ('sys', 'stdin'), ('sys', 'stdout'), ('sys', 'stderr')
        } 