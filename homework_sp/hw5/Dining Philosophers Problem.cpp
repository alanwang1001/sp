#include <iostream>
#include <thread>
#include <mutex>
#include <vector>
#include <chrono>

const int NUM_PHILOSOPHERS = 5;
std::mutex forks[NUM_PHILOSOPHERS];

void philosopher(int id) {
    int left_fork = id;
    int right_fork = (id + 1) % NUM_PHILOSOPHERS;

    for (int i = 0; i < 2; ++i) { // 每位哲學家吃兩次
        std::cout << "哲學家 " << id << " 正在思考...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        // 避免死結的核心：使用 std::lock 同時獲取兩把鎖，若無法同時獲取則等待
        std::lock(forks[left_fork], forks[right_fork]);
        
        // 將獲取到的鎖交給 lock_guard 管理生命週期 (adopt_lock 表示已經上鎖了)
        std::lock_guard<std::mutex> left_lock(forks[left_fork], std::adopt_lock);
        std::lock_guard<std::mutex> right_lock(forks[right_fork], std::adopt_lock);

        std::cout << "哲學家 " << id << " 拿起了叉子 " << left_fork << " 和 " << right_fork << "，開始進食。\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(200)); // 模擬進食時間
        std::cout << "哲學家 " << id << " 放下叉子，結束進食。\n";
    }
}

int main() {
    std::vector<std::thread> philosophers;
    for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
        philosophers.push_back(std::thread(philosopher, i));
    }

    for (auto& p : philosophers) {
        p.join();
    }
    return 0;
}
