#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>   // 給 open 用的 O_RDONLY 等巨集
#include <unistd.h>  // 給 read, write, close 用的

#define BUFFER_SIZE 1024 // 我們準備一個 1KB 的推車 (Buffer) 來搬運資料

int main() {
    // 準備兩個變數來接「號碼牌」
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
        close(fd_in); // 記得把前面開好的先關掉
        exit(1);
    }

    // 3. 開始迴圈搬運
    // 只要 read 回傳值大於 0，代表還有讀到東西
    while ((bytes_read = read(fd_in, buffer, BUFFER_SIZE)) > 0) {
        // 讀到多少 bytes，就完完整整地寫入多少 bytes 到新檔案
        bytes_written = write(fd_out, buffer, bytes_read);
        
        if (bytes_written != bytes_read) {
            perror("寫入時發生錯誤");
            break;
        }
    }

    // 4. 用完一定要歸還號碼牌 (關閉檔案)
    close(fd_in);
    close(fd_out);

    printf("檔案複製成功！\n");
    return 0;
}
