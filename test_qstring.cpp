#include "test_qstring.h"

#include <QDebug>
#include <QString>
#include <iostream>
#include <string>
BEGIN_NAMESPACE
NAMED_INIT(O, "O");
NAMED_INIT(A, "A");
SINGLETON_INIT(A);
A::A() { std::cerr << "ctor<A>\n"; }
A::~A() { std::cerr << "dtor<A>\n"; }

QString A::hello_message_from_qt() { return QString("Hello from qt"); }
std::string A::hello_message_from_std() {
  return std::string("Hello from std");
}
void A::say_hello_with_qt(QString greetings) { qDebug() << greetings; }
void A::say_hello_with_std(std::string greetings) { std::cerr << greetings; }

NAMED_INIT(B, "B");
SINGLETON_INIT(B);
B::B() { std::cerr << "ctor<B>\n"; }
B::~B() { 
  std::cerr << "~B(): " << _my_a << " count: " << (_my_a ? _my_a.use_count() : -1) << "\n";
  // auto tmp = _my_a;
  // _my_a = nullptr;
  std::cerr << "dtor<B>\n";
  // std::cerr << "~B(): " << tmp << " count: " << (tmp ? tmp.use_count() : -1) << "\n";
}
QString B::hello_message_from_qt() {
  return _my_a ? _my_a->hello_message_from_qt() : nullptr;
}
std::string B::hello_message_from_std() {
  return _my_a ? _my_a->hello_message_from_std() : nullptr;
}
void B::say_hello_with_qt(QString greetings) {
  std::cerr << "hello-qt(): " << _my_a << " count: " << (_my_a ? _my_a.use_count() : -1) << "\n";
  if (_my_a) _my_a->say_hello_with_qt( greetings );
}
void B::say_hello_with_std(std::string greetings) {
  std::cerr << "hello-std(): " << _my_a << " count: " << (_my_a ? _my_a.use_count() : -1) << "\n";
  if (_my_a) _my_a->say_hello_with_std( greetings );
}

std::shared_ptr<A> B::get_a() { return _my_a; }
void B::set_a(std::shared_ptr<A> a) { _my_a = a; }
END_NAMESPACE
