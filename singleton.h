// Copyright 2021 Charbel Jacquin
#pragma once
#include <memory>
#include <exception>
#include <iostream>
using namespace std;
template<typename T> class SingletonException: public exception { };
template<typename T> class Singleton {
 public:
    Singleton() {
      if (__instance) throw SingletonException<T>();
    }
    ~Singleton() {
    }
    static void ensure() {
      if (!__instance) {
        __instance = make_shared<T>();
      }
    }
    static void shutdown() {
      if (__instance) {
        std::cerr << "shutdown:" << __instance.use_count() << "\n";
        __instance.reset();
      }
      __instance = nullptr;
    }
    static shared_ptr<T> instance(bool create=false, bool nullok=false) {
        if (create) ensure();
        if (!nullok && !__instance) throw SingletonException<T>();
        return __instance;
    }

 private:
    static shared_ptr<T> __instance;
};
#define SINGLETON_INIT(T)   template<> std::shared_ptr<T> Singleton<T>::__instance = nullptr