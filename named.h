#pragma once
template<typename T> class Named {
 public:
    const char *class_name() const { return __class_name; }
    Named() = default;
    ~Named() = default;
 private:
    static const char *__class_name;
};
#define NAMED_INIT(T, class_name) template<> const char * Named<T>::__class_name = class_name