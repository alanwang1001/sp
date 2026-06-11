#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

int main() {
    printf("【父行程】準備執行 ls -l，但這次輸出不會在畫面上，會被存入 output.txt\n");

    // 1. 建立分身
    pid_t pid = fork();

    if (pid < 0) {
        perror("Fork 失敗");
        exit(1);
    } 
    else if (pid == 0) {
        // ---------------------------------------------------
        // 這裡是子行程專區：負責處理 I/O 重導向與執行新程式
        // ---------------------------------------------------
        
        // 2. 開啟目標檔案 (拿到號碼牌，假設是 3)
        // 權限 O_WRONLY(唯寫) | O_CREAT(沒有就建立) | O_TRUNC(有就清空), 0644
        int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            perror("開啟檔案失敗");
            exit(1);
        }

        // 3. 【核心魔法】：狸貓換太子
        // 把 標準輸出(1) 重導向到我們剛開的檔案(fd)
        dup2(fd, 1); 
        
        // 選擇性：如果你連錯誤訊息都想存進檔案，可以再加一行 dup2(fd, 2);

        // 既然 1 已經指向檔案了，原本的 fd 號碼牌就不需要了，關閉以節省資源
        close(fd);

        // 4. 換腦手術：執行 ls 指令
        char *args[] = {"ls", "-l", NULL};
        execvp(args[0], args);

        // 如果 execvp 成功，程式會被取代，這行絕對不會執行。
        // 若執行到這行，代表出錯了 (此時的 perror 會寫進檔案裡，因為 stderr 2 如果沒重導向，還是會在螢幕，但如果上面有 dup2(fd, 2) 就會進檔案)
        perror("execvp 失敗");
        exit(1);
    } 
    else {
        // ---------------------------------------------------
        // 這裡是父行程專區
        // ---------------------------------------------------
        
        // 父行程的 標準輸出(1) 還是指向螢幕的喔！因為 fork 出來的記憶體是獨立的
        int status;
        waitpid(pid, &status, 0); // 等待子行程完工
        printf("【父行程】子行程已經完工，請打開 output.txt 看看結果！\n");
    }

    return 0;
}
