#ifndef SHELL_H
#define SHELL_H

#include <string>
#include <vector>

class MiniShell {
public:
    // 啟動 Shell 的主迴圈
    void run();

private:
    // 解析使用者輸入的指令
    std::vector<std::string> parseCommand(const std::string& input);
    // 執行指令 (包含內建指令與外部程式)
    bool executeCommand(std::vector<std::string>& args);
};

#endif
