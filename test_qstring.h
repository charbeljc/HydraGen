#include <QtCore/QString>

namespace bindtest {
class TestQString {
    public:
        QString hello_message_from_qt();
        std::string hello_message_from_std();

        void say_hello_with_qt(QString greetings);
        void say_hello_with_std(std::string greetings);
};
};
