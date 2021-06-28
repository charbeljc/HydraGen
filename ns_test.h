// #include <string>
namespace A {
  int foo(int bar);
  int foo(float zorgl);
  class A {
   public:
    int foo(int bar);
    class AA { int foobar(); };
  };
  class AB {
    int barfoo();
  };
  float bar(int a, int b);
};

namespace B {
  double foo();
  float bar(int a, int b, int c);
};

namespace A {
  const char* foo(int a, int b);
}