#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <chrono>

std::queue<int> buffer;
const unsigned int MAX_SIZE = 5; // 緩衝區最大容量
std::mutex mtx;
std::condition_variable cv_producer, cv_consumer;

void producer() {
    for (int i = 1; i <= 10; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        // 如果緩衝區滿了，生產者等待
        cv_producer.wait(lock, [] { return buffer.size() < MAX_SIZE; });
        
        buffer.push(i);
        std::cout << "生產者製造了: " << i << " (目前庫存: " << buffer.size() << ")\n";
        
        lock.unlock();
        cv_consumer.notify_all(); // 喚醒消費者
        std::this_thread::sleep_for(std::chrono::milliseconds(100)); // 模擬生產時間
    }
}

void consumer() {
    for (int i = 1; i <= 10; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        // 如果緩衝區空的，消費者等待
        cv_consumer.wait(lock, [] { return !buffer.empty(); });
        
        int item = buffer.front();
        buffer.pop();
        std::cout << "消費者消耗了: " << item << " (目前庫存: " << buffer.size() << ")\n";
        
        lock.unlock();
        cv_producer.notify_all(); // 喚醒生產者
        std::this_thread::sleep_for(std::chrono::milliseconds(150)); // 模擬消費時間
    }
}

int main() {
    std::thread prod(producer);
    std::thread cons(consumer);

    prod.join();
    cons.join();
    return 0;
}
