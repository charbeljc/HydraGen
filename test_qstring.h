#pragma once
#ifdef BINDER
#define QT_NAMESPACE Qt5
#endif
#include <QtCore/QString>
#include <memory>
#include <string>

#ifdef USE_NAMESPACE
#define BEGIN_NAMESPACE namespace test {
#define END_NAMESPACE } // namespace test
#else
#define BEGIN_NAMESPACE
#define END_NAMESPACE
#endif
#include <singleton.h>
#include <named.h>
BEGIN_NAMESPACE
class O: public Named<O> {};

class A: public Named<A>, public O {
 public:
  A();
  virtual ~A();
  QString hello_message_from_qt();
  std::string hello_message_from_std();

  void say_hello_with_qt(const QString greetings);
  void say_hello_with_std(const std::string greetings);
};

class B: public Named<A>, public O {
 public:
  B();
  virtual ~B();
  explicit B(std::shared_ptr<A> a) : _my_a(a) {}

 private:
  std::shared_ptr<A> _my_a;

 public:
  QString hello_message_from_qt();
  std::string hello_message_from_std();

  void say_hello_with_qt(const QString greetings);
  void say_hello_with_std(const std::string greetings);

  std::shared_ptr<A> get_a();
  void set_a(std::shared_ptr<A> a);
};

class SA: public A, public Singleton<A> {};
class SB: public B, public Singleton<B> {};

END_NAMESPACE
