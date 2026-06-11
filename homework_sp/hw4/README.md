# ⚡ 系統程式設計實務指南：從系統呼叫到多執行緒同步
> **System Programming: From System Calls to Multi-Threading Synchronization**

---

## 📘 本書簡介

本書專門為資訊工程與電腦科學相關科系學生設計，旨在建構從核心作業系統（OS）到使用者應用程式之間的橋樑。系統程式（System Programming）的精髓在於理解程式如何與底層硬體、作業系統內核進行高效率且安全的互動。

本書透過大量嚴謹的 **C 語言系統範例**、**記憶體架構圖解** 以及**核心機制解析**，帶領讀者深入系統開發的核心領域。

---

## 📌 目錄
1. [第一章：系統呼叫與檔案 I/O 機制 (System Calls & File I/O)](#第一章系統呼叫與檔案-io-機制-system-calls--file-io)
   - 1.1 使用者模式與內核模式的轉換
   - 1.2 檔案描述子 (File Descriptor) 與系統核心結構
   - 1.3 實戰：低階檔案控制與錯誤處理
2. [第二章：行程與執行緒生命週期 (Process & Thread Lifecycle)](#第二章行程與執行緒生命週期-process--thread-lifecycle)
   - 2.1 行程控制區塊 (PCB) 與上下文切換 (Context Switch)
   - 2.2 `fork()`、`exec()` 與 `wait()` 的深層運作邏輯
   - 2.3 POSIX Thread (pthread) 的建立與資源共享
3. [第三章：行程間通訊深度剖析 (Deep Dive into IPC)](#第三章行程間通訊深度剖析-deep-dive-into-ipc)
   - 3.1 匿名管道 (Anonymous Pipes) 的半雙工通訊
   - 3.2 共享記憶體 (Shared Memory) 的高效率存取
4. [第四章：並行控制與同步機制 (Concurrency & Synchronization)](#第四章並行控制與同步機制-concurrency--synchronization)
   - 4.1 競爭條件 (Race Condition) 與臨界區 (Critical Section)
   - 4.2 互斥鎖 (Mutex) 與號誌量 (Semaphore) 實戰
   - 4.3 死鎖 (Deadlock) 的四個必要條件與預防

---

## 第一章：系統呼叫與檔案 I/O 機制 (System Calls & File I/O)

### 1.1 使用者模式與內核模式的轉換

在現代作業系統中，為了確保系統安全與穩定，CPU 的執行狀態被劃分為不同的特權等級（Privilege Levels），通常在 x86 架構中稱為 **Ring 0（核心模式/Kernel Mode）** 與 **Ring 3（使用者模式/User Mode）**。

* **使用者模式 (User Mode)：** 一般應用程式運行的狀態。此模式下，程式無法直接存取硬體設備（如硬碟、網路卡）或受保護的記憶體空間。
* **核心模式 (Kernel Mode)：** 作業系統內核運行的狀態。擁有至高無上的權限，可直接執行任何 CPU 指令並存取所有硬體。

當應用程式需要讀取檔案時，必須透過 **系統呼叫 (System Call)** 來請求內核代為執行。這個過程伴隨著**軟體中斷（Software Interrupt）**或陷阱（Trap），觸發 CPU 進行模式切換，並保護目前的暫存器狀態（Context Save）。
### 1.2 檔案描述子 (File Descriptor) 與系統核心結構

對 Linux / Unix 系統而言，「**一切皆檔案 (Everything is a file)**」。不論是普通文件、目錄、網路 Socket、還是硬體設備，在使用者空間中都是透過一個非負整數來代表，這個整數就是 **檔案描述子 (File Descriptor, FD)**。

每個行程在核心中都有一個 `task_struct`（行程控制塊），其中包含一個檔案描述子表（File Descriptor Table）。核心透過三個層次的表格來管理檔案：

1.  **行程檔案描述子表 (Per-process FD Table)：** 索引值即為 FD，指向系統級的開啟檔案表。
2.  **系統開啟檔案表 (System-wide Open File Table)：** 紀錄檔案的讀寫偏移量（File Offset）、存取權限（讀/寫）以及指向 i-node 表的指標。
3.  **核心 i-node 表 (System-wide i-node Table)：** 紀錄檔案在磁碟上的實際屬性（大小、權限、所在區塊）。

> **預設的三個 FD：**
> * `0`: 標準輸入 (`stdin`)
> * `1`: 標準輸出 (`stdout`)
> * `2`: 標準錯誤輸出 (`stderr`)

### 1.3 實戰：低階檔案控制與錯誤處理

以下是一個使用 C 語言直接呼叫 POSIX 標準系統呼叫 `open()`、`read()`、`write()` 與 `close()` 的檔案複製程式。程式中加入了嚴謹的錯誤處理機制（使用 `errno` 與 `perror`）。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

#define BUFFER_SIZE 1024

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "使用方法: %s <來源檔案> <目的檔案>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    // 1. 開啟來源檔案（唯讀模式）
    int src_fd = open(argv[1], O_RDONLY);
    if (src_fd == -1) {
        perror("無法開啟來源檔案");
        exit(EXIT_FAILURE);
    }

    // 2. 開啟/建立目的檔案（唯寫模式、若不存在則建立、若存在則清空，權限設為 0644）
    int dest_fd = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (dest_fd == -1) {
        perror("無法建立目的檔案");
        close(src_fd);
        exit(EXIT_FAILURE);
    }

    char buffer[BUFFER_SIZE];
    ssize_t bytes_read, bytes_written;

    // 3. 讀寫循環核心
    while ((bytes_read = read(src_fd, buffer, BUFFER_SIZE)) > 0) {
        bytes_written = write(dest_fd, buffer, bytes_read);
        if (bytes_written != bytes_read) {
            perror("寫入資料時發生錯誤或不完整");
            close(src_fd);
            close(dest_fd);
            exit(EXIT_FAILURE);
        }
    }

    if (bytes_read == -1) {
        perror("讀取檔案時發生錯誤");
    }

    // 4. 關閉檔案描述子，釋放核心資源

    close(src_fd);
    close(dest_fd);

    printf("檔案複製成功！\n");
    return 0;
}
```

# 第二章：行程與執行緒生命週期 (Process & Thread Lifecycle)

> **本章導讀：**
> 程式碼被編譯器轉譯成執行檔後，靜靜地躺在硬碟裡，這時它只是一個「程式 (Program)」。當作業系統將它載入記憶體並由 CPU 開始執行時，它就擁有了生命，成為一個「行程 (Process)」。本章將帶你深入了解作業系統如何管理這些生命，以及比行程更輕量的「執行緒 (Thread)」是如何運作的。

---

## 2.1 行程與核心管理機制 (Process & Kernel Management)

### 2.1.1 行程控制區塊 (PCB, Process Control Block)
在多工作業系統中，同一時間可能會有數百個行程在背景運作。作業系統核心為了管理這些行程，會為每一個行程建立一個專屬的資料結構，稱為 **行程控制區塊 (PCB)**（在 Linux 核心原始碼中被定義為 `struct task_struct`）。

PCB 就像是這個行程的「身分證與履歷表」，裡面紀錄了極度關鍵的資訊：
1. **行程識別碼 (PID, Process ID)：** 系統中獨一無二的整數編號。
2. **行程狀態 (Process State)：** 例如執行中 (Running)、就緒 (Ready)、阻塞/等待中 (Blocked/Waiting)。
3. **程式計數器 (Program Counter, PC)：** 紀錄這個行程下一行要執行的指令記憶體位址。
4. **CPU 暫存器快照：** 當行程被暫停時，必須把 CPU 暫存器裡的計算結果存放在這裡。
5. **記憶體管理資訊：** 紀錄該行程的虛擬記憶體分頁表 (Page Table)。
6. **開啟的檔案列表：** 檔案描述子表 (File Descriptor Table)。

### 2.1.2 上下文切換 (Context Switch)
當 CPU 決定暫停執行「行程 A」，改為執行「行程 B」的過程，就稱為**上下文切換**。
這是一個非常耗費效能的動作。因為核心必須先將 CPU 目前所有的暫存器狀態「存檔」寫入行程 A 的 PCB；接著，再從行程 B 的 PCB 中「讀取」狀態覆蓋到 CPU 暫存器上。此外，還必須刷新 CPU 內的記憶體快取 (TLB Flush)，因為兩個行程的記憶體空間是完全隔離的。

---

## 2.2 行程的建立與終止：`fork`、`exec` 與 `wait`

在 UNIX/Linux 系統中，創造新行程的方式非常特別：**系統不會「憑空創造」新行程，而是透過「複製」舊行程來產生。**

### 2.2.1 核心系統呼叫解析
* **`fork()` (分叉)：** 這是建立新行程的唯一常規方法。當父行程呼叫 `fork()` 時，作業系統會複製父行程的 PCB、記憶體空間與檔案描述子表，產生一個子行程。
  * **寫時複製 (Copy-on-Write, CoW)：** 為了節省記憶體，剛複製完時，父子共用同一塊實體記憶體，只有當其中一方試圖「修改」變數時，系統才會真正切出一塊新記憶體給子行程。
  * **神奇的雙返回值：** `fork()` 呼叫一次，卻會返回兩次！在父行程中會回傳子行程的 PID；在子行程中則回傳 0。
* **`exec()` 系列：** `fork()` 只會複製出雙胞胎，如果我們希望子行程去執行「完全不同的程式」（例如去執行 `ls` 指令），就必須呼叫 `exec()`。它會把目前的行程清空，換上新程式的程式碼與資料。
* **`wait()` (等待與回收)：** 當子行程執行結束（呼叫 `exit()`）時，它並不會立刻消失，而是會變成 **殭屍行程 (Zombie Process)**，保留著 PID 和結束狀態碼。父行程必須呼叫 `wait()` 來幫子行程「收屍」，釋放最後的系統資源。

### 2.2.2 實戰程式碼：父子行程控制與指令執行

以下範例展示了如何使用 `fork` 產生子行程，讓子行程透過 `execvp` 執行終端機指令，並讓父行程透過 `wait` 安全地回收資源。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main() {
    printf("系統程式啟動，目前父行程 PID: %d\n", getpid());

    // 呼叫 fork() 建立子行程
    pid_t pid = fork();

    if (pid < 0) {
        // pid 小於 0 代表系統資源不足，建立失敗
        perror("Fork 失敗");
        exit(EXIT_FAILURE);
    } 
    else if (pid == 0) {
        // ==========================================
        // 這裡是【子行程】執行的區域 (fork 回傳 0)
        // ==========================================
        printf("[子行程] 誕生！我的 PID: %d, 我的老爸 PID: %d\n", getpid(), getppid());
        printf("[子行程] 我即將捨棄原本的程式碼，換裝去執行 'ls -l' 指令...\n");
        
        // 準備 execvp 需要的參數陣列，必須以 NULL 結尾
        char *args[] = {"ls", "-l", NULL};
        
        // 執行外部程式。一旦成功，子行程的記憶體就會被 'ls' 覆蓋，永遠不會回到下一行
        execvp(args[0], args);
        
        // 如果程式走到這裡，代表 execvp 找不到該指令或執行失敗
        perror("[子行程] Exec 執行失敗");
        exit(EXIT_FAILURE);
    } 
    else {
        // ==========================================
        // 這裡是【父行程】執行的區域 (fork 回傳子行程的 PID)
        // ==========================================
        int status;
        printf("[父行程] 成功建立子行程 (PID: %d)。我在這裡等待他工作結束...\n", pid);
        
        // 阻塞等待，直到任何一個子行程結束
        pid_t child_pid = wait(&status);
        
        // 檢查子行程是否是正常呼叫 exit() 或 return 結束的
        if (WIFEXITED(status)) {
            printf("[父行程] 收到通知！子行程 %d 已正常結束，離開狀態碼: %d\n", 
                   child_pid, WEXITSTATUS(status));
        } else {
            printf("[父行程] 警告：子行程異常終止（可能被訊號強制砍除）。\n");
        }
    }
    
    return 0;
}

---
```

# 第三章：行程間通訊深度剖析 (Deep Dive into IPC)

> **本章導讀：**
> 在上一章中，我們學會了如何使用 `fork()` 建立子行程。然而，現代作業系統為了安全起見，具備嚴格的**記憶體保護機制 (Memory Protection)**。行程 A 的變數與記憶體，行程 B 絕對無法直接讀取或修改。
> 既然大家都被關在各自的「虛擬記憶體沙盒」裡，行程之間該如何聊天、交換資料或分工合作呢？這就是本章要探討的核心技術：**行程間通訊 (Inter-Process Communication, IPC)**。

---

## 3.1 為什麼需要 IPC？記憶體隔離的挑戰

當我們呼叫 `fork()` 產生子行程時，子行程會獲得父行程記憶體空間的一份「完整副本」。雖然一開始裡面的資料長得一模一樣，但它們在實體記憶體中是完全獨立的兩塊區域。

**核心觀念：**
在父行程中修改變數 `x`，子行程的變數 `x` **絕對不會**跟著改變。如果父子行程需要共同完成一項任務（例如：子行程負責讀取檔案，父行程負責將資料顯示到畫面上），我們就必須依賴作業系統核心（Kernel）提供的 IPC 通道來傳遞資料。

常見的 IPC 機制包含：
1. **Pipes (管道)**
2. **Shared Memory (共享記憶體)**
3. **Message Queues (訊息佇列)**
4. **Sockets (網路套接字)**
5. **Signals (訊號)**

本章將聚焦於系統程式中最基礎且最常用的兩種：**管道**與**共享記憶體**。

---

## 3.2 匿名管道 (Anonymous Pipes)：最古老的通訊通道

**匿名管道 (Pipe)** 是 UNIX 系統中最經典的通訊方式。你可以把它想像成一根埋在作業系統核心裡的水管。
* **半雙工 (Half-Duplex)：** 資料只能「單向」流動。一端專門用來灌水（寫入），另一端專門用來接水（讀取）。
* **串聯父子行程：** 建立管道會產生兩個檔案描述子 (FD)，通常結合 `fork()` 使用，讓父行程拿著寫入端，子行程拿著讀取端，藉此達成通訊。

### 3.2.1 管道的運作流程
1. 呼叫 `pipe(fd)` 建立管道。`fd[0]` 是讀取端，`fd[1]` 是寫入端。
2. 呼叫 `fork()` 建立子行程。此時父子雙方都擁有這兩個 FD。
3. **重要步驟：關閉不需要的端點。** 如果父行程負責寫、子行程負責讀，那麼父行程必須關閉 `fd[0]`，子行程必須關閉 `fd[1]`。

### 3.2.2 實戰程式碼：使用 Pipe 傳遞訊息

以下範例展示父行程如何透過管道將一段字串傳送給子行程。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

#define BUFFER_SIZE 1024

int main() {
    int pipefd[2];
    pid_t pid;
    char buffer[BUFFER_SIZE];

    // 1. 建立管道 (必須在 fork 之前建立)
    if (pipe(pipefd) == -1) {
        perror("管道建立失敗");
        exit(EXIT_FAILURE);
    }

    // 2. 建立子行程
    pid = fork();

    if (pid < 0) {
        perror("Fork 失敗");
        exit(EXIT_FAILURE);
    } 
    else if (pid == 0) {
        // ==========================================
        // 【子行程：負責接收資料 (讀取)】
        // ==========================================
        // 養成好習慣：關閉用不到的「寫入端」
        close(pipefd[1]); 
        
        printf("[子行程] 等待父行程傳送資料...\n");
        
        // 阻塞讀取，直到管道內有資料 (或寫入端被完全關閉)
        ssize_t bytes_read = read(pipefd[0], buffer, BUFFER_SIZE - 1);
        
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0'; // 補上字串結尾符號
            printf("[子行程] 收到訊息囉: \"%s\"\n", buffer);
        }
        
        // 讀取完畢，關閉讀取端
        close(pipefd[0]);
        exit(EXIT_SUCCESS);
    } 
    else {
        // ==========================================
        // 【父行程：負責發送資料 (寫入)】
        // ==========================================
        // 養成好習慣：關閉用不到的「讀取端」
        close(pipefd[0]); 
        
        const char *msg = "孩子你好，這是一份來自作業系統核心的機密文件！";
        printf("[父行程] 準備將資料寫入管道...\n");
        
        // 將資料寫入管道中
        write(pipefd[1], msg, strlen(msg));
        
        // 寫入完畢後，關閉寫入端。這會讓子行程的 read() 收到 EOF (End of File) 而結束阻塞
        close(pipefd[1]);
        
        // 等待子行程安全結束
        wait(NULL);
        printf("[父行程] 通訊完畢，程式結束。\n");
    }

    return 0;
}

---
```

# 第四章：並行控制與同步機制 (Concurrency & Synchronization)

> **本章導讀：**
> 在第二章中，我們見識到了多執行緒 (Multi-threading) 帶來的極速效能與資源共享優勢。然而，「共享」是一把雙面刃。當多個執行緒同時去修改同一個記憶體區塊時，就如同多台車輛在沒有紅綠燈的十字路口全速搶道，必將釀成車禍（資料毀損）。
> 本章將深入探討並行程式設計中的災難來源，並介紹作業系統核心提供的交通號誌：互斥鎖與號誌量。

---

## 4.1 混亂的開端：競爭條件與臨界區

### 4.1.1 競爭條件 (Race Condition)
當兩個以上的執行緒或行程，同時存取並修改同一個共享資源（例如全域變數、共享記憶體），且程式最終的執行結果完全取決於 CPU 排程器切換執行緒的「隨機順序」時，這種現象就稱為 **競爭條件 (Race Condition)**。

在底層系統中，一句簡單的 `counter++` 其實是由三道組合語言指令構成的：
1. `LOAD`：從記憶體將變數讀進 CPU 暫存器。
2. `ADD`：在暫存器內將數值加 1。
3. `STORE`：將暫存器的數值寫回記憶體。

如果執行緒 A 剛做完 `ADD` 卻還沒 `STORE`，CPU 就被切換給執行緒 B，B 讀到的就會是舊的錯誤資料。最終兩次加法只會產生一次的效果。

### 4.1.2 臨界區 (Critical Section)
程式碼中「會存取到共享資源」的那段危險區域，我們稱為 **臨界區**。
舉例來說，當我們開發多執行緒程式，讓多個執行緒同時對一棵 AVL 樹進行節點插入與平衡旋轉，抑或是在雜湊表（Hash Table）中進行線性探測（Linear Probing）處理碰撞時，這段修改指標與寫入記憶體的程式碼區塊，就是標準的臨界區。一旦沒有保護好，樹的結構或雜湊鍊會瞬間斷裂大亂。

**同步機制的唯一守則：同一時間，絕對只允許一個執行緒進入臨界區。**

---

## 4.2 互斥鎖 (Mutex)：捍衛臨界區的鐵門

**互斥鎖 (Mutual Exclusion, Mutex)** 是最單純也最常用的同步工具。你可以把它想像成洗手間的鑰匙：
1. 執行緒要進入臨界區前，必須先嘗試「上鎖 (Lock)」。
2. 如果鎖已經被別人拿走了，該執行緒就會被作業系統強制「阻塞 (Blocked)」，在門外排隊睡覺。
3. 等到裡面的人出來並「解鎖 (Unlock)」後，作業系統會喚醒門外的下一個執行緒。

### 4.2.1 實戰程式碼：使用 `pthread_mutex_t` 保護計數器

以下範例展示了兩個執行緒同時對全域變數加 10 萬次。如果不加鎖，結果絕對不到 20 萬；加上 Mutex 後，每一次的加法都受到完美保護。

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define ITERATIONS 100000

// 共享資源
long counter = 0;

// 定義並靜態初始化互斥鎖
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void* worker_thread(void* arg) {
    int id = *(int*)arg;
    
    for (int i = 0; i < ITERATIONS; i++) {
        // --- 進入臨界區前，先上鎖 ---
        pthread_mutex_lock(&lock);
        
        // ==========================================
        // 臨界區 (Critical Section) 開始
        // 這裡面的程式碼，同一時間絕對只有一個執行緒在跑
        // ==========================================
        counter++; 
        
        // --- 離開臨界區，立刻解鎖 ---
        pthread_mutex_unlock(&lock);
    }
    
    printf("[執行緒 %d] 完工！\n", id);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    int id1 = 1, id2 = 2;

    // 建立兩個執行緒
    pthread_create(&t1, NULL, worker_thread, &id1);
    pthread_create(&t2, NULL, worker_thread, &id2);

    // 等待執行緒結束
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    // 預期 200,000
    printf("預期數值: %d\n", ITERATIONS * 2);
    printf("最終計數器數值: %ld\n", counter);

    // 銷毀互斥鎖，釋放系統資源
    pthread_mutex_destroy(&lock);

    return 0;
}
