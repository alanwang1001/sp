#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>      // 提供 fork(), getpid(), getppid()
#include <sys/types.h>
#include <sys/wait.h>    // 提供 wait()

int main() {
    int x = 10; // 宣告一個區域變數，用來觀察父子行程是否互相影響

    printf("準備呼叫 fork()... 這是原始的行程 (PID = %d)\n", getpid());
    printf("---------------------------------------------------\n");

    // 【關鍵時刻】：在這裡進行「細胞分裂」
    pid_t pid = fork(); 

    // 從這行開始，如果 fork 成功，就會有「兩個」行程同時往下執行這段程式碼！
    // 我們必須透過 pid (回傳值) 來判斷現在自己是誰。

    if (pid < 0) {
        // 情境一：回傳值小於 0，代表分裂失敗 (通常是系統資源不足)
        perror("Fork 失敗了！");
        exit(1);
    } 
    else if (pid == 0) {
        // 情境二：回傳值等於 0，代表現在執行這段程式碼的是「子行程」
        
        x = x + 5; // 子行程把自己的 x 加上 5
        
        // getpid() 取得自己的 PID，getppid() 取得父親的 PID
        printf("【子行程】我是分身！我的 PID = %d, 我的父親是 PPID = %d\n", getpid(), getppid());
        printf("【子行程】我把變數 x 變成了: %d\n", x);
    } 
    else {
        // 情境三：回傳值大於 0，代表現在執行這段程式碼的是「父行程」
        // 此時的 pid 變數裡面，裝的是剛出生的「子行程的 PID」
        
        x = x - 2; // 父行程把自己的 x 減去 2
        
        printf("【父行程】我是本尊！我的 PID = %d, 我剛生出的孩子 PID = %d\n", getpid(), pid);
        printf("【父行程】我把變數 x 變成了: %d\n", x);

        // 作為一個負責任的父親，通常會等待子行程執行完畢再結束，
        // 否則子行程可能會變成「孤兒行程」或「殭屍行程」。
        wait(NULL); 
        printf("【父行程】確認子行程已經結束，我也要收工了。\n");
    }

    return 0;
}
