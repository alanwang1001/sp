#include <iostream>
#include <thread>
#include <mutex>

int balance = 0; // 共享資源：帳戶餘額
std::mutex mtx;  // 保護餘額的互斥鎖

// 存款執行緒函數
void deposit() {
    for (int i = 0; i < 100000; ++i) {
        std::lock_guard<std::mutex> lock(mtx); // 上鎖，離開作用域自動解鎖
        balance++;
    }
}

// 提款執行緒函數
void withdraw() {
    for (int i = 0; i < 100000; ++i) {
        std::lock_guard<std::mutex> lock(mtx);
        balance--;
    }
}

int main() {
    std::cout << "初始餘額: " << balance << std::endl;

    std::thread t1(deposit);
    std::thread t2(withdraw);

    t1.join();
    t2.join();

    std::cout << "最終餘額: " << balance << " (預期為 0)" << std::endl;
    return 0;
}
