// #include <string>
int foo();
int bar();
struct foobar {
  int a;
  int b;
};
namespace A {
  int foo(int bar);
  int foo(float zorgl);
  class A {
   public:
    A(int foo);
    A();
    ~A();
    int foo(int bar);
    class AA { int foobar(); };
  };
  class AB {
    int barfoo();
    void set_a(A *a = nullptr);
  };
  float bar(int a, int b);
};

namespace B {
  double foo();
  float bar(int a = 1 + 2, int b = 2, int c = 3 + 4);
};

namespace A {
  const char* foo(int a, int b);
};


namespace B {
  bool zorgl();
};