#include "shell.h"
#include <iostream>
#include <sstream>
#include <unistd.h>
#include <sys/wait.h>
#include <cstring>

std::vector<std::string> MiniShell::parseCommand(const std::string& input) {
    std::vector<std::string> args;
    std::istringstream iss(input);
    std::string token;
    // 依空白字元切割輸入字串
    while (iss >> token) {
        args.push_back(token);
    }
    return args;
}

bool MiniShell::executeCommand(std::vector<std::string>& args) {
    if (args.empty()) return true;

    // 實作內建指令 (Built-in commands)
    if (args[0] == "exit") return false; // 結束 shell
    
    if (args[0] == "cd") {
        if (args.size() > 1) {
            // 使用 chdir System Call 切換目錄
            if (chdir(args[1].c_str()) != 0) {
                perror("cd error");
            }
        } else {
            std::cerr << "cd: missing argument\n";
        }
        return true;
    }

    // 執行外部指令 (External commands)
    pid_t pid = fork(); // 建立子行程

    if (pid == 0) {
        // Child Process (子行程)
        // 將 C++ string vector 轉換為 execvp 需要的 char* 陣列
        std::vector<char*> c_args;
        for (auto& arg : args) {
            c_args.push_back(&arg[0]);
        }
        c_args.push_back(nullptr); // execvp 規定最後必須是 NULL

        // 載入並執行新程式
        if (execvp(c_args[0], c_args.data()) == -1) {
            perror("Execution failed");
        }
        exit(EXIT_FAILURE); // 如果 execvp 失敗，結束子行程
    } else if (pid > 0) {
        // Parent Process (父行程)
        int status;
        // 等待子行程執行完畢，避免產生 Zombie Process
        waitpid(pid, &status, 0); 
    } else {
        perror("Fork failed");
    }
    
    return true;
}

void MiniShell::run() {
    std::string input;
    // Shell 的主迴圈
    while (true) {
        std::cout << "myshell> ";
        if (!std::getline(std::cin, input)) break; // 處理 EOF (Ctrl+D)
        
        std::vector<std::string> args = parseCommand(input);
        if (!executeCommand(args)) break; // 如果回傳 false (例如輸入 exit)，則跳出迴圈
    }
}
