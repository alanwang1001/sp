# 系統程式作業報告：行程控制與檔案 I/O 完整實作指南

本文件詳細說明並實作了 UNIX/Linux 系統中最核心的兩大概念：**行程控制 (Process Control)** 與 **檔案 I/O (File I/O)**。內容涵蓋 `fork`, `execvp`, `open`, `read`, `write`, `close`, `dup2` 以及標準檔案描述符的應用。

---

## 第一部分：行程控制之起點 —— `fork()`

### 核心概念：系統中的「影分身之術」
`fork()` 是建立新行程（Process）的基礎方法。呼叫 `fork()` 時，作業系統會將目前的行程（父行程）完美複製一份，產生一個全新的行程（子行程）。兩者擁有相同的程式碼與狀態，但記憶體空間是獨立的。

**最關鍵的機制：回傳值**
一次 `fork()` 呼叫，會產生兩個不同的回傳值：
1. **在父行程中**：回傳大於 0 的整數（剛出生的子行程 PID）。
2. **在子行程中**：固定回傳 0。
3. **若回傳 -1**：代表建立失敗（系統資源不足）。

### 實作程式碼：`fork_demo.c`
此程式展示了如何透過回傳值讓父子行程執行不同的工作，並驗證記憶體獨立性。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main() {
    int x = 10; // 觀察父子行程是否互相影響的變數

    printf("準備呼叫 fork()... 這是原始的行程 (PID = %d)\n", getpid());
    printf("---------------------------------------------------\n");

    pid_t pid = fork(); // 進行細胞分裂

    if (pid < 0) {
        perror("Fork 失敗！");
        exit(1);
    } 
    else if (pid == 0) {
        // --- 子行程專區 ---
        x = x + 5; 
        printf("【子行程】PID = %d, PPID = %d\n", getpid(), getppid());
        printf("【子行程】變數 x 變成了: %d\n", x);
    } 
    else {
        // --- 父行程專區 ---
        x = x - 2; 
        printf("【父行程】PID = %d, 剛生出的孩子 PID = %d\n", getpid(), pid);
        printf("【父行程】變數 x 變成了: %d\n", x);

        wait(NULL); // 等待子行程結束，避免產生殭屍行程
        printf("【父行程】確認子行程已經結束，收工。\n");
    }

    return 0;
}
```

---

## 第二部分：行程換腦手術 —— `execvp()`

### 核心概念：Fork-Exec 模式
`execvp()` 會將當前行程的記憶體（程式碼、資料等）全部清空，並載入另一個全新的程式取代它。因為這是一場「換腦手術」，**只要 `execvp()` 成功，寫在它後面的程式碼永遠都不會被執行到**。

通常我們採用 **Fork-Exec 模式**：父行程 `fork` 出子行程，然後子行程呼叫 `execvp` 變成另一個程式執行，而父行程在旁邊等待 (`wait`)。

### 實作程式碼：`exec_demo.c`
此程式模擬在終端機執行 `ls -l` 指令。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    printf("【父行程】準備執行 ls -l 指令...\n");

    pid_t pid = fork();

    if (pid < 0) {
        perror("Fork 失敗");
        exit(1);
    } 
    else if (pid == 0) {
        // --- 子行程專區 ---
        printf("【子行程】準備變成 ls 程式！\n");

        char *args[] = {"ls", "-l", NULL}; // 必須以 NULL 結尾
        execvp(args[0], args);

        // 如果 execvp 成功，這行永遠不會執行
        perror("execvp 失敗了！找不到指令！");
        exit(1); 
    } 
    else {
        // --- 父行程專區 ---
        int status;
        waitpid(pid, &status, 0); 
        printf("【父行程】子行程 (ls) 已經執行結束。\n");
    }

    return 0;
}
```

---

## 第三部分：檔案 I/O 基礎 —— `open`, `read`, `write`, `close`

### 核心概念：檔案描述符 (File Descriptor, FD)
作業系統不會直接把檔案給你，而是給你一個非負整數的「號碼牌」，稱為 FD。後續的讀寫都認這個號碼。
* **`open`**：開啟檔案，取得 FD。常用 flags 包括 `O_RDONLY` (唯讀), `O_WRONLY` (唯寫), `O_CREAT` (不存在則建立), `O_TRUNC` (存在則清空)。
* **`read` / `write`**：搭配 Buffer（緩衝區）批次搬運資料，減少系統呼叫次數以提升效能。
* **`close`**：釋放資源，確保資料寫入磁碟。

### 實作程式碼：檔案複製 (File Copy)

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

#define BUFFER_SIZE 1024

int main() {
    int fd_in, fd_out; 
    ssize_t bytes_read, bytes_written;
    char buffer[BUFFER_SIZE];

    // 1. 開啟來源檔案 (唯讀)
    fd_in = open("source.txt", O_RDONLY);
    if (fd_in < 0) {
        perror("開啟 source.txt 失敗");
        exit(1);
    }

    // 2. 開啟目的檔案 (唯寫 | 不存在就建立 | 存在就清空，權限 0644)
    fd_out = open("dest.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd_out < 0) {
        perror("開啟 dest.txt 失敗");
        close(fd_in);
        exit(1);
    }

    // 3. 迴圈搬運
    while ((bytes_read = read(fd_in, buffer, BUFFER_SIZE)) > 0) {
        bytes_written = write(fd_out, buffer, bytes_read);
        if (bytes_written != bytes_read) {
            perror("寫入時發生錯誤");
            break;
        }
    }

    // 4. 關閉檔案
    close(fd_in);
    close(fd_out);

    printf("檔案複製成功！\n");
    return 0;
}
```

---

## 第四部分：標準 I/O 與重導向 —— `0, 1, 2` 與 `dup2`

### 核心概念：狸貓換太子的魔法
行程啟動時，作業系統預設開啟三個 FD：
* **`0` (stdin)**：標準輸入（鍵盤）
* **`1` (stdout)**：標準輸出（螢幕）
* **`2` (stderr)**：標準錯誤（螢幕）

**`dup2(oldfd, newfd)`** 的作用是強迫 `newfd` 指向與 `oldfd` 相同的地方。如果我們打開一個檔案得到 FD 3，然後呼叫 `dup2(3, 1)`，原本指向螢幕的 FD 1 就會改指嚮檔案。這就是命令列 `>` (重導向) 的底層原理。

### 實作程式碼：自製 `ls -l > output.txt`
此程式結合了行程控制與檔案 I/O，是 Shell 運作的核心原型。

```c

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

int main() {
    printf("【父行程】準備執行 ls -l，輸出將被重導向至 output.txt\n");

    pid_t pid = fork();

    if (pid < 0) {
        perror("Fork 失敗");
        exit(1);
    } 
    else if (pid == 0) {
        // --- 子行程專區：負責重導向與換腦 ---
        
        // 1. 開啟目標檔案
        int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            perror("開啟檔案失敗");
            exit(1);
        }

        // 2. I/O 重導向：將 標準輸出(1) 指嚮檔案(fd)
        dup2(fd, 1); 
        
        // 3. 關閉不需要的 fd
        close(fd);

        // 4. 執行新指令 (execvp 會繼承已經被重導向的 FD 1)
        char *args[] = {"ls", "-l", NULL};
        execvp(args[0], args);

        perror("execvp 失敗");
        exit(1);
    } 
    else {
        // --- 父行程專區 ---
        // 父行程的 FD 1 依然指向螢幕，不受子行程影響
        int status;
        waitpid(pid, &status, 0); 
        printf("【父行程】子行程完工，請查看 output.txt 結果！\n");
    }

    return 0;
}
```
