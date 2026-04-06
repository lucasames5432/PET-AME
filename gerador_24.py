import itertools
import csv
import json
import os
from typing import Self

# ==========================================
# 1. CLASSES MATEMÁTICAS (Sem Frações Decimais)
# ==========================================
p = '+'
m = '-'
t = '*'
d = '/'

class Expression:
    _left: Self
    _operation: str
    _right: Self

    def __init__(self, left: Self, operation: str, right: Self):
        self._left = left
        self._operation = operation
        self._right = right
        self._is_ordered = False
        self._is_singular = False

        if operation not in ['+', '-', '/', '*']:
            raise TypeError()
        return

    def to_string(self) -> str:
        if self._operation in ['+', '*']:
            # Pega os nós da árvore sem converter para decimal
            nodes = self.get_nodes_of_chain(self._operation)
            nodes = sorted(nodes, key=lambda n: (n.evaluate(), n.to_string()))
            str_values = [n.to_string() for n in nodes]
            return f'({f" {self._operation} ".join(str_values)})'
            
        return f'({self._left.to_string()} {self._operation} {self._right.to_string()})'

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f'Expression({self._left!r}, {self._operation!r}, {self._right!r})'

    def __add__(self, other: 'Expression'):
        return Expression(self, p, other)
    def __sub__(self, other: 'Expression'):
        return Expression(self, m, other)
    def __mul__(self, other: 'Expression'):
        return Expression(self, t, other)
    def __truediv__(self, other: 'Expression'):
        return Expression(self, d, other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Expression):
            return self.evaluate() == other.evaluate()
        if isinstance(other, float) or isinstance(other, int):
            return self.evaluate() == other
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def evaluate(self) -> float:
        match self._operation:
            case '+': return self._left.evaluate() + self._right.evaluate()
            case '-': return self._left.evaluate() - self._right.evaluate()
            case '*': return self._left.evaluate() * self._right.evaluate()
            case '/': 
                val_dir = self._right.evaluate()
                if val_dir == 0: return float('inf')
                return self._left.evaluate() / val_dir
        return 0

    def get_nodes_of_chain(self, target_op: str) -> list:
        if self._operation == target_op:
            return self._left.get_nodes_of_chain(target_op) + self._right.get_nodes_of_chain(target_op)
        return [self]

    def _order_self(self) -> None:
        self._is_ordered = True

        if self._operation == '-' and self._right.evaluate() == 0:
            self._operation = '+'
        if self._operation == '/' and self._right.evaluate() == 1:
            self._operation = '*'

        if self._operation == '-' and not self._left._is_singular and self._left._operation == '-':
            new_right = Expression(self._left._right, '+', self._right)
            self._left = self._left._left
            self._right = new_right

        if self._operation == '/' and not self._left._is_singular and self._left._operation == '/':
            new_right = Expression(self._left._right, '*', self._right)
            self._left = self._left._left
            self._right = new_right

        if self._operation == '*' and not self._left._is_singular and self._left._operation == '/':
            new_left = Expression(self._left._left, '*', self._right)
            new_right = self._left._right
            self._operation = '/'
            self._left = new_left
            self._right = new_right

        if self._operation == '*' and not self._right._is_singular and self._right._operation == '/':
            new_left = Expression(self._left, '*', self._right._left)
            new_right = self._right._right
            self._operation = '/'
            self._left = new_left
            self._right = new_right

        if self._operation == '+' and not self._left._is_singular and self._left._operation == '-':
            new_left = Expression(self._left._left, '+', self._right)
            new_right = self._left._right
            self._operation = '-'
            self._left = new_left
            self._right = new_right

        if self._operation == '+' and not self._right._is_singular and self._right._operation == '-':
            new_left = Expression(self._left, '+', self._right._left)
            new_right = self._right._right
            self._operation = '-'
            self._left = new_left
            self._right = new_right

        if self._operation == '-' and not self._right._is_singular and self._right._operation == '-':
            new_left = Expression(self._left, '+', self._right._right)
            new_right = self._right._left
            self._operation = '-'
            self._left = new_left
            self._right = new_right
            self._left.order()

        if self._operation == '/' and not self._right._is_singular and self._right._operation == '/':
            new_left = Expression(self._left, '*', self._right._right)
            new_right = self._right._left
            self._operation = '/'
            self._left = new_left
            self._right = new_right
            self._left.order()

        if self._operation in ['-', '/']:
            return

        if self._left.evaluate() < self._right.evaluate():
            return
        if self._left.evaluate() == self._right.evaluate():
            if self._left.to_string() <= self._right.to_string():
                return

        temporary = self._left
        self._left = self._right
        self._right = temporary

    def order(self) -> None:
        self._left.order()
        self._right.order()
        self._order_self()


class SingularExpression(Expression):
    _value: float

    def __init__(self, value:float):
        self._is_singular = True
        self._value = value

    def get_nodes_of_chain(self, target_op: str) -> list:
        return [self]

    def evaluate(self) -> float:
        return self._value

    def to_string(self) -> str:
        if self._value.is_integer():
            return str(self._value).replace('.0', '')
        return str(self._value)

    def order(self) -> None:
        return

    def __repr__(self) -> str:
        return f'SingularExpression({self._value!r})'


