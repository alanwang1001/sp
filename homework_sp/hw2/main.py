from lexer import Lexer
from parser import Parser
from compiler import Compiler
from vm import VM

def main():
    source_code = """
    let x = 10;
    let y = 5;
    let result = x + y * 2;

    if result > 15 {
        print result;
    }
    """

    print("=== 1. 原始碼 ===")
    print(source_code.strip())
    
    print("\n=== 2. 執行流程 ===")
    
    # 1. 詞法分析
    lexer = Lexer(source_code)
    
    # 2. 語法分析
    parser = Parser(lexer.tokens)
    ast = parser.parse()
    
    # 3. 編譯為中間碼
    compiler = Compiler()
    bytecode = compiler.compile(ast)
    
    print("產生的 Bytecode:")
    for i, instr in enumerate(bytecode):
        print(f"  {i:02d}: {instr}")

    print("\n=== 3. 虛擬機輸出 ===")
    
    # 4. 執行
    vm = VM(bytecode)
    vm.run()

if __name__ == '__main__':
    main()