# ==========================================
# 2. MOTOR DE FORÇA BRUTA E FILTROS
# ==========================================
def filter_congruent_expressions(list_exp: list[Expression]) -> list[Expression]:
    return_list = []
    seen_strings = set()
    for exp in list_exp:
        exp.order()
        exp_str = exp.to_string()
        if exp_str not in seen_strings:
            seen_strings.add(exp_str)
            return_list.append(exp)
    return return_list

def list_subtraction(list1: list, list2: list) -> list:
    return_list = []
    for element in list1:
        if element in list2:
            list2.remove(element)
            continue
        return_list.append(element)
    return return_list

def all_possible_ops(e1: Expression, e2: Expression) -> list[Expression]:
    arr = [e1 + e2, e1 - e2, e1 * e2, e2 - e1]
    if e1.evaluate() != 0: arr.append(e2 / e1)
    if e2.evaluate() != 0: arr.append(e1 / e2)
    return arr

def recursive_solver(*cards: Expression, restrain_integers: bool=False) -> list[Expression]:
    cards_list = list(cards)
    solutions: list[Expression] = []

    if len(cards_list) == 1: solutions = cards_list
    if len(cards_list) == 2: solutions = all_possible_ops(cards_list[0], cards_list[1])

    if len(cards_list) == 3:
        two_couplings = itertools.combinations(cards_list, 2)
        for coupling in two_couplings:
            remaining_card = list_subtraction(cards_list, list(coupling))[0]
            result_coupling = recursive_solver(*coupling, restrain_integers=restrain_integers)
            for result in result_coupling:
                solutions += recursive_solver(result, remaining_card, restrain_integers=restrain_integers)

    if len(cards_list) == 4:
        three_couplings = itertools.combinations(cards_list, 3)
        for coupling in three_couplings:
            remaining_card = list_subtraction(cards_list, list(coupling))[0]
            result_coupling = recursive_solver(*coupling, restrain_integers=restrain_integers)
            for result in result_coupling:
                solutions += recursive_solver(result, remaining_card, restrain_integers=restrain_integers)

        two_couplings = itertools.combinations(cards_list, 2)
        for coupling in two_couplings:
            remaining_cards = list_subtraction(cards_list, list(coupling))
            result_coupling = recursive_solver(*coupling, restrain_integers=restrain_integers)
            result_remaining_cards = recursive_solver(*remaining_cards, restrain_integers=restrain_integers)
            for result1 in result_coupling:
                for result2 in result_remaining_cards:
                    solutions += recursive_solver(result1, result2, restrain_integers=restrain_integers)

    if restrain_integers:
        return [n for n in solutions if n.evaluate().is_integer()]
    return solutions

# ==========================================
# 3. SCRIPT PRINCIPAL E GERADOR DE ARQUIVOS
# ==========================================
def main() -> None:
    print("Iniciando o Mega Script (1820 combinações)... Pegue um café! ☕")

    all_hands_raw = list(itertools.combinations_with_replacement(range(1, 14), 4))

    jogos_com_solucao = []
    todas_solucoes_limpas = []
    jogos_com_solucoes_js = {}
    counter_games = 0

    for hand in all_hands_raw:
        counter_games += 1
        cards = [SingularExpression(n) for n in hand]

        solutions = recursive_solver(*cards, restrain_integers=False)
        solutions_24 = [n for n in solutions if abs(n.evaluate() - 24) <= 1e-5]

        if solutions_24:
            jogos_com_solucao.append(hand)
            filtered_solutions = filter_congruent_expressions(solutions_24)
            
            str_hand = str(list(hand))
            jogos_com_solucoes_js[str_hand] = []
            
            for sol in filtered_solutions:
                str_sol = sol.to_string()
                todas_solucoes_limpas.append([str_hand, str_sol])
                jogos_com_solucoes_js[str_hand].append(str_sol)

        if counter_games % 100 == 0:
            print(f"Progresso: {counter_games}/1820 mãos processadas...")

    # Define a pasta atual para salvar os arquivos
    pasta_atual = os.path.dirname(os.path.abspath(__file__))

    # ARQUIVO 1: CSV de Mãos (Para o artigo)
    with open(os.path.join(pasta_atual, 'jogos_com_solucao.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Carta 1', 'Carta 2', 'Carta 3', 'Carta 4'])
        writer.writerows(jogos_com_solucao)

    # ARQUIVO 2: CSV de Soluções (Para o artigo)
    with open(os.path.join(pasta_atual, 'todas_as_solucoes.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Mao_Cartas', 'Solucao_Matematica'])
        writer.writerows(todas_solucoes_limpas)
        
    # ARQUIVO 3: BANCO DE DADOS JAVASCRIPT (Para o site do PET)
    with open(os.path.join(pasta_atual, 'banco_solucoes.js'), 'w', encoding='utf-8') as f:
        f.write("// Arquivo gerado automaticamente pelo Mega Script\n")
        f.write("const bancoSolucoes = " + json.dumps(jogos_com_solucoes_js, indent=4) + ";\n")
        f.write("const maosValidas = Object.keys(bancoSolucoes).map(x => JSON.parse(x));\n")

    print("\n✅ TUDO PRONTO!")
    print(f"-> Combinações resolvíveis: {len(jogos_com_solucao)}")
    print("Os arquivos CSV e o arquivo 'banco_solucoes.js' foram criados na mesma pasta deste script!")

if __name__ == "__main__":
    main()